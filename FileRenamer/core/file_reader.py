import os
import json
import pandas as pd
import pdfplumber
from docx import Document
import re
from typing import Optional
from .utils import identify_extension
from zipfile import is_zipfile


class FileReader:
    """
    Lecteur de fichiers multi-formats robuste, capable d'extraire un texte propre et normalisé
    à partir de différents types de fichiers (.txt, .json, .csv, .xlsx, .pdf, .docx).

    Conçu pour l'ingestion dans des modèles de langage (LLM) ou pipelines NLP :
    - Supprime les emojis, caractères spéciaux et valeurs vides
    - Normalise les espaces et la mise en forme
    - Retourne une chaîne de texte nettoyée prête à l'analyse
    """

    def __init__(self, max_words: int = 500, remove_emojis: bool = True) -> None:
        """
        Initialise le lecteur avec des options de nettoyage.
        
        Args:
            max_words: Nombre maximum de mots à conserver dans le texte final.
            remove_emojis: Si vrai, supprime les emojis du texte.
        """
        self.max_words = max_words
        self.remove_emojis = remove_emojis
        self.path: Optional[str] = None
        self.ext: Optional[str] = None

    # ------------------------------------------------------------
    #  Normalisation du texte brut
    # ------------------------------------------------------------
    def _normalize_text(self, text: str) -> str:
        """
        Nettoie et standardise le texte brut :
        - Supprime les emojis et caractères non désirés
        - Remplace les tabulations et retours à la ligne par des espaces
        - Réduit les espaces multiples à un seul
        - Convertit le texte en minuscules
        - Tronque à `max_words` mots
        """
        if self.remove_emojis:
            text = re.sub(r'[\U0001F600-\U0001FAFF]', '', text)

        text = text.replace("\n", " ").replace("\t", " ")
        text = re.sub(r"[^a-zA-Z0-9\sàâäéèêëïîôöùûüç.,;:!?'/\-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        words = text.split()[:self.max_words]
        return " ".join(words).lower()

    # ------------------------------------------------------------
    #  Nettoyage universel de DataFrame (CSV / Excel)
    # ------------------------------------------------------------
    def _clean_dataframe(self, df: pd.DataFrame, max_cells: int = 10000) -> str:
        """
        Nettoie un DataFrame pour extraire un texte lisible :
        - Supprime les valeurs NaN, NaT, None, Unnamed et vides
        - Limite le nombre de cellules analysées pour éviter les surcharges
        - Concatène toutes les cellules en une chaîne unique nettoyée
        """
        df = df.fillna("").astype(str)
        flat_values = df.values.ravel()[:max_cells]

        mask = ~pd.Series(flat_values).str.match(
            r"^\s*(nan|nat|none|null|unnamed.*)?\s*$",
            case=False,
            na=True
        )
        valid_cells = flat_values[mask.values]

        text = " ".join(valid_cells).lower()
        text = re.sub(r"[^a-zA-Z0-9\sàâäéèêëïîôöùûüç.,;:!?'/\-]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()

        words = text.split()[:self.max_words]
        return " ".join(words)

    # ------------------------------------------------------------
    #  Lecteurs individuels
    # ------------------------------------------------------------
    def text_reader(self) -> str:
        """Lit un fichier texte (.txt) et retourne le texte normalisé."""
        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return self._normalize_text(text)

    def json_reader(self) -> str:
        """Lit un fichier JSON et retourne son contenu sous forme de texte normalisé."""
        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        text = json.dumps(data, indent=2, ensure_ascii=False)
        return self._normalize_text(text)

    def pdf_reader(self) -> str:
        """Lit un fichier PDF et retourne le texte extrait et normalisé."""
        all_text = []
        with pdfplumber.open(self.path) as pdf:
            for i, page in enumerate(pdf.pages):
                raw_text = page.extract_text() or ""
                all_text.extend(raw_text.splitlines())
                if len(all_text) >= self.max_words:
                    break
        return self._normalize_text(" ".join(all_text))

    def docx_reader(self) -> str:
        """Lit un fichier Word (.docx) et retourne le texte nettoyé et normalisé."""
        if not is_zipfile(self.path):
            try:
                with open(self.path, "rb") as f:
                    raw = f.read().decode("latin-1", errors="ignore")
                return self._normalize_text(raw)
            except Exception as e:
                return f"(fichier DOCX invalide : {self.path}, erreur : {e})"

        doc = Document(self.path)
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return self._normalize_text(" ".join(lines))

    def csv_reader(self) -> str:
        """Lit un fichier CSV (séparateur auto-détecté) et retourne le texte nettoyé."""
        df = pd.read_csv(self.path, sep=None, engine="python")
        return self._clean_dataframe(df)

    def xlsx_reader(self) -> str:
        """Lit un fichier Excel (.xlsx) de manière sécurisée, même avec plusieurs feuilles."""
        try:
            xls = pd.ExcelFile(self.path)
            dfs = []
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                if not df.empty:
                    dfs.append(df)
            if not dfs:
                return "(fichier Excel vide)"
            df = pd.concat(dfs, ignore_index=True)
        except Exception as e:
            return f"(erreur lors de la lecture du fichier Excel : {e})"

        return self._clean_dataframe(df)

    # ------------------------------------------------------------
    #  Point d'entrée principal
    # ------------------------------------------------------------
    def read_text_file(self, path: Optional[str] = None) -> str:
        """
        Sélectionne automatiquement le lecteur approprié en fonction de l'extension du fichier.
        
        Args:
            path: Chemin complet vers le fichier à lire.
        
        Returns:
            Texte nettoyé prêt à l’analyse.
        
        Raises:
            Exception: Si aucun chemin n’est fourni.
            ValueError: Si le type de fichier n’est pas pris en charge.
        """
        if path:
            self.path = path
            self.ext, _ = identify_extension(path)
        else:
            raise Exception("Aucun chemin de fichier fourni.")

        if self.ext == ".txt":
            content = self.text_reader()
        elif self.ext == ".json":
            content = self.json_reader()
        elif self.ext == ".csv":
            content = self.csv_reader()
        elif self.ext == ".pdf":
            content = self.pdf_reader()
        elif self.ext == ".docx":
            content = self.docx_reader()
        elif self.ext == ".xlsx":
            content = self.xlsx_reader()
        else:
            raise ValueError(f"Type de fichier non pris en charge : {self.ext}")

        return content
