import os
import zipfile
from typing import Tuple, List


def identify_extension(file_path: str) -> Tuple[str, str]:
    """
    Identifie l’extension d’un fichier et détermine s’il s’agit
    d’un fichier texte pris en charge par le pipeline.

    Args:
        file_path: Chemin complet vers le fichier à analyser.

    Returns:
        tuple[str, str]: 
            - extension : par exemple ".txt"
            - type : "text" si pris en charge, sinon "unknown"

    Exemple :
        >>> identify_extension("data/report.pdf")
        (".pdf", "text")

        >>> identify_extension("photo.png")
        (".png", "unknown")
    """
    _, ext = os.path.splitext(file_path)
    ext = ext.lower().strip()

    # Extensions de fichiers texte supportées
    text_exts = {".txt", ".pdf", ".docx", ".csv", ".xlsx", ".json"}

    filetype = "text" if ext in text_exts else "unknown"
    return ext, filetype


def is_text_file(file_path: str) -> bool:
    """
    Vérifie si un fichier est un fichier texte pris en charge.

    Args:
        file_path: Chemin du fichier à vérifier.

    Returns:
        bool: True si le fichier est de type texte, False sinon.
    """
    _, filetype = identify_extension(file_path)
    return filetype == "text"


def zip_files(file_paths: List[str], output_zip_path: str) -> str:
    """
    Crée une archive ZIP contenant les fichiers spécifiés.

    Args:
        file_paths: Liste des chemins absolus des fichiers à inclure dans l’archive.
        output_zip_path: Chemin complet du fichier ZIP à créer.

    Returns:
        str: Chemin du fichier ZIP généré.
    """
    with zipfile.ZipFile(output_zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for path in file_paths:
            if os.path.isfile(path):
                arcname = os.path.basename(path)  # Nom du fichier à l’intérieur du ZIP
                zipf.write(path, arcname)
    return output_zip_path
