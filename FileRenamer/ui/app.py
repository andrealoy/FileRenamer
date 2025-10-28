#app.py -- Main Streamlit Application 

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # So we are able to execute the app from the main package or inside the ui folder

from core.utils import identify_extension
from core.file_io import FileReader 
import pandas as pd 
import streamlit as st 
from streamlit_helpers import upload_files , clear_temp_dir

# ============================================================
# CONFIGURATION
# ============================================================

allowed_exts = [".png" , ".jpg" , ".jpeg" , ".bmp" , ".tiff" , ".txt" , ".docx" , ".pdf" , ".csv" , ".xlsx" , ".json"]
uploaded_files = st.file_uploader("Choose Files" , type=allowed_exts , accept_multiple_files=True)

upload_files(uploaded_files)


############### TON CODE ICI ###############


# Cleaning à la fin pour supprimer les fichiers dans le dossier temporaire aprés traitement 
clear_temp_dir() 
