from openai import OpenAI
import re
from typing import Optional

client = OpenAI()


class GPTAgent:
    """
    Agent GPT chargé de générer des descriptions et des noms de fichiers à partir de texte brut.
    
    Cet agent interagit avec l'API OpenAI pour :
    - Résumer le contenu d'un fichier sous forme de phrase courte et neutre.
    - Générer un nom de fichier clair et concis à partir d'une description.
    """

    def __init__(self, model_name: str = "gpt-4.1") -> None:
        """
        Initialise l'agent GPT avec le modèle spécifié.
        
        Args:
            model_name: Nom du modèle OpenAI à utiliser (par défaut : 'gpt-4.1').
        """
        self.model_name = model_name

    # ----------------------------------------------------
    #  Nettoyage du texte généré par GPT
    # ----------------------------------------------------
    def _clean_gpt_text(self, text: str) -> str:
        """
        Nettoie le texte brut généré par GPT pour supprimer les formules inutiles
        et les guillemets ou espaces superflus.
        
        Args:
            text: Texte brut retourné par GPT.
        
        Returns:
            Texte nettoyé et condensé.
        """
        text = re.sub(
            r"(?i)\b(of course|sure|here's|as an ai|certainly|let me|i can|this image|this text)\b.*?:",
            "",
            text
        )
        text = re.sub(r"(?i)\b(of course|sure|certainly|let me)\b", "", text)
        text = text.replace('"', '').replace("'", "").replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ----------------------------------------------------
    #  Génération d'une description de fichier texte
    # ----------------------------------------------------
    def generate_description_text(self, text: str) -> str:
        """
        Génère une courte description neutre d’un texte à l’aide de GPT.
        
        Args:
            text: Contenu brut du fichier à résumer.
        
        Returns:
            Une phrase unique et descriptive générée par GPT.
        """
        prompt = f"""
You are an assistant that summarizes text files.
Write ONE short, neutral sentence describing this file.
No commentary, no introduction, no quotes. Don't start by "This file contains" or "This file depicts"
Please write ONLY the description.

CONTENT:
{text[:2000]}
"""
        response = client.responses.create(
            model=self.model_name,
            input=prompt
        )
        raw_output: str = response.output_text.strip()
        return self._clean_gpt_text(raw_output)

    # ----------------------------------------------------
    # Génération d’un nom de fichier à partir d’une description
    # ----------------------------------------------------
    def generate_filename(self, description: str) -> str:
        """
        Génère un nom de fichier clair et concis à partir d’une description.
        
        Args:
            description: Phrase descriptive du contenu du fichier.
        
        Returns:
            Nom de fichier en minuscules, avec des underscores, sans extension ni ponctuation.
        """
        prompt = f"""
You are an assistant that creates filenames from short descriptions.

Given the following description:
"{description}"

Generate a clear, short filename (3–5 lowercase English words).
Use underscores (_) instead of spaces.
Do not add extensions or commentary.
Do not include the file type (pdf , doc , xlsx...) in the name.
Only output the filename itself.
"""
        response = client.responses.create(
            model=self.model_name,
            input=prompt
        )
        raw_output: str = response.output_text.strip()
        clean_name = self._clean_gpt_text(raw_output)
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "", clean_name)
        return clean_name.lower() or "unnamed_file"
