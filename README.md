# 📂 AI FileRenamer

**AI FileRenamer** est une application **Streamlit** alimentée par **l’API ChatGPT** qui permet de **renommer automatiquement des fichiers** et de **générer un tableau récapitulatif** contenant :
- le **nom original** du fichier,  
- une **courte description** du contenu,  
- et le **nouveau nom proposé**.  

L’app gère plusieurs formats (txt, json, csv, pdf, docx, xlsx) et inclut une étape de **nettoyage** et **normalisation** avant traitement.

---

## 🚀 Fonctionnalités principales

- 📤 Upload multiple de fichiers (txt, json, csv, pdf, docx, xlsx)
- 🧹 Normalisation automatique des noms (suppression des caractères spéciaux, espaces, etc.)
- 🧽 Nettoyage spécifique des fichiers CSV
- 🧠 Lecture du contenu et génération de **descriptions courtes** via GPT
- 🏷️ Création de **nouveaux noms de fichiers** pertinents
- 📊 Tableau récapitulatif interactif
- 💾 Export des résultats (CSV + ZIP contenant les fichiers renommés)

---

## 🧩 Structure du projet



---

## 🧱 Architecture et fonctionnement

### 🔄 Diagramme global du flux
```mermaid
flowchart TD
    A[Utilisateur lance l'app Streamlit] --> B[Upload de fichiers : txt, json, csv, pdf, docx, xlsx]
    B --> C[Normalisation des noms de fichiers]
    C --> D[Lecture et nettoyage du contenu]
    D --> E[Appel à GPTAgent pour générer une description courte]
    E --> F[Appel à GPTAgent pour proposer un nouveau nom]
    F --> G[Construction du tableau récapitulatif]
    G --> H[Affichage des résultats + options d’export (CSV / ZIP)]


sequenceDiagram
    participant User
    participant StreamlitApp as UI
    participant Pipeline as Core
    participant GPT as GPTAgent
    participant FS as FileSystem

    User->>UI: Upload des fichiers
    UI->>Pipeline: run_ai_naming_with_progress(files)
    Pipeline->>FS: Lecture des fichiers (file_reader)
    Pipeline->>GPT: Génère description courte
    GPT-->>Pipeline: Retour description
    Pipeline->>GPT: Génère nouveau nom
    GPT-->>Pipeline: Retour nom
    Pipeline->>UI: Envoie résultats formatés
    UI->>User: Affiche tableau + options de téléchargement



## 🧰 Installation
### 1️⃣ Cloner le dépôt
git clone https://github.com/andrealoy/FileRenamer.git
cd FileRenamer

###2️⃣ Créer un environnement virtuel (recommandé)
python -m venv .venv
source .venv/bin/activate   # macOS / Linux
.venv\Scripts\activate      # Windows

###3️⃣ Installer les dépendances
pip install -r requirements.txt

### 4️⃣ Configurer la clé API OpenAI
export OPENAI_API_KEY="sk-xxxxx"   # macOS / Linux
setx OPENAI_API_KEY "sk-xxxxx"     # Windows

⚠️ Ne commitez jamais votre clé API dans le dépôt GitHub.

### 🖥️ Utilisation
Lancer l’application Streamlit :
streamlit run ui/app.py
L’application s’ouvre dans votre navigateur à l’adresse :
👉 http://localhost:8501

Étapes :
Uploader vos fichiers
Cliquer sur 🚀 Lancer l’analyse
L’IA lit les fichiers et génère :
une description
un nouveau nom
Téléchargez :
le CSV des résultats
le ZIP contenant les fichiers renommés

### 🧠 Détails techniques
core/ai_pipeline.py

Pipeline en 4 étapes principales :
Lecture du texte (FileReader)
Génération de description (GPTAgent.generate_description_text)
Proposition de nouveau nom (GPTAgent.generate_filename)
Formatage pour l’interface
core/file_reader.py
Gère la lecture et le nettoyage des fichiers (txt, csv, pdf, docx, xlsx, json)
Normalise les noms et les contenus avant envoi à l’IA
core/gpt_agent.py
Interface avec l’API ChatGPT
Génère une courte description et un nom adapté pour chaque fichier
ui/app.py
Interface Streamlit
Gestion de l’upload, affichage des résultats, boutons de téléchargement

### 🧪 Tests
Ajouter vos tests unitaires dans un dossier tests/ :
pytest tests/
Cas à tester :
Normalisation des noms de fichiers
Nettoyage CSV
Réponses mockées de GPTAgent
### ⚙️ Personnalisation
Modèle GPT : configurable (GPT-4, GPT-3.5, etc.)
Température / style : ajustable via variable d’environnement
Stratégies de nommage : ajout de préfixes/suffixes, datation, incréments
⚠️ Confidentialité
Les fichiers sont temporairement lus et analysés pour génération de texte.
⚠️ Ne pas uploader de documents sensibles : le contenu est envoyé à l’API GPT pour traitement.
En production, envisagez :
un anonymiseur de texte
un modèle local hébergé sur serveur sécurisé
📦 Export et formats
CSV : liste des noms originaux / descriptions / nouveaux noms
ZIP : contient les fichiers renommés avec les nouveaux noms générés
🤝 Contribution
Les contributions sont les bienvenues !
Suggestions d’améliorations :
Support de nouveaux formats
Tests unitaires étendus
Interface plus riche (barre de progression, logs détaillés)
Pour contribuer :
Forker le dépôt
Créer une branche (feature/ma-feature)
Commit & push
Ouvrir une Pull Request
📄 Licence
MIT License — libre d’utilisation, modification et distribution.
👨‍💻 Auteur
Développé par Andréa Loy
💡 Basé sur Python, Streamlit et OpenAI GPT API.




