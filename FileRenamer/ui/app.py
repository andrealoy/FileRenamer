import streamlit as st
from ui.streamlit_helpers import (
    upload_files,
    clear_and_clean_button,
    TEXT_EXTS,
    items_to_dataframe
)
from core.ai_pipeline import run_ai_naming

st.set_page_config(page_title="AI File Renamer", layout="wide")
st.title("📂 AI File Renamer")

# -----------------------------
# 1️⃣ Upload des fichiers
# -----------------------------
files = upload_files(TEXT_EXTS)

# -----------------------------
# 2️⃣ Boutons sur la même ligne
# -----------------------------
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    lancer = st.button("🚀 Lancer l'analyse", key="lancer_btn")

with col2:
    clear_and_clean_button("uploaded_temp", key="clear_btn_right")

# -----------------------------
# 3️⃣ Lancer l'analyse
# -----------------------------
if lancer and files:
    # Pipeline AI
    results = run_ai_naming(files)  # renvoie une liste de dicts
    
    # Transformer en DataFrame pour Streamlit
    df_results = items_to_dataframe(results)
    
    # Affichage dans Streamlit
    st.subheader("Résultats de l'analyse")
    st.dataframe(df_results, use_container_width=True)
    
    # Optionnel : télécharger les résultats en CSV
    csv = df_results.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Télécharger les résultats CSV",
        data=csv,
        file_name="ai_file_renamer_results.csv",
        mime="text/csv"
    )
