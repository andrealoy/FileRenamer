"""
Script de lancement principal de l’application Streamlit.

Ce script exécute l’interface utilisateur située dans `ui/app.py`
en utilisant la commande `streamlit run`.

Usage :
    python main.py
"""

import os 
os.system("python -m streamlit run ui/app.py")