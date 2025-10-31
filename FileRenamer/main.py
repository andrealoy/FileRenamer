"""
🚀 Point d’entrée principal de FileRenamer
Lance automatiquement l’application Streamlit (`ui/app.py`)
sur Windows, macOS et Linux.

Usage :
    python main.py
"""

import os
import sys
import platform
import subprocess
from typing import NoReturn


def launch_streamlit() -> NoReturn:
    """
    Lance l’application Streamlit avec la commande appropriée
    selon le système d’exploitation.
    """

    # Chemin du fichier Streamlit à exécuter
    app_path = os.path.join("ui", "app.py")

    if not os.path.exists(app_path):
        print(f"❌ Erreur : le fichier {app_path} est introuvable.")
        sys.exit(1)

    # Détection du système
    system = platform.system().lower()

    # Commande adaptée à chaque OS
    if "windows" in system:
        python_cmd = "python"
    else:  # macOS ou Linux
        python_cmd = "python3" if shutil.which("python3") else "python"

    # Commande finale
    command = [python_cmd, "-m", "streamlit", "run", app_path]

    print(f"🌍 Lancement de Streamlit via : {' '.join(command)}")
    print("🔗 L'application s'ouvrira automatiquement dans ton navigateur.\n")

    try:
        # Exécute la commande sans bloquer la compatibilité Streamlit
        subprocess.run(command, check=True)
    except KeyboardInterrupt:
        print("\n🛑 L’application a été interrompue manuellement.")
        sys.exit(0)
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Échec du lancement Streamlit : {e}")
        sys.exit(1)


if __name__ == "__main__":
    import shutil
    launch_streamlit()
