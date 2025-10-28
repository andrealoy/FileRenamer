# app.py — Streamlit UI (interface only)
# -------------------------------------------------------------
# This file exposes ONLY the interface. It:
# - keeps your custom `upload_files(...)` helper
# - shows counts of text/image files uploaded
# - provides a button to trigger AI naming (hook to implement elsewhere)
# - lets the user review/edit filenames in a table
# - creates a ZIP for download
# - includes explicit clean/reset actions via `clear_temp_dir()`
#
# >>> Plug your backend logic into `run_ai_naming(...)` <<<
# It must return a list[dict] with keys: name, ext, path, clean_description, generated_filename
# -------------------------------------------------------------

from __future__ import annotations
import os
import io
import zipfile
import pandas as pd
import streamlit as st

# Your helpers (as requested)
from streamlit_helpers import upload_files, clear_temp_dir

# ============================================================
# CONFIGURATION
# ============================================================
st.set_page_config(page_title="AI File Name Generator", page_icon="📁", layout="wide")

# ============================================================
# SESSION STATE
# ============================================================
if "df" not in st.session_state:
    st.session_state.df = None
if "uploaded_counts" not in st.session_state:
    st.session_state.uploaded_counts = {"text": 0, "image": 0}

# ============================================================
# UI TITLE
# ============================================================
st.title("📁 AI File Name Generator + ZIP Export")

# ============================================================
# UPLOAD SECTION (keeps your helper)
# ============================================================
allowed_exts = [
    ".png", ".jpg", ".jpeg", ".bmp", ".tiff",
    ".txt", ".docx", ".pdf", ".csv", ".xlsx", ".json",
]

# Expecting your helper to SAVE files to a temp dir and return two lists
# (text_files, image_files). Each item ideally is a dict with keys like
# {"name": str, "ext": str, "path": str} — adapt if your helper differs.
text_files, image_files = upload_files(allowed_exts)

# Feedback on upload
st.session_state.uploaded_counts = {"text": len(text_files or []), "image": len(image_files or [])}
st.success(f"✅ {st.session_state.uploaded_counts['text']} text and {st.session_state.uploaded_counts['image']} image files uploaded.")

# ============================================================
# AI NAMING (Hook only — no business logic here)
# ============================================================

def run_ai_naming(text_files, image_files):
    """Hook for your backend. Implement elsewhere if desired.
    Must return a list of dicts with keys:
    - name (original filename w/out ext)
    - ext (including dot, e.g. ".png")
    - path (absolute or temp path to the saved file)
    - clean_description (string)
    - generated_filename (string, WITHOUT extension)
    """
    raise NotImplementedError("Plug your AI pipeline here (describe/clean/generate)")

col_left, col_right = st.columns([1, 1])

with col_left:
    if st.button("🧠 Generate Descriptions & Filenames", type="primary", use_container_width=True):
        try:
            with st.spinner("Analyzing with your AI backend..."):
                results = run_ai_naming(text_files or [], image_files or [])
                # Build dataframe for review UI
                df = pd.DataFrame([
                    {
                        "Original File Name": r.get("name", ""),
                        "Description": r.get("clean_description", ""),
                        "Generated File Name": f"{r.get('generated_filename', '')}{r.get('ext', '')}",
                        "Path": r.get("path", ""),
                    }
                    for r in (results or [])
                ])
                st.session_state.df = df
                st.success("✅ AI naming complete!")
        except NotImplementedError as e:
            st.info("Interface only: backend not connected. Implement `run_ai_naming(...)` to enable this.")
        except Exception as e:
            st.error(f"⚠️ An unexpected error occurred: {e}")

with col_right:
    # Manual reset & cleanup controls are explicit to avoid deleting files before download
    if st.button("🧹 Clean temporary files", use_container_width=True):
        try:
            clear_temp_dir()
            st.session_state.df = None
            st.success("🧼 Temp directory cleaned.")
        except Exception as e:
            st.error(f"Could not clean temp dir: {e}")

# ============================================================
# REVIEW TABLE + ZIP DOWNLOAD
# ============================================================
if st.session_state.df is not None and not st.session_state.df.empty:
    st.subheader("📝 Review & Edit Filenames")
    edited = st.data_editor(
        st.session_state.df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
    )
    st.session_state.df = edited

    st.divider()

    # Create ZIP in-memory from the edited names
    if st.button("📦 Create ZIP with Renamed Files", type="secondary"):
        try:
            renamed_files = []
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
                for _, row in st.session_state.df.iterrows():
                    old_path = row.get("Path", "")
                    new_name = row.get("Generated File Name", "")

                    if not old_path or not os.path.exists(old_path):
                        st.warning(f"Skipping missing file: {old_path}")
                        continue
                    if not new_name:
                        st.warning(f"Skipping unnamed file for path: {old_path}")
                        continue

                    with open(old_path, "rb") as src:
                        zipf.writestr(new_name, src.read())
                    renamed_files.append(new_name)

            zip_buffer.seek(0)
            st.download_button(
                "⬇️ Download Renamed Files (.zip)",
                zip_buffer,
                file_name="renamed_files.zip",
                mime="application/zip",
            )
            st.success(f"✅ Created ZIP with {len(renamed_files)} files.")
        except Exception as e:
            st.error(f"Failed to create ZIP: {e}")

# ============================================================
# OPTIONAL: Reset the app state (also cleans temp dir)
# ============================================================
st.divider()
if st.button("🔄 Reset App (clean & clear)"):
    try:
        clear_temp_dir()
    finally:
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()
