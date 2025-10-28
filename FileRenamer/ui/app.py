# app.py — Streamlit UI (interface only)
"""
============================================================
📄 AI Text File Renamer — Mode d’emploi 
============================================================

Ce fichier est l’interface principale de l’application Streamlit.
Il permet de renommer automatiquement des fichiers texte à l’aide de l’IA.

💡 Objectif :
--------------------------------------------
Automatiser la création de noms de fichiers clairs et cohérents
à partir du contenu de fichiers texte (ex. rapports, scripts, articles...).

============================================================
🧠 FONCTIONNEMENT GÉNÉRAL
============================================================

1️⃣ — UPLOAD
--------------------------------------------
Appelle la fonction :
    → `upload_files(allowed_exts)`  (dans `streamlit_helpers.py`)

👉 Cette fonction ouvre l’explorateur Streamlit pour que l’utilisateur
puisse déposer ses fichiers texte (PDF, TXT, DOCX, etc.).
Elle renvoie une liste de fichiers avec leur nom, extension et chemin :
    [{"name": ..., "ext": ..., "path": ...}, ...]

------------------------------------------------------------

2️⃣ — ANALYSE IA
--------------------------------------------
Appelle la fonction :
    → `run_ai_naming(text_files)`  (dans `core/ai_pipeline.py`)

👉 Cette fonction :
   - lit le contenu des fichiers texte avec `FileReader`
   - envoie le texte à GPT (via `GPTAgent.generate_description_text`)
   - génère une description courte et neutre
   - puis crée un nouveau nom de fichier avec `GPTAgent.generate_filename`

Elle retourne une liste d’objets avec :
    [
        {
            "name": "ancien_nom",
            "ext": ".txt",
            "path": "uploaded_temp/ancien_nom.txt",
            "clean_description": "brève description du contenu",
            "generated_filename": "nouveau_nom_proposé"
        },
        ...
    ]

------------------------------------------------------------

3️⃣ — AFFICHAGE DES RÉSULTATS
--------------------------------------------
👉 Dans Streamlit, tu affiches les résultats dans un tableau interactif
avec `st.data_editor`.

Cela permet à l’utilisateur :
   - de visualiser les descriptions générées
   - de corriger manuellement les noms si besoin
   - de garder un aperçu clair avant export

------------------------------------------------------------

4️⃣ — EXPORTATION EN ZIP
--------------------------------------------
👉 Une fois la table validée :
   - parcours chaque ligne du DataFrame
   - lis le fichier d’origine via son chemin (`row["Path"]`)
   - écris-le dans un fichier ZIP avec le nouveau nom (`row["Generated File Name"]`)
   - utilise `st.download_button()` pour permettre le téléchargement

Résultat : un ZIP propre, contenant tous les fichiers renommés.

------------------------------------------------------------

5️⃣ — NETTOYAGE / RÉINITIALISATION
--------------------------------------------
Appelle :
    → `clear_temp_dir()` (dans `streamlit_helpers.py`)

👉 Cette fonction vide le dossier temporaire `uploaded_temp`
où sont enregistrés les fichiers uploadés.
Elle est utilisée dans deux cas :
   - quand on clique sur "🧹 Clean temporary files"
   - ou quand on réinitialise l’app ("🔄 Reset App")

------------------------------------------------------------

✅ En résumé :
--------------------------------------------
- `upload_files()` → charge les fichiers
- `run_ai_naming()` → appelle GPT pour décrire et renommer
- `st.data_editor()` → montre les résultats
- `ZIP + download_button` → exporte les fichiers renommés
- `clear_temp_dir()` → nettoie le dossier temporaire

============================================================
🧭 ÉTAPES À SUIVRE POUR UTILISER L’APP
============================================================

1️⃣ Ouvre un terminal dans le dossier du projet.
2️⃣ Exécute :  `streamlit run app.py`
3️⃣ Dépose tes fichiers texte dans la section "Upload".
4️⃣ Clique sur **"🧠 Generate Descriptions & Filenames"**.
5️⃣ Corrige ou valide les noms proposés dans le tableau.
6️⃣ Clique sur **"📦 Create ZIP with Renamed Files"** pour télécharger.
7️⃣ Nettoie si besoin avec **"🧹 Clean temporary files"**.

============================================================
🔍 FICHIERS IMPORTANTS
============================================================

📂 core/
 ├── file_reader.py         → lit et nettoie le texte
 ├── gpt_agent.py           → gère les appels GPT
 └── ai_pipeline.py         → enchaîne tout le processus IA

📂 helpers/
 └── streamlit_helpers.py   → upload et nettoyage des fichiers

============================================================
💬 CONSEIL :
============================================================
Si tu veux tester sans tout relancer :
- Modifie juste le contenu du dossier `uploaded_temp`
- Clique sur "Generate" à nouveau
- Et regarde la table s’actualiser instantanément

Bonne utilisation 👋
============================================================
"""



























# from __future__ import annotations
# import os
# import io
# import zipfile
# import pandas as pd
# import streamlit as st

# # Your helpers (as requested)
# from streamlit_helpers import upload_files, clear_temp_dir

