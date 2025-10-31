import os
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from FileRenamer.core.file_reader import FileReader


# --- CONFIG ---
PATH = "./examples/"
MAX_WORKERS = os.cpu_count()  # nombre optimal de cœurs CPU


# --- FONCTION TRAITEMENT ---
def process_file(filename):
    """Lit un fichier et retourne les infos utiles."""
    reader = FileReader()  # chaque process a sa propre instance
    filepath = os.path.join(PATH, filename)

    start = time.time()
    text = reader.read_text_file(filepath)
    duration = time.time() - start

    wordcount = len(text.split())
    return filename, text, wordcount, duration


# --- MAIN EXECUTION ---
if __name__ == "__main__":
    files = os.listdir(PATH)
    print(f"{len(files)} files in folder '{PATH}'")
    print("=" * 100)

    start_total = time.time()

    with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(process_file, f): f for f in files}

        for future in as_completed(futures):
            filename, text, wordcount, duration = future.result()
            print(f"\n{'=' * 100}")
            print(f"FILE: {filename}")
            print(f"{'-' * 100}")
            print(text[:1000])  # limite l’affichage si texte long
            print(f"{'-' * 100}")
            print(f"WORDCOUNT: {wordcount}")
            print(f"ELAPSED: {duration:.2f}s")

    total_duration = time.time() - start_total
    print("=" * 100)
    print(f"✅ Done! Total time: {total_duration:.2f}s using {MAX_WORKERS} processes.")
