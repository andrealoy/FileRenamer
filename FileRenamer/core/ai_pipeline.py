from core.file_reader import FileReader
from core.gpt_agent import GPTAgent

# Étape 1 — lecture texte
def step_read_text_files(text_files):
    items = []
    for f in text_files:
        reader = FileReader(f["path"])
        clean_text = reader.read_text_file()
        items.append({
            "name": f["name"],
            "ext": f["ext"],
            "path": f["path"],
            "clean_text": clean_text
        })
    return items

# Étape 2 — descriptions texte
def step_generate_description_text(items, gpt):
    out = []
    for it in items:
        try:
            desc = gpt.generate_description_text(it["clean_text"])
        except Exception as e:
            desc = f"(error generating description: {e})"
        out.append({**it, "clean_description": desc})
    return out

# Étape 3 — génération de noms de fichiers
def step_generate_filenames(items, gpt):
    out = []
    for it in items:
        try:
            filename = gpt.generate_filename(it["clean_description"])
        except Exception as e:
            filename = it["name"]
        out.append({**it, "generated_filename": filename})
    return out

# Étape 4 — format final
def step_format_for_ui(items):
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
# 🚀 Pipeline complet — uniquement texte
# ----------------------------------------------------------
def run_ai_naming(text_files):
    """
    1️⃣ Lecture et description texte
    2️⃣ Génération des filenames
    """
    gpt = GPTAgent(paths=None)

    # Texte
    text_items = step_read_text_files(text_files)
    text_items = step_generate_description_text(text_items, gpt)
    text_items = step_generate_filenames(text_items, gpt)

    return step_format_for_ui(text_items)
