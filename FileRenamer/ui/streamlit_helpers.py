# streamlit_helpers.py — version texte uniquement
import os
import shutil
import streamlit as st

TEXT_EXTS = {".txt", ".docx", ".pdf", ".csv", ".xlsx", ".json"}


def upload_files(allowed_exts, TEMP_DIR: str = "uploaded_temp"):
    """
    Ouvre un file_uploader Streamlit, sauvegarde les fichiers dans TEMP_DIR,
    et renvoie une liste de dictionnaires :
    [
        {"name": "document", "ext": ".txt", "path": "uploaded_temp/document.txt"},
        ...
    ]
    """
    os.makedirs(TEMP_DIR, exist_ok=True)

    # Normalisation des extensions acceptées
    allowed_types = [ext.lstrip(".").lower() for ext in allowed_exts]
    allowed_exts_norm = {e.lower() for e in allowed_exts}

    uploaded = st.file_uploader(
        "📂 Dépose tes fichiers texte ici",
        type=allowed_types,
        accept_multiple_files=True
    )

    text_files = []

    for f in uploaded or []:
        base, ext = os.path.splitext(f.name)
        ext = ext.lower()
        if ext not in allowed_exts_norm:
            continue

        save_path = os.path.abspath(os.path.join(TEMP_DIR, f.name))
        with open(save_path, "wb") as out:
            out.write(f.read())

        text_files.append({"name": base, "ext": ext, "path": save_path})

    return text_files


def clear_temp_dir(TEMP_DIR: str = "uploaded_temp") -> None:
    """
    Supprime et recrée le dossier temporaire utilisé pour les uploads.
    """
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
