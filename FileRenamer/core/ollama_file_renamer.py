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
from openai import OpenAI

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
#                      MODEL HANDLER
# ============================================================

def query_model(prompt, images=None, model_choice="Ollama"):
    """
    Envoie la requête soit vers Ollama, soit vers OpenAI (ChatGPT)
    selon le choix de l'utilisateur.
    """
    if model_choice == "Ollama":
        try:
            response = ollama.chat(
                model="gemma3:12b",
                messages=[{"role": "user", "content": prompt, "images": images or []}]
            )
            return response["message"]["content"].strip()
        except Exception as e:
            return f"Error (Ollama): {e}"

    elif model_choice == "GPT":
        try:
            client = OpenAI()
            messages = [{"role": "user", "content": prompt}]
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.3,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"Error (GPT): {e}"

# ============================================================
#                      GEMMA / GPT FUNCTIONS
# ============================================================

def describe_text_files(text_paths, model_choice):
    results = []
    for path in text_paths:
        name = os.path.basename(path)
        ext = os.path.splitext(path)[1]
        try:
            content = read_text_file(path)[:2000]
            description = query_model(
                f"Summarize this text in 1-2 concise English sentences:\n\n{content}",
                model_choice=model_choice
            )
        except Exception as e:
            description = f"Error: {e}"
        results.append({"name": name, "path": path, "description": description, "ext": ext})
    return results

def describe_image_files(image_paths, model_choice):
    results = []
    for path in image_paths:
        name = os.path.basename(path)
        ext = os.path.splitext(path)[1]
        description = query_model(
            "Describe this image in 1-2 short natural English sentences.",
            images=[path],
            model_choice=model_choice
        )
        results.append({"name": name, "path": path, "description": description, "ext": ext})
    return results

def clean_descriptions(results, model_choice):
    cleaned = []
    for item in results:
        cleaned_desc = query_model(
            "Clean this short description by removing phrases like "
            "'this image', 'this document', etc. Keep only the factual description , no comments:\n\n"
            + item["description"],
            model_choice=model_choice
        )
        item["clean_description"] = cleaned_desc
        cleaned.append(item)
    return cleaned

def generate_filenames(results, model_choice):
    renamed = []
    for item in results:
        original_name = os.path.splitext(item["name"])[0]
        prompt = (
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
        new_name = query_model(prompt, model_choice=model_choice)
        item["generated_filename"] = new_name
        renamed.append(item)
    return renamed

# ============================================================
#                      STREAMLIT APP
# ============================================================

st.title("📁 AI File Name Generator + ZIP Export")

# Sélection du modèle
model_choice = st.radio(
    "🤖 Choose AI model to use:",
    ("Ollama (local)", "GPT (online)"),
    horizontal=True
)
model_choice = "GPT" if "GPT" in model_choice else "Ollama"

if "df" not in st.session_state:
    st.session_state.df = None

uploaded_files = st.file_uploader("📤 Upload your files", accept_multiple_files=True)

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
        with st.spinner(f"Analyzing with {model_choice}..."):
            results = []
            if text_files:
                results += generate_filenames(
                    clean_descriptions(describe_text_files(text_files, model_choice), model_choice),
                    model_choice
                )
            if image_files:
                results += generate_filenames(
                    clean_descriptions(describe_image_files(image_files, model_choice), model_choice),
                    model_choice
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
