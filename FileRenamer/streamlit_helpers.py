import os
import shutil
import streamlit as st
import tempfile
from typing import List, Dict, Any, Optional

from core.ai_pipeline import run_ai_naming, read_multiprocessed, step_sanitize_names
from core.utils import zip_files
from core.gpt_agent import GPTAgent

TEXT_EXTS = {".txt", ".docx", ".pdf", ".csv", ".xlsx", ".json"}


# ------------------------------------------------------------
#   Upload de fichiers
# ------------------------------------------------------------
def upload_files(allowed_exts: List[str], TEMP_DIR: str = "uploaded_temp") -> List[Dict[str, str]]:
    """
    Gère l’upload des fichiers via Streamlit, les enregistre localement,
    et met à jour la session Streamlit avec les fichiers uploadés.

    Args:
        allowed_exts: Liste d’extensions autorisées (ex: [".txt", ".pdf"]).
        TEMP_DIR: Dossier temporaire où stocker les fichiers uploadés.

    Returns:
        Liste de dictionnaires contenant :
            - name : nom du fichier sans extension
            - ext : extension du fichier
            - path : chemin absolu du fichier enregistré
    """
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

        if save_path not in [file["path"] for file in st.session_state["uploaded_files"]]:
            st.session_state["uploaded_files"].append({
                "name": os.path.splitext(f.name)[0],
                "ext": os.path.splitext(f.name)[1],
                "path": save_path
            })

    return st.session_state["uploaded_files"]


# ------------------------------------------------------------
#   Nettoyage du dossier et de la session
# ------------------------------------------------------------
def clear_and_clean(TEMP_DIR: str = "uploaded_temp") -> None:
    """
    Supprime le dossier temporaire et réinitialise la session Streamlit.
    Fonction robuste multiplateforme (ignore si le dossier n'existe pas).
    """
    try:
        if os.path.exists(TEMP_DIR):
            shutil.rmtree(TEMP_DIR, ignore_errors=True)
        os.makedirs(TEMP_DIR, exist_ok=True)
    except Exception as e:
        st.warning(f"⚠️ Impossible de nettoyer le dossier temporaire : {e}")

    st.session_state["uploaded_files"] = []
    st.session_state["last_results_df"] = None



def clear_and_clean_button(TEMP_DIR: str = "uploaded_temp") -> None:
    """
    Affiche un bouton Streamlit permettant de réinitialiser
    le dossier temporaire et la session.
    """
    if st.button("🧹 Clear & Clean"):
        clear_and_clean(TEMP_DIR)
        st.success("Dossier et session nettoyés ✅")


# ------------------------------------------------------------
#   Conversion des résultats en DataFrame
# ------------------------------------------------------------
def items_to_dataframe(items: List[Dict[str, Any]]):
    """
    Convertit une liste d’items en DataFrame pour affichage dans Streamlit.

    Args:
        items: Liste de dictionnaires contenant au minimum :
            - name
            - clean_description (optionnel)
            - generated_filename (optionnel)
            - path

    Returns:
        pandas.DataFrame : Tableau prêt pour affichage.
    """
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


# ------------------------------------------------------------
#  Téléchargement ZIP des fichiers renommés
# ------------------------------------------------------------
def download_zip_button(items: List[Dict[str, Any]], zip_name: str = "renamed_files.zip") -> None:
    """
    Crée un bouton Streamlit pour télécharger les fichiers renommés sous forme d’archive ZIP.

    Args:
        items: Liste d’items contenant :
            - "path" : chemin original du fichier
            - "generated_filename" : nom final souhaité
        zip_name: Nom du fichier ZIP généré.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        renamed_paths = []

        for item in items:
            orig_path = item["path"]
            new_name = item.get("generated_filename", os.path.splitext(os.path.basename(orig_path))[0])
            dest_path = os.path.join(tmpdir, new_name)
            shutil.copy2(orig_path, dest_path)
            renamed_paths.append(dest_path)

        zip_path = os.path.join(tmpdir, zip_name)
        zip_files(renamed_paths, zip_path)

        with open(zip_path, "rb") as f:
            st.download_button(
                label="📦 Télécharger tous les fichiers renommés",
                data=f,
                file_name=zip_name,
                mime="application/zip"
            )


# ------------------------------------------------------------
#  Pipeline AI avec barre de progression
# ------------------------------------------------------------
def run_ai_naming_with_progress(files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Exécute le pipeline AI sur plusieurs fichiers avec une barre de progression Streamlit.

    Args:
        files: Liste de fichiers à analyser (nom, extension, chemin).

    Returns:
        Liste de dictionnaires contenant les résultats enrichis :
            - name
            - clean_description
            - generated_filename
            - path
    """
    results: List[Dict[str, Any]] = []
    total_files = len(files)

    progress_text = st.empty()
    progress_bar = st.progress(0)
    processed = read_multiprocessed(files)
    gpt = GPTAgent()

    for i, f in enumerate(processed, start=1):
        progress_text.text(f"Fichier {i} / {total_files} : {f['name']}{f['ext']}")
        partial_result = run_ai_naming([f], gpt)
        results.extend(partial_result)
        progress_bar.progress(i / total_files)

    progress_text.empty()
    progress_bar.empty()
    results = step_sanitize_names(results)

    st.success("✅ Analyse terminée !")
    return results
