import os
import json
import pandas as pd
import PyPDF2
from docx import Document
import re
from .utils import identify_extension


class FileReader:
    """
    A robust multi-format file reader that extracts clean, normalized text
    from various file types (.txt, .json, .csv, .xlsx, .pdf, .docx).

    Designed for feeding into LLMs or NLP pipelines:
    - Removes emojis, strange characters, and empty values
    - Normalizes whitespace and formatting
    - Returns a single clean text string
    """

    def __init__(self, path, max_lines=20, remove_emojis=True):
        self.path = path
        self.ext, _ = identify_extension(path)
        self.max_lines = max_lines
        self.remove_emojis = remove_emojis

    # ------------------------------------------------------------
    # 🧹 Text normalization for LLM ingestion
    # ------------------------------------------------------------
    def _normalize_text(self, text: str) -> str:
        """
        Cleans and standardizes raw text:
        - Removes emojis and strange characters
        - Replaces tabs and newlines with spaces
        - Reduces multiple spaces
        - Converts everything to lowercase
        """

        # Remove emojis (optional)
        if self.remove_emojis:
            text = re.sub(r'[\U0001F600-\U0001FAFF]', '', text)

        # Replace newlines and tabs by spaces
        text = text.replace("\n", " ").replace("\t", " ")

        # Keep only alphanumeric characters and basic punctuation
        text = re.sub(r"[^a-zA-Z0-9\s.,;:!?'/\-]", " ", text)

        # Replace multiple spaces by a single one
        text = re.sub(r"\s+", " ", text).strip()

        return text.lower()

    # ------------------------------------------------------------
    # 🧩 Universal DataFrame cleaner (CSV / Excel)
    # ------------------------------------------------------------


    def _clean_dataframe(self, df: pd.DataFrame) -> str:
        # Convertir les noms de colonnes en chaînes pour éviter les erreurs avec .str
        df.columns = df.columns.map(str)

        # Supprimer les colonnes parasites (souvent "Unnamed: 0", etc.)
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

        # Supprimer les lignes où toutes les valeurs sont nulles (NaN, NaT, None, etc.)
        mask_all_null = df.isnull().all(axis=1)
        df = df[~mask_all_null]

        # Remplacer les NaN restants par des chaînes vides et convertir en string
        df = df.fillna("").astype(str)

        # Supprimer les lignes qui ne contiennent que des espaces ou des chaînes vides
        mask_all_empty = df.apply(lambda x: "".join(x).strip() == "", axis=1)
        df = df[~mask_all_empty]

        # Fusionner colonnes + contenu en un seul texte
        text = " ".join(df.columns) + " " + " ".join(
            " ".join(row) for row in df.head(self.max_lines).values.tolist()
        )

        # Nettoyage des mots : garder dates, supprimer nombres
        words = text.split()
        cleaned = []
        for w in words:
            try:
                pd.to_datetime(w, format=None, errors="raise")
                cleaned.append(w)
            except Exception:
                if not w.replace(".", "", 1).isdigit():
                    cleaned.append(w)

        return " ".join(cleaned)


    # ------------------------------------------------------------
    # 📄 Individual file readers
    # ------------------------------------------------------------
    def text_reader(self):
        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()
        return self._normalize_text(text)

    def json_reader(self):
        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            data = json.load(f)
        text = json.dumps(data, indent=2, ensure_ascii=False)
        return self._normalize_text(text)

    def pdf_reader(self):
        lines = []
        with open(self.path, "rb") as f:
            reader = PyPDF2.PdfReader(f)
            for i, page in enumerate(reader.pages):
                raw_text = page.extract_text() or ""
                lines.extend(raw_text.splitlines())
                if len(lines) >= self.max_lines:
                    break
        return self._normalize_text(" ".join(lines))

    def docx_reader(self):
        doc = Document(self.path)
        lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
        return self._normalize_text(" ".join(lines[:self.max_lines]))

    def csv_reader(self):
        df = pd.read_csv(self.path, sep=None, engine="python")  # autodetect separator
        return self._clean_dataframe(df)

    def xlsx_reader(self):
        """
        Reads Excel file safely, even if it has multiple sheets or merged cells.
        """
        try:
            xls = pd.ExcelFile(self.path)
            dfs = []
            for sheet_name in xls.sheet_names:
                df = pd.read_excel(xls, sheet_name=sheet_name, header=None)
                if not df.empty:
                    dfs.append(df)
            if not dfs:
                return "(empty Excel file)"
            df = pd.concat(dfs, ignore_index=True)
        except Exception as e:
            return f"(error reading Excel file: {e})"

        return self._clean_dataframe(df)

    # ------------------------------------------------------------
    # 🧠 Main entry point
    # ------------------------------------------------------------
    def read_text_file(self) -> str:
        """Automatically selects the right reader based on file extension."""
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
            raise ValueError(f"Unsupported file type: {self.ext}")
        return content
