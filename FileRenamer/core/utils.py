import os

def identify_extension(file_path: str):
    """
    Identifie l’extension d’un fichier et détermine s’il s’agit
    d’un fichier texte pris en charge par le pipeline.

    Retourne un tuple : (extension, type)
        - extension : ex. ".txt"
        - type : "text" ou "unknown"

    Exemple :
        identify_extension("data/report.pdf")
        → (".pdf", "text")

        identify_extension("photo.png")
        → (".png", "unknown")
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower().strip()

    # Extensions de texte supportées
    text_exts = {".txt", ".pdf", ".docx", ".csv", ".xlsx", ".json"}

    if ext in text_exts:
        filetype = "text"
    else:
        filetype = "unknown"

    return ext, filetype


def is_text_file(file_path: str) -> bool:
    """
    Vérifie si un fichier est un fichier texte supporté.
    Retourne True pour les fichiers texte, False sinon.
    """
    _, filetype = identify_extension(file_path)
    return filetype == "text"
