import streamlit as st
import pandas as pd
import os
import io
import zipfile
import json
import csv
import ollama
import re
from sklearn.cluster import KMeans
from sentence_transformers import SentenceTransformer
from collections import Counter
import shutil

# ============================================================
# CONFIGURATION
# ============================================================
TEMP_DIR = "uploaded_temp"
CLASSIFIED_DIR = "classified_files"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(CLASSIFIED_DIR, exist_ok=True)

# ============================================================
# HELPERS
# ============================================================
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
# GEMMA INTERACTIONS
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
                    "content": f"Summarize this text file '{name}' in 1–2 concise English sentences:\n\n{content}"
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
                    "content": f"Describe this image file '{name}' in 1–2 short natural English sentences.",
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
                        "You will receive the original file name and a short description.\n"
                        "Generate a short descriptive filename (max 6 words) using both.\n"
                        "Use lowercase, underscores, and no file extension.\n\n"
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
# CLUSTERING (CATEGORIES)
# ============================================================

def cluster_files_and_label(df, n_clusters=8):
    model = SentenceTransformer("all-MiniLM-L6-v2")
    texts = df["Generated File Name"].tolist()
    embeddings = model.encode(texts)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    labels = kmeans.fit_predict(embeddings)
    df["Category"] = labels

    # Regrouper les fichiers par cluster
    clusters = {i: df[df["Category"] == i]["Generated File Name"].tolist() for i in range(n_clusters)}

    # Nommer chaque cluster via Gemma (local)
    cluster_names = {}
    for cid, names in clusters.items():
        try:
            joined = "\n".join(names[:10])
            response = ollama.chat(
                model="gemma3:12b",
                messages=[{
                    "role": "user",
                    "content": (
                        "Here are several filenames that belong to the same group:\n\n"
                        f"{joined}\n\n"
                        "Suggest a short and natural English label (1–3 words, lowercase, underscores only) "
                        "that describes their common theme or topic."
                    )
                }]
            )
            label = sanitize_filename(response["message"]["content"].strip())
        except Exception as e:
            label = f"cluster_{cid}"
        cluster_names[cid] = label
        df.loc[df["Category"] == cid, "Category Name"] = label

    return df, cluster_names

# ============================================================
# STREAMLIT APP
# ============================================================

st.title("📁 AI File Organizer with Gemma + Clustering")

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

    if st.button("🧠 Generate AI Filenames + Clustering"):
        with st.spinner("Analyzing files with Gemma..."):
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

            st.success("✅ AI naming complete! Now clustering files...")

            df, cluster_names = cluster_files_and_label(df, n_clusters=8)
            st.session_state.df = df
            st.session_state.cluster_names = cluster_names

# ============================================================
# DISPLAY RESULTS
# ============================================================

if st.session_state.df is not None:
    st.subheader("📊 File Overview + Clusters")
    st.dataframe(st.session_state.df, use_container_width=True)

    if st.button("📦 Download ZIP by Category"):
        df = st.session_state.df
        cluster_names = st.session_state.cluster_names

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
            for _, row in df.iterrows():
                old_path = row["Path"]
                category = row["Category Name"]
                new_name = row["Generated File Name"]

                arcname = os.path.join(category, new_name)
                with open(old_path, "rb") as src:
                    zipf.writestr(arcname, src.read())

        zip_buffer.seek(0)
        st.download_button(
            "⬇️ Download Categorized ZIP",
            zip_buffer,
            file_name="organized_files.zip",
            mime="application/zip"
        )
        st.success("✅ Files clustered and archived successfully!")
