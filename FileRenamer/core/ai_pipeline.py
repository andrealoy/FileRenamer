from core.file_reader import FileReader
from core.gpt_agent import GPTAgent
import os
from concurrent.futures import ProcessPoolExecutor, as_completed
from typing import List, Dict, Any, Optional


# Lecture texte simple
def step_process_single_file(files_input: Dict[str, str]) -> Dict[str, Any]:
    """Lit un fichier texte et retourne un dictionnaire contenant les informations nettoyées."""
    reader = FileReader()
    clean_text = reader.read_text_file(files_input["path"])
    item = {
        "name": files_input["name"],
        "ext": files_input["ext"],
        "path": files_input["path"],
        "clean_text": clean_text,
    }
    return item


# Lecture texte multiprocessée
def read_multiprocessed(text_files: List[Dict[str, str]]) -> List[Dict[str, Any]]:
    """
    Lit plusieurs fichiers en parallèle à l'aide d'un pool de processus.
    Retourne une liste de dictionnaires contenant les textes nettoyés.
    """
    num_workers = min(len(text_files), os.cpu_count() - 1)
    results = []
    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        futures = {executor.submit(step_process_single_file, f): f for f in text_files}

        for future in as_completed(futures):
            try:
                item = future.result()
                results.append(item)
            except Exception as e:
                print(f"❌ Erreur avec {futures[future]['name']}: {e}")
    return results


# Descriptions texte
def step_generate_description_text(items: List[Dict[str, Any]], gpt: GPTAgent) -> List[Dict[str, Any]]:
    """
    Utilise GPT pour générer une description textuelle à partir du contenu nettoyé de chaque fichier.
    Retourne la liste enrichie avec une clé 'clean_description'.
    """
    out = []
    for it in items:
        try:
            desc = gpt.generate_description_text(it["clean_text"])
        except Exception as e:
            desc = f"(erreur lors de la génération de la description : {e})"
        out.append({**it, "clean_description": desc})
    return out


# Génération de noms de fichiers
def step_generate_filenames(items: List[Dict[str, Any]], gpt: GPTAgent) -> List[Dict[str, Any]]:
    """
    Utilise GPT pour générer un nom de fichier à partir de la description nettoyée.
    Retourne la liste enrichie avec une clé 'generated_filename'.
    """
    out = []
    for it in items:
        try:
            filename = gpt.generate_filename(it["clean_description"])
        except Exception as e:
            filename = it["name"]
        out.append({**it, "generated_filename": filename})
    return out


# Vérifie les doublons et supprime les extensions inutiles
def step_sanitize_names(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Supprime les doublons dans les noms de fichiers générés et enlève les extensions multiples.
    Si un nom existe déjà, un suffixe numérique est ajouté.
    """
    used: Dict[str, int] = {}
    for it in items:
        base_name = it["generated_filename"].strip()
        name_no_ext = os.path.splitext(base_name)[0]  # enlève toute extension éventuelle
        ext = it["ext"]

        if name_no_ext in used:
            used[name_no_ext] += 1
            final_name = f"{name_no_ext}_{used[name_no_ext]}"
        else:
            used[name_no_ext] = 1
            final_name = name_no_ext

        it["generated_filename"] = f"{final_name}{ext}"

    return items


# Format final
def step_format_for_ui(items: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    """
    Prépare les données dans un format compatible avec une interface utilisateur (UI).
    Retourne une liste contenant uniquement les champs utiles.
    """
    return [
        {
            "name": it["name"],
            "ext": it["ext"],
            "path": it["path"],
            "clean_description": it.get("clean_description", ""),
            "generated_filename": it.get("generated_filename", it["name"]),
        }
        for it in items
    ]


# ----------------------------------------------------------
# 🚀 Pipeline complet
# ----------------------------------------------------------

def run_ai_naming(processed: List[Dict[str, Any]], gpt: Optional[GPTAgent] = None) -> List[Dict[str, str]]:
    """
    1️⃣ Génère une description textuelle à partir du contenu nettoyé.
    2️⃣ Crée un nom de fichier adapté à partir de la description.
    3️⃣ Formate les résultats pour affichage dans l'UI.
    """
    gpt = gpt or GPTAgent()

    described = step_generate_description_text(processed, gpt)
    renamed = step_generate_filenames(described, gpt)
    return step_format_for_ui(renamed)
