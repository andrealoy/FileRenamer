import streamlit as st
from ui.streamlit_helpers import (
    upload_files,
    clear_and_clean_button,
    clear_and_clean,
    TEXT_EXTS,
    items_to_dataframe,
    download_zip_button,
    run_ai_naming_with_progress
)

st.set_page_config(page_title="AI File Renamer", layout="wide")
st.title("📂 AI File Renamer")

# -----------------------------
#  Upload fichiers
# -----------------------------
files = upload_files(TEXT_EXTS)

# -----------------------------
#  Boutons alignés
# -----------------------------
col1, col2, col3 = st.columns([3, 2, 1])
with col1:
    lancer = st.button("🚀 Lancer l'analyse", key="lancer_btn")
with col3:
    clear_and_clean_button("uploaded_temp")

# -----------------------------
#  Lancer pipeline AI
# -----------------------------
if lancer and files:
    with st.spinner("⌛ Analyse en cours…"):
        results = run_ai_naming_with_progress(files)
        df_results = items_to_dataframe(results)
        st.session_state["last_results_df"] = df_results


# -----------------------------
#  Affichage DataFrame + téléchargements
# -----------------------------
if st.session_state.get("last_results_df") is not None:
    st.subheader("Résultats de l'analyse")
    df = st.session_state["last_results_df"]

    # Affichage DataFrame
    st.dataframe(
        df[["Nom", "Description", "Nouveau nom"]],
        use_container_width=True
    )

    # CSV
    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        label="📥 Télécharger les résultats CSV",
        data=csv,
        file_name="ai_file_renamer_results.csv",
        mime="text/csv",
        key="download_results_btn"
    )

    # ZIP
    zip_items = [
        {"path": row["path"], "generated_filename": row["Nouveau nom"]}
        for _, row in df.iterrows()
    ]
    download_zip_button(zip_items, zip_name="renamed_files.zip")
