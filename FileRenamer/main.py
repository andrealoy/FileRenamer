import os
from core.file_io import FileReader
from core.utils import identify_extension

def process_file(path):
    """Lit un fichier texte et affiche un aperçu."""
    ext, filetype = identify_extension(path)
    print(f"\n📄 {os.path.basename(path)} — type détecté : {filetype}")

    if filetype == "text":
        try:
            reader = FileReader(path)
            content = reader.read_text_file()
            print("--- CONTENU DU FICHIER ---\n")
            print(content)
        except Exception as e:
            print(f"❌ Erreur de lecture : {e}")
    else:
        print("⚠️ Fichier ignoré (non texte).")

def main():
    path = input("👉 Entre le chemin du fichier ou du dossier à lire : ").strip()

    if not os.path.exists(path):
        print("❌ Le chemin n'existe pas.")
        return

    # Si c’est un dossier → on lit tous les fichiers à l’intérieur
    if os.path.isdir(path):
        print(f"\n📁 Parcours du dossier : {path}\n")
        for root, _, files in os.walk(path):
            for f in files:
                file_path = os.path.join(root, f)
                process_file(file_path)
    else:
        process_file(path)

if __name__ == "__main__":
    main()
