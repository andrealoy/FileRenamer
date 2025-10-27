import streamlit as st
import pandas as pd
import os
import json
import csv
import ollama
import zipfile
import io
import uuid
import re

# ============================================================
#                      UTILITIES
# ============================================================

TEMP_DIR = "uploaded_temp"
os.makedirs(TEMP_DIR, exist_ok=True)

def sanitize_filename(name: str) -> str:
    name = name.strip().lower()
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^a-z0-9_\-\.]", "_", name)
    name = re.sub(r"_+", "_", name)
    return name

def ensure_extension(base: str, ext: str) -> str:
    if not ext.startswith("."):
        ext = "." + ext
    if "." not in os.path.basename(base):
        return base + ext
    return base

def read_text_file(path):
    _, ext = os.path.splitext(path)
    ext = ext.lower()
    try:
        if ext == ".txt":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
        elif ext == ".json":
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                data = json.load(f)
            return json.dumps(data, indent=2)
        elif ext == ".csv":
            lines = []
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                reader = csv.reader(f)
                for i, row in enumerate(reader):
                    lines.append(", ".join(row))
                    if i >= 4:
                        break
            return "\n".join(lines)
        elif ext == ".pdf":
            import PyPDF2
            text = ""
            with open(path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                for page in reader.pages:
                    text += page.extract_text() or ""
            return text
        elif ext == ".docx":
            import docx
            doc = docx.Document(path)
            return "\n".join(p.text for p in doc.paragraphs)
        else:
            with open(path, "r", encoding="utf-8", errors="ignore") as f:
                return f.read()
    except Exception:
        return ""

# ============================================================
#                      GEMMA FUNCTIONS
# ============================================================

def describe_text_with_gemma(text_paths):
    results = []
    for path in text_paths:
        name = os.path.basename(path)
        ext = os.path.splitext(path)[1]
        try:
            content = read_text_file(path)[:2000]
            response = ollama.chat(
                model="gemma3:12b",
                messages=[{
                    "role": "user",
                    "content": "Summarize this text in 1-2 concise English sentences:\n\n" + content
                }]
            )
            description = response["message"]["content"].strip()
        except Exception as e:
            description = f"Error: {e}"
        results.append({"name": name, "path": path, "description": description, "ext": ext})
    return results

def describe_images_with_gemma(image_paths):
    results = []
    for path in image_paths:
        name = os.path.basename(path)
        ext = os.path.splitext(path)[1]
        try:
            response = ollama.chat(
                model="gemma3:12b",
                messages=[{
                    "role": "user",
                    "content": "Describe this image in 1-2 short natural English sentences.",
                    "images": [path]
                }]
            )
            description = response["message"]["content"].strip()
        except Exception as e:
            description = f"Error: {e}"
        results.append({"name": name, "path": path, "description": description, "ext": ext})
    return results

def clean_descriptions_with_gemma(results):
    cleaned = []
    for item in results:
        try:
            response = ollama.chat(
                model="gemma3:12b",
                messages=[{
                    "role": "user",
                    "content": (
                        "Clean this short description by removing phrases like "
                        "'this image', 'this document', etc. Keep only the factual description:\n\n"
                        + item["description"]
                    )
                }]
            )
            item["clean_description"] = response["message"]["content"].strip()
        except Exception as e:
            item["clean_description"] = f"Error cleaning: {e}"
        cleaned.append(item)
    return cleaned

def generate_filenames_with_gemma(results):
    renamed = []
    for item in results:
        try:
            original_name = os.path.splitext(item["name"])[0]

            response = ollama.chat(
                model="gemma3:12b",
                messages=[{
                    "role": "user",
                    "content": (
                        "You will receive a short description and the original file name.\n"
                        "Generate a short descriptive filename (max 6 words) based on both.\n"
                        "Use clues from the original file name if they are meaningful (dates, subjects, etc.).\n"
                        "Keep it natural, relevant, and readable.\n\n"
                        "Rules:\n"
                        "- Use only lowercase letters, numbers, and underscores.\n"
                        "- Do NOT include the file extension.\n"
                        "- Return only the filename text.\n\n"
                        f"Original filename: {original_name}\n\n"
                        f"Description:\n{item.get('clean_description', item.get('description', ''))}"
                    )
                }]
            )
            item["generated_filename"] = response["message"]["content"].strip()
        except Exception as e:
            item["generated_filename"] = f"Error generating filename: {e}"
        renamed.append(item)
    return renamed


# ============================================================
#                      STREAMLIT APP
# ============================================================

st.title("📁 AI File Name Generator + ZIP Export")

if "df" not in st.session_state:
    st.session_state.df = None
if "renamed_files" not in st.session_state:
    st.session_state.renamed_files = {}

uploaded_files = st.file_uploader("📤 Upload your files", accept_multiple_files=True)

# ---------- SAVE FILES LOCALLY ----------
if uploaded_files:
    file_paths = []
    for f in uploaded_files:
        save_path = os.path.join(TEMP_DIR, f.name)
        with open(save_path, "wb") as out:
            out.write(f.read())
        file_paths.append(save_path)

    text_ext = {'.txt', '.pdf', '.odt', '.doc', '.docx', '.csv', '.json'}
    image_ext = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic'}

    text_files = [p for p in file_paths if os.path.splitext(p)[1].lower() in text_ext]
    image_files = [p for p in file_paths if os.path.splitext(p)[1].lower() in image_ext]

    st.success(f"✅ {len(text_files)} text and {len(image_files)} image files uploaded.")

    if st.button("🧠 Generate Descriptions & Filenames"):
        with st.spinner("Analyzing with Gemma..."):
            results = []
            if text_files:
                results += generate_filenames_with_gemma(
                    clean_descriptions_with_gemma(describe_text_with_gemma(text_files))
                )
            if image_files:
                results += generate_filenames_with_gemma(
                    clean_descriptions_with_gemma(describe_images_with_gemma(image_files))
                )

            df = pd.DataFrame([
                {
                    "Original File Name": r["name"],
                    "Description": r.get("clean_description", ""),
                    "Generated File Name": sanitize_filename(r.get("generated_filename", "")) + r["ext"],
                    "Path": r["path"]
                }
                for r in results
            ])
            st.session_state.df = df
            st.success("✅ AI naming complete!")

# ---------- DISPLAY TABLE ----------
if st.session_state.df is not None:
    st.subheader("📝 Review & Edit Filenames")
    edited = st.data_editor(st.session_state.df, use_container_width=True)
    st.session_state.df = edited

    # ---------- ZIP DOWNLOAD ----------
    if st.button("📦 Create ZIP with Renamed Files"):
        renamed_files = []
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for _, row in st.session_state.df.iterrows():
                old_path = row["Path"]
                new_name = row["Generated File Name"]
                new_path = os.path.join(TEMP_DIR, new_name)

                with open(old_path, "rb") as src:
                    zipf.writestr(new_name, src.read())
                renamed_files.append(new_name)

        zip_buffer.seek(0)
        st.download_button(
            "⬇️ Download Renamed Files (.zip)",
            zip_buffer,
            file_name="renamed_files.zip",
            mime="application/zip"
        )
        st.success(f"✅ Created ZIP with {len(renamed_files)} files.")











# import streamlit as st
# import pandas as pd
# import os
# import json
# import csv
# import ollama

# # ---------- HELPERS ----------

# def classify_text_files(file_paths):
#     text_extensions = {'.txt', '.pdf', '.odt', '.doc', '.docx', '.csv', '.json'}
#     classified = {"text_documents": [], "others": []}

#     print("🗂️ Classifying text files...")
#     for path in file_paths:
#         _, ext = os.path.splitext(path)
#         ext = ext.lower()
#         if ext in text_extensions:
#             classified["text_documents"].append(path)
#         else:
#             classified["others"].append(path)
#     print(f"📄 Found {len(classified['text_documents'])} text documents.")
#     return classified


# def classify_image_files(file_paths):
#     image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.tif', '.webp', '.heic'}
#     classified = {"images": [], "others": []}

#     print("🖼️ Classifying image files...")
#     for path in file_paths:
#         _, ext = os.path.splitext(path)
#         ext = ext.lower()
#         if ext in image_extensions:
#             classified["images"].append(path)
#         else:
#             classified["others"].append(path)
#     print(f"🖼️ Found {len(classified['images'])} image files.")
#     return classified


# # ---------- DECODERS ----------
# def decode_txt(path):
#     with open(path, "r", encoding="utf-8", errors="ignore") as f:
#         return f.read()

# def decode_json(path):
#     try:
#         with open(path, "r", encoding="utf-8", errors="ignore") as f:
#             data = json.load(f)
#         return json.dumps(data, indent=2)
#     except Exception as e:
#         return f"Error reading JSON: {e}"

# def decode_pdf(path):
#     try:
#         import PyPDF2
#         text = ""
#         with open(path, "rb") as f:
#             reader = PyPDF2.PdfReader(f)
#             for page in reader.pages:
#                 text += page.extract_text() or ""
#         return text
#     except Exception as e:
#         return f"Error reading PDF: {e}"

# def decode_docx(path):
#     try:
#         import docx
#         doc = docx.Document(path)
#         return "\n".join(p.text for p in doc.paragraphs)
#     except Exception as e:
#         return f"Error reading DOCX: {e}"

# def decode_csv(path, max_lines=5):
#     try:
#         lines = []
#         with open(path, "r", encoding="utf-8", errors="ignore") as f:
#             reader = csv.reader(f)
#             for i, row in enumerate(reader):
#                 lines.append(", ".join(row))
#                 if i >= max_lines - 1:
#                     break
#         return "\n".join(lines)
#     except Exception as e:
#         return f"Error reading CSV: {e}"

# def decode_odt(path):
#     try:
#         from odf.opendocument import load
#         from odf.text import P
#         doc = load(path)
#         paragraphs = [p.firstChild.data for p in doc.getElementsByType(P) if p.firstChild]
#         return "\n".join(paragraphs)
#     except Exception as e:
#         return f"Error reading ODT: {e}"

# def read_text_file(path):
#     _, ext = os.path.splitext(path)
#     ext = ext.lower()

#     if ext == ".txt":
#         return decode_txt(path)
#     elif ext == ".pdf":
#         return decode_pdf(path)
#     elif ext == ".docx":
#         return decode_docx(path)
#     elif ext == ".json":
#         return decode_json(path)
#     elif ext == ".csv":
#         return decode_csv(path)
#     elif ext == ".odt":
#         return decode_odt(path)
#     else:
#         try:
#             return decode_txt(path)
#         except Exception as e: 
#             return ""


# # ---------- GEMMA FUNCTIONS ----------

# def describe_images_with_gemma(image_dict):
#     results = []
#     print("\n🤖 Describing images with Gemma...\n")
#     for i, (name, path, ext) in enumerate(zip(image_dict["names"], image_dict["paths"], image_dict["exts"]), 1):
#         print(f"🖼️ [{i}/{len(image_dict['paths'])}] {name} ...", end=" ")
#         try:
#             response = ollama.chat(
#                 model="gemma3:12b",
#                 messages=[{
#                     "role": "user",
#                     "content": (
#                         "Describe this image in one or two short natural English sentences. "
#                         "Focus on the context and environment rather than only the subject."
#                     ),
#                     "images": [path]
#                 }]
#             )
#             description = response["message"]["content"].strip()
#             print("✅")
#         except Exception as e:
#             description = f"Error: {e}"
#             print("❌")
#         results.append({"name": name, "path": path, "description": description, "ext": ext})
#     print("\n✅ Image descriptions complete!\n")
#     return results


# def describe_text_with_gemma(text_dict):
#     results = []
#     print("\n🤖 Summarizing text files with Gemma...\n")
#     for i, (name, path, ext) in enumerate(zip(text_dict["names"], text_dict["paths"], text_dict["exts"]), 1):
#         print(f"📄 [{i}/{len(text_dict['paths'])}] {name} ...", end=" ")
#         try:
#             content = read_text_file(path)[:2000]
#             response = ollama.chat(
#                 model="gemma3:12b",
#                 messages=[{
#                     "role": "user",
#                     "content": (
#                         "Summarize the following text in one or two concise English sentences. "
#                         "Focus on the main idea and tone of the document:\n\n" 
#                         + content
#                     )
#                 }]
#             )
#             description = response["message"]["content"].strip()
#             print("✅")
#         except Exception as e:
#             description = f"Error: {e}"
#             print("❌")
#         results.append({"name": name, "path": path, "description": description, "ext": ext})
#     print("\n✅ Text descriptions complete!\n")
#     return results


# def clean_descriptions_with_gemma(results, mode="image"):
#     print(f"\n🧹 Cleaning {mode} descriptions with Gemma...\n")
#     cleaned = []

#     for i, item in enumerate(results, 1):
#         print(f"🧾 [{i}/{len(results)}] Cleaning → {item['name']} ...", end=" ")
#         try:
#             prompt = (
#                 "You will receive a short description. "
#                 "Return only the clean, natural English description of the content itself — "
#                 "remove any mention of 'this image', 'this photo', 'this document', "
#                 "'the following text', or similar phrases. "
#                 "Keep only the concise factual description."
#             )
#             response = ollama.chat(
#                 model="gemma3:12b",
#                 messages=[
#                     {"role": "user", "content": prompt + "\n\nDescription:\n" + item["description"]}
#                 ]
#             )
#             clean_desc = response["message"]["content"].strip()
#             item["clean_description"] = clean_desc
#             cleaned.append(item)
#             print("✅")
#         except Exception as e:
#             print("❌")
#             item["clean_description"] = f"Error cleaning: {e}"
#             cleaned.append(item)

#     print(f"\n✨ Cleaned {len(cleaned)} {mode} descriptions successfully!\n")
#     return cleaned


# def generate_filenames_with_gemma(results, mode="image"):
#     print(f"\n🏷️ Generating filenames for {mode} descriptions with Gemma...\n")
#     renamed = []

#     for i, item in enumerate(results, 1):
#         print(f"💡 [{i}/{len(results)}] Generating name for → {item['name']} ...", end=" ")
#         try:
#             prompt = (
#                 "Generate a short, descriptive filename (no longer than 6 words) based on the description below. "
#                 "Use only lowercase letters, numbers, and underscores. "
#                 "Do NOT include file extensions or any extra commentary. "
#                 "Return ONLY the filename text.\n\n"
#                 f"Description:\n{item.get('clean_description', item.get('description', ''))}"
#             )

#             response = ollama.chat(
#                 model="gemma3:12b",
#                 messages=[{"role": "user", "content": prompt}]
#             )

#             filename = response["message"]["content"].strip()
#             item["generated_filename"] = filename
#             renamed.append(item)
#             print("✅")
#         except Exception as e:
#             print("❌")
#             item["generated_filename"] = f"Error generating filename: {e}"
#             renamed.append(item)

#     print(f"\n✅ Filenames generated for {len(renamed)} {mode} files!\n")
#     return renamed


# # ---------- STREAMLIT APP ----------

# st.title("📁 AI File Name Generator")

# uploaded_files = st.file_uploader("Upload your files", accept_multiple_files=True)

# if uploaded_files:
#     # Save uploaded files to temp directory
#     temp_dir = "uploaded_files"
#     os.makedirs(temp_dir, exist_ok=True)
#     file_paths = []

#     for f in uploaded_files:
#         temp_path = os.path.join(temp_dir, f.name)
#         with open(temp_path, "wb") as f_out:
#             f_out.write(f.read())
#         file_paths.append(temp_path)

#     df = pd.DataFrame({
#         "Original File Name": [os.path.basename(p) for p in file_paths],
#         "Description": ["" for _ in file_paths],
#         "Generated File Name": ["" for _ in file_paths]
#     })

#     st.dataframe(df, use_container_width=True)

#     # ---------- Bouton AI ----------
#     if st.button("🧠 AI file names"):
#         with st.spinner("Analyzing files with Gemma..."):
#             text_class = classify_text_files(file_paths)
#             image_class = classify_image_files(file_paths)

#             text_paths = text_class["text_documents"]
#             image_paths = image_class["images"]

#             # Préparer dictionnaires
#             text_dict = {
#                 "names": [os.path.basename(p) for p in text_paths],
#                 "paths": text_paths,
#                 "exts": [os.path.splitext(p)[1] for p in text_paths]
#             }
#             image_dict = {
#                 "names": [os.path.basename(p) for p in image_paths],
#                 "paths": image_paths,
#                 "exts": [os.path.splitext(p)[1] for p in image_paths]
#             }

#             # 1️⃣ Description
#             text_results = describe_text_with_gemma(text_dict) if text_paths else []
#             image_results = describe_images_with_gemma(image_dict) if image_paths else []

#             # 2️⃣ Nettoyage
#             clean_texts = clean_descriptions_with_gemma(text_results, mode="text") if text_results else []
#             clean_images = clean_descriptions_with_gemma(image_results, mode="image") if image_results else []

#             # 3️⃣ Génération de noms
#             final_texts = generate_filenames_with_gemma(clean_texts, mode="text") if clean_texts else []
#             final_images = generate_filenames_with_gemma(clean_images, mode="image") if clean_images else []

#             # 4️⃣ Mettre à jour le DataFrame
#             all_results = final_texts + final_images
#             for item in all_results:
#                 df.loc[df["Original File Name"] == item["name"], "Description"] = item["clean_description"]
#                 df.loc[df["Original File Name"] == item["name"], "Generated File Name"] = item["generated_filename"] + item["ext"]

#             st.success("✅ File analysis complete!")
#             st.dataframe(df, use_container_width=True)

#             # 5️⃣ Affichage final
#             st.subheader("📄 Text Documents — Generated Names")
#             if final_texts:
#                 for item in final_texts:
#                     st.markdown(f"**{item['name']} → `{item['generated_filename']}{item['ext']}`**")
#                     st.caption(item['clean_description'])

#             st.subheader("🖼️ Image Files — Generated Names")
#             if final_images:
#                 for item in final_images:
#                     st.image(item["path"], caption=f"{item['generated_filename']}{item['ext']}", use_column_width=True)
#                     st.caption(item['clean_description'])

# else:
#     st.info("Please upload one or more files to begin.")
