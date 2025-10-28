import os
import shutil
import streamlit as st

TEXT_EXTS = {".txt", ".docx", ".pdf", ".csv", ".xlsx", ".json"}
IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".bmp", ".tiff"}

def upload_files(allowed_exts, TEMP_DIR: str = "uploaded_temp"):
    """
    Ouvre un file_uploader, sauvegarde dans TEMP_DIR et renvoie
    (text_files, image_files) où chaque item est un dict:
    { "name": <nom sans ext>, "ext": ".png", "path": "<chemin absolu>" }
    """
    os.makedirs(TEMP_DIR, exist_ok=True)

    # streamlit attend les extensions sans le point
    allowed_types = [ext.lstrip(".").lower() for ext in allowed_exts]
    uploaded = st.file_uploader(
        "Dépose tes fichiers",
        type=allowed_types,
        accept_multiple_files=True
    )

    text_files, image_files = [], []

    # normalise pour le test d'appartenance
    allowed_exts_norm = {e.lower() for e in allowed_exts}

    for f in (uploaded or []):
        base, ext = os.path.splitext(f.name)
        ext = ext.lower()

        # au cas où, on ne garde que ce qui est autorisé
        if ext not in allowed_exts_norm:
            continue

        save_path = os.path.abspath(os.path.join(TEMP_DIR, f.name))
        with open(save_path, "wb") as out:
            out.write(f.read())

        rec = {"name": base, "ext": ext, "path": save_path}

        if ext in IMAGE_EXTS:
            image_files.append(rec)
        else:
            text_files.append(rec)

    return text_files, image_files


def clear_temp_dir(TEMP_DIR: str = "uploaded_temp") -> None:
    """
    Vide TEMP_DIR proprement.
    """
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)
