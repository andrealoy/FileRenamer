from openai import OpenAI
import re

client = OpenAI()

class GPTAgent:
    def __init__(self, paths=None):
        self.paths = paths

    # ----------------------------------------------------
    # 🧹 Nettoyage du texte GPT
    # ----------------------------------------------------
    def clean_gpt_text(self, text: str) -> str:
        text = re.sub(r"(?i)\b(of course|sure|here's|as an ai|certainly|let me|i can|this image|this text)\b.*?:", "", text)
        text = re.sub(r"(?i)\b(of course|sure|certainly|let me)\b", "", text)
        text = text.replace('"', '').replace("'", "").replace("\n", " ")
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    # ----------------------------------------------------
    # 🧠 Description pour fichier texte
    # ----------------------------------------------------
    def generate_description_text(self, text: str) -> str:
        prompt = f"""
You are an assistant that summarizes text files.
Write ONE short, neutral sentence describing this file.
No commentary, no introduction, no quotes.

CONTENT:
{text[:2000]}
"""
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )
        raw_output = response.output_text.strip()
        return self.clean_gpt_text(raw_output)

    # ----------------------------------------------------
    # 🧠 Génération de filename à partir d’une description
    # ----------------------------------------------------
    def generate_filename(self, description: str) -> str:
        prompt = f"""
You are an assistant that creates filenames from short descriptions.

Given the following description:
"{description}"

Generate a clear, short filename (3–5 lowercase English words).
Use underscores (_) instead of spaces.
Do not add extensions or commentary.
Only output the filename itself.
"""
        response = client.responses.create(
            model="gpt-4.1",
            input=prompt
        )
        raw_output = response.output_text.strip()
        clean_name = self.clean_gpt_text(raw_output)
        clean_name = re.sub(r"[^a-zA-Z0-9_]", "", clean_name)
        return clean_name.lower() or "unnamed_file"
