# streamlit_helpers.py — version texte uniquement
import os
import shutil
import random 
import streamlit as st

TEXT_EXTS = {".txt", ".docx", ".pdf", ".csv", ".xlsx", ".json"}

def upload_files(allowed_exts, TEMP_DIR: str = "uploaded_temp"):
    os.makedirs(TEMP_DIR, exist_ok=True)

    if "uploaded_files" not in st.session_state:
        st.session_state["uploaded_files"] = []

    # Clé dynamique pour le file_uploader
    key = st.session_state.get("file_uploader_key", "file_uploader_default")

    uploaded = st.file_uploader(
        "📂 Dépose tes fichiers texte ici",
        type=[ext.lstrip(".") for ext in allowed_exts],
        accept_multiple_files=True,
        key=key
    )

    if uploaded:
        # On n'ajoute que les fichiers réellement nouveaux
        existing_paths = {f["path"] for f in st.session_state["uploaded_files"]}
        for f in uploaded:
            base, ext = os.path.splitext(f.name)
            ext = ext.lower()
            save_path = os.path.abspath(os.path.join(TEMP_DIR, f.name))
            if save_path in existing_paths:
                continue  # éviter les doublons

            # Sauvegarde sur le disque
            with open(save_path, "wb") as out:
                out.write(f.read())

            # Ajout dans le session_state
            st.session_state["uploaded_files"].append({
                "name": base,
                "ext": ext,
                "path": save_path
            })

    return st.session_state["uploaded_files"]


def clear_temp_dir(TEMP_DIR: str = "uploaded_temp") -> None:
    """
    Supprime et recrée le dossier temporaire utilisé pour les uploads.
    """
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR)
    os.makedirs(TEMP_DIR, exist_ok=True)

def clear_and_clean_button(TEMP_DIR: str = "uploaded_temp"):
    """
    Vide TEMP_DIR et réinitialise les fichiers uploadés, y compris le file_uploader
    """
    if st.button("🧹 Clear & Clean"):
        # Vider le dossier temporaire
        clear_temp_dir(TEMP_DIR)

        # Réinitialiser les fichiers uploadés
        st.session_state["uploaded_files"] = []

        # Générer une clé unique pour le file_uploader
        st.session_state["file_uploader_key"] = f"file_uploader_{random.randint(0, 100000)}"

        st.success("Dossier temporaire vidé et fichiers uploadés réinitialisés !")

# # streamlit_helpers.py — version texte uniquement
# import os
# import shutil
# import streamlit as st

# TEXT_EXTS = {".txt", ".docx", ".pdf", ".csv", ".xlsx", ".json"}


# def upload_files(allowed_exts, TEMP_DIR: str = "uploaded_temp"):
#     """
#     Ouvre un file_uploader Streamlit, sauvegarde les fichiers dans TEMP_DIR,
#     et renvoie une liste de dictionnaires :
#     [
#         {"name": "document", "ext": ".txt", "path": "uploaded_temp/document.txt"},
#         ...
#     ]
#     """
#     os.makedirs(TEMP_DIR, exist_ok=True)

#     # Normalisation des extensions acceptées
#     allowed_types = [ext.lstrip(".").lower() for ext in allowed_exts]
#     allowed_exts_norm = {e.lower() for e in allowed_exts}

#     uploaded = st.file_uploader(
#         "📂 Dépose tes fichiers texte ici",
#         type=allowed_types,
#         accept_multiple_files=True
#     )

#     text_files = []

#     for f in uploaded or []:
#         base, ext = os.path.splitext(f.name)
#         ext = ext.lower()
#         if ext not in allowed_exts_norm:
#             continue

#         save_path = os.path.abspath(os.path.join(TEMP_DIR, f.name))
#         with open(save_path, "wb") as out:
#             out.write(f.read())

#         text_files.append({"name": base, "ext": ext, "path": save_path})

#     return text_files


# def clear_temp_dir(TEMP_DIR: str = "uploaded_temp") -> None:
#     """
#     Supprime et recrée le dossier temporaire utilisé pour les uploads.
#     """
#     if os.path.exists(TEMP_DIR):
#         shutil.rmtree(TEMP_DIR)
#     os.makedirs(TEMP_DIR, exist_ok=True)