# # ============================================================
# # CONFIGURATION
# # ============================================================
# st.set_page_config(page_title="AI File Name Generator", page_icon="📁", layout="wide")

# # ============================================================
# # SESSION STATE
# # ============================================================
# if "df" not in st.session_state:
#     st.session_state.df = None
# if "uploaded_counts" not in st.session_state:
#     st.session_state.uploaded_counts = {"text": 0, "image": 0}

# # ============================================================
# # UI TITLE
# # ============================================================
# st.title("📁 AI File Name Generator + ZIP Export")

# # ============================================================
# # UPLOAD SECTION (keeps your helper)
# # ============================================================
# allowed_exts = [
#     ".txt", ".docx", ".pdf", ".csv", ".xlsx", ".json",
# ]

# # Expecting your helper to SAVE files to a temp dir and return two lists
# # (text_files, image_files). Each item ideally is a dict with keys like
# # {"name": str, "ext": str, "path": str} — adapt if your helper differs.
# text_files = upload_files(allowed_exts)

# # Feedback on upload
# st.session_state.uploaded_counts = {"text": len(text_files or []), "image": len(image_files or [])}
# st.success(f"✅ {st.session_state.uploaded_counts['text']} text and {st.session_state.uploaded_counts['image']} image files uploaded.")

# # ============================================================
# # AI NAMING (Hook only — no business logic here)
# # ============================================================

# def run_ai_naming(text_files, image_files):
#     """Hook for your backend. Implement elsewhere if desired.
#     Must return a list of dicts with keys:
#     - name (original filename w/out ext)
#     - ext (including dot, e.g. ".png")
#     - path (absolute or temp path to the saved file)
#     - clean_description (string)
#     - generated_filename (string, WITHOUT extension)
#     """
#     raise NotImplementedError("Plug your AI pipeline here (describe/clean/generate)")

# col_left, col_right = st.columns([1, 1])

# with col_left:
#     if st.button("🧠 Generate Descriptions & Filenames", type="primary", use_container_width=True):
#         try:
#             with st.spinner("Analyzing with your AI backend..."):
#                 results = run_ai_naming(text_files or [], image_files or [])
#                 # Build dataframe for review UI
#                 df = pd.DataFrame([
#                     {
#                         "Original File Name": r.get("name", ""),
#                         "Description": r.get("clean_description", ""),
#                         "Generated File Name": f"{r.get('generated_filename', '')}{r.get('ext', '')}",
#                         "Path": r.get("path", ""),
#                     }
#                     for r in (results or [])
#                 ])
#                 st.session_state.df = df
#                 st.success("✅ AI naming complete!")
#         except NotImplementedError as e:
#             st.info("Interface only: backend not connected. Implement `run_ai_naming(...)` to enable this.")
#         except Exception as e:
#             st.error(f"⚠️ An unexpected error occurred: {e}")

# with col_right:
#     # Manual reset & cleanup controls are explicit to avoid deleting files before download
#     if st.button("🧹 Clean temporary files", use_container_width=True):
#         try:
#             clear_temp_dir()
#             st.session_state.df = None
#             st.success("🧼 Temp directory cleaned.")
#         except Exception as e:
#             st.error(f"Could not clean temp dir: {e}")

# # ============================================================
# # REVIEW TABLE + ZIP DOWNLOAD
# # ============================================================
# if st.session_state.df is not None and not st.session_state.df.empty:
#     st.subheader("📝 Review & Edit Filenames")
#     edited = st.data_editor(
#         st.session_state.df,
#         use_container_width=True,
#         hide_index=True,
#         num_rows="dynamic",
#     )
#     st.session_state.df = edited

#     st.divider()

#     # Create ZIP in-memory from the edited names
#     if st.button("📦 Create ZIP with Renamed Files", type="secondary"):
#         try:
#             renamed_files = []
#             zip_buffer = io.BytesIO()
#             with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zipf:
#                 for _, row in st.session_state.df.iterrows():
#                     old_path = row.get("Path", "")
#                     new_name = row.get("Generated File Name", "")

#                     if not old_path or not os.path.exists(old_path):
#                         st.warning(f"Skipping missing file: {old_path}")
#                         continue
#                     if not new_name:
#                         st.warning(f"Skipping unnamed file for path: {old_path}")
#                         continue

#                     with open(old_path, "rb") as src:
#                         zipf.writestr(new_name, src.read())
#                     renamed_files.append(new_name)

#             zip_buffer.seek(0)
#             st.download_button(
#                 "⬇️ Download Renamed Files (.zip)",
#                 zip_buffer,
#                 file_name="renamed_files.zip",
#                 mime="application/zip",
#             )
#             st.success(f"✅ Created ZIP with {len(renamed_files)} files.")
#         except Exception as e:
#             st.error(f"Failed to create ZIP: {e}")

# # ============================================================
# # OPTIONAL: Reset the app state (also cleans temp dir)
# # ============================================================
# st.divider()
# if st.button("🔄 Reset App (clean & clear)"):
#     try:
#         clear_temp_dir()
#     finally:
#         for k in list(st.session_state.keys()):
#             del st.session_state[k]
#         st.rerun()
