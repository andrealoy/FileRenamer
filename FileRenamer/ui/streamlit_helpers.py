import os
import shutil
import streamlit as st
from core.ai_pipeline import (step_format_for_ui,
    run_ai_naming
)
from core.utils import zip_files 

TEXT_EXTS = {".txt", ".docx", ".pdf", ".csv", ".xlsx", ".json"}

# -----------------------------
# Upload de fichiers
# -----------------------------
def upload_files(allowed_exts, TEMP_DIR="uploaded_temp"):
    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = []

    os.makedirs(TEMP_DIR, exist_ok=True)
    allowed_types = [ext.lstrip(".").lower() for ext in allowed_exts]

    uploaded = st.file_uploader(
        "📂 Dépose tes fichiers texte ici",
        type=allowed_types,
        accept_multiple_files=True,
        key="file_uploader_widget"
    )

    for f in uploaded or []:
        save_path = os.path.abspath(os.path.join(TEMP_DIR, f.name))
        with open(save_path, "wb") as out:
            out.write(f.read())

        if save_path not in [f["path"] for f in st.session_state["uploaded_files"]]:
            st.session_state["uploaded_files"].append({
                "name": os.path.splitext(f.name)[0],
                "ext": os.path.splitext(f.name)[1],
                "path": save_path
            })

    return st.session_state["uploaded_files"]

# -----------------------------
# Clear & Clean
# -----------------------------
def clear_and_clean_button(TEMP_DIR="uploaded_temp"):
    if st.button("🧹 Clear & Clean"):
        # Vider dossier temporaire
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR, exist_ok=True)

        # Vider session_state
        st.session_state["uploaded_files"] = []
        st.session_state["last_results_df"] = None



# -----------------------------
# Convertir items en DataFrame pour Streamlit
# -----------------------------
def items_to_dataframe(items):
    import pandas as pd
    if not items:
        return pd.DataFrame()
    return pd.DataFrame([
        {
            "Nom": it["name"],
            "Description": it.get("clean_description", ""),
            "Nouveau nom": it.get("generated_filename", it["name"]),
            "path": it["path"]
        }
        for it in items
    ])

def download_zip_button(items, zip_name="renamed_files.zip"):
    """
    Crée un bouton Streamlit pour télécharger les fichiers renommés en ZIP.

    Args:
        items (list[dict]): Liste d'items contenant au minimum :
            - "path" : chemin original du fichier
            - "generated_filename" : nom à utiliser dans le ZIP
        zip_name (str): nom du fichier ZIP à générer
    """
    # Créer un dossier temporaire pour copier/renommer les fichiers
    import tempfile
    import shutil

    with tempfile.TemporaryDirectory() as tmpdir:
        renamed_paths = []

        for item in items:
            orig_path = item["path"]
            new_name = item.get("generated_filename", os.path.splitext(os.path.basename(orig_path))[0]) + os.path.splitext(orig_path)[1]
            dest_path = os.path.join(tmpdir, new_name)
            shutil.copy2(orig_path, dest_path)
            renamed_paths.append(dest_path)

        # Chemin du zip final
        zip_path = os.path.join(tmpdir, zip_name)
        zip_files(renamed_paths, zip_path)

        # Streamlit download button
        with open(zip_path, "rb") as f:
            st.download_button(
                label="📦 Télécharger tous les fichiers renommés",
                data=f,
                file_name=zip_name,
                mime="application/zip"
            )

def run_ai_naming_with_progress(files):
    """
    Analyse les fichiers un par un avec affichage d'une barre de progression.
    Retourne une liste de dictionnaires (résultats).
    """
    results = []
    total_files = len(files)

    # Placeholders pour texte et barre
    progress_text = st.empty()
    progress_bar = st.progress(0)

    for i, f in enumerate(files, start=1):
        progress_text.text(f"Fichier {i} / {total_files} : {f['name']}{f['ext']}")
        partial_result = run_ai_naming([f])
        results.extend(partial_result)

        progress_bar.progress(i / total_files)

    # Nettoyer la barre et le texte
    progress_text.empty()
    progress_bar.empty()

    # Message final
    st.success("✅ Analyse terminée !")

    return results