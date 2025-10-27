import streamlit as st 
import os 

# ============================================================
# CONFIGURATION
# ============================================================
TEMP_DIR = "uploaded_temp"
CLASSIFIED_DIR = "classified_files"
os.makedirs(TEMP_DIR, exist_ok=True)
os.makedirs(CLASSIFIED_DIR, exist_ok=True)