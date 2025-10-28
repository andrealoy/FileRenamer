"""
FileRenamer - Guide rapide pour l'interface Streamlit

Objectif :
Ce projet renomme automatiquement des fichiers texte à l’aide d’un agent GPT. Le pipeline lit le contenu des fichiers, génère une description, puis propose un nouveau nom cohérent.

Structure utile :
- core/ai_pipeline.py : contient le pipeline principal
- ui/streamlit_helpers.py : gère l’upload et le dossier temporaire
- ui/app.py : interface Streamlit à compléter

Fonctionnement :
1. L’utilisateur charge des fichiers via Streamlit.
2. La fonction upload_files(TEXT_EXTS) sauvegarde les fichiers dans uploaded_temp/ et renvoie une liste :
   [{"name": "fichier", "ext": ".txt", "path": "uploaded_temp/fichier.txt"}]
3. Ces fichiers sont passés au pipeline :
   from core.ai_pipeline import run_ai_naming
   results = run_ai_naming(text_files)
4. Chaque élément de results contient :
   - name : nom original
   - ext : extension
   - path : chemin complet
   - clean_description : description générée par GPT
   - generated_filename : nouveau nom proposé
   
To do : 
-integrer le pipeline dans l'interface 
-ajouter un petit élément qui montre un chargement
-integrer le tableau pour afficher les resultats et pouvoir renommer les fichiers ou on est pas fan du nom
-integrer l'export zip (dans utils.py)

Pour lancer le projet streamlit run ui/app.py depuis le dossier FileRenamer ( qui contient ui , core etc... )
"""




# EXEMPLE MINIMAL D'INTERFACE

import os
import streamlit as st 
from core.ai_pipeline import run_ai_naming
#from ui.streamlit_helpers import upload_files, clear_temp_dir, TEXT_EXTS
from ui.streamlit_helpers import upload_files, clear_temp_dir, clear_and_clean_button, TEXT_EXTS

st.title("AI File Renamer")

TEMP_DIR = "uploaded_temp"

# --- Bouton Clear & Clean ---
clear_and_clean_button(TEMP_DIR)

# --- Upload des fichiers ---
if "uploaded_files" not in st.session_state:
    st.session_state["uploaded_files"] = []

# Ajouter les nouveaux fichiers uploadés
new_files = upload_files(TEXT_EXTS, TEMP_DIR)
if new_files:
    # Ajouter uniquement les fichiers qui ne sont pas déjà dans la session_state
    existing_paths = {f["path"] for f in st.session_state["uploaded_files"]}
    for f in new_files:
        if f["path"] not in existing_paths:
            st.session_state["uploaded_files"].append(f)

text_files = st.session_state["uploaded_files"]

# --- Lancement de l'analyse ---
if st.button("Lancer l'analyse") and text_files:
    results = run_ai_naming(text_files)
    for r in results:
        st.subheader(f"{r['name']}{r['ext']}")
        st.write(f"Description : {r['clean_description']}")
        st.write(f"Nouveau nom : {r['generated_filename']}{r['ext']}")




#st.title("AI File Renamer")

#text_files = upload_files(TEXT_EXTS)

# if st.button("Lancer l'analyse") and text_files:
#     results = run_ai_naming(text_files)
#     for r in results:
#         st.subheader(f"{r['name']}{r['ext']}")
#         st.write(f"Description : {r['clean_description']}")
#         st.write(f"Nouveau nom : {r['generated_filename']}{r['ext']}")
# clear_temp_dir()
