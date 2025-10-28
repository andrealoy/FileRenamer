# main.py
import os
from core.ai_pipeline import run_ai_naming
from core.utils import is_text_file

def collect_text_files_from_folder(folder_path):
    """
    Explore un dossier et récupère uniquement les fichiers texte (.txt, .pdf, .csv, etc.)
    Retourne une liste de dictionnaires :
        [{"name": "mon_fichier", "ext": ".txt", "path": "C:/.../mon_fichier.txt"}]
    """
    text_files = []

    for root, _, filenames in os.walk(folder_path):
        for fname in filenames:
            name, ext = os.path.splitext(fname)  # ← correction ici
            abs_path = os.path.join(root, fname)

            if is_text_file(abs_path):
                text_files.append({"name": name, "ext": ext.lower(), "path": abs_path})

    return text_files

def main():
    print("=== 🧠 AI Text File Naming Pipeline ===\n")

    # 💡 Demande à l’utilisateur un dossier à analyser
    folder = input("👉 Enter folder path to analyze: ").strip()
    if not os.path.isdir(folder):
        print(f"❌ Folder not found: {folder}")
        return

    # 🧩 Collecter uniquement les fichiers texte
    text_files = collect_text_files_from_folder(folder)

    if len(text_files) == 0:
        print("⚠️ No supported text files found in this folder.")
        return

    print(f"✅ Found {len(text_files)} text files.")
    print("🚀 Running AI pipeline...\n")

    # 🚀 Appel du pipeline principal
    results = run_ai_naming(text_files)

    # 🧾 Affichage des résultats
    print("\n=== RESULTS ===")
    for r in results:
        print(f"📄 Original: {r['name']}{r['ext']}")
        print(f"📝 Description: {r['clean_description']}")
        print(f"💾 New Filename: {r['generated_filename']}{r['ext']}")
        print("-" * 50)

    print(f"\n🎉 Done! Processed {len(text_files)} text files total.")


if __name__ == "__main__":
    main()
