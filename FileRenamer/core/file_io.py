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
        """Cleans and standardizes raw text for LLM processing."""

        # Optional emoji removal
        if self.remove_emojis:
            emoji_pattern = re.compile("["
                u"\U0001F600-\U0001F64F"  # emoticons
                u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                u"\U0001F680-\U0001F6FF"  # transport & map symbols
                u"\U0001F1E0-\U0001F1FF"  # flags
                "]+", flags=re.UNICODE)
            text = emoji_pattern.sub('', text)

        # Remove weird characters, tabs, and excessive spaces
        text = re.sub(r"[^\w\s.,;:!?\'\"()\-/%]+", " ", text)
        text = text.replace("\n", " ").replace("\t", " ")
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        # Convert to lowercase for consistency
        return text.lower()

    # ------------------------------------------------------------
    # 🧩 Universal DataFrame cleaner (CSV / Excel)
    # ------------------------------------------------------------
    def _clean_dataframe(self, df: pd.DataFrame) -> str:
        """
        Cleans and flattens tabular data for semantic LLM ingestion:
        - Keeps textual and date-like content
        - Removes numeric noise (isolated numbers, floats)
        - Avoids duplicates while preserving order
        """

        # Drop "Unnamed" columns (Excel artifacts)
        df = df.loc[:, ~df.columns.astype(str).str.contains('^Unnamed', case=False)]

        # Replace missing values safely
        df = df.replace({pd.NA: "", "NaT": "", "nan": "", "None": "", None: ""}).fillna("")
        df = df.astype(str)

        # Keep non-empty rows
        df = df[df.apply(lambda row: any(cell.strip() for cell in row), axis=1)]
        if df.empty:
            return "(empty table)"

        # Build text content
        headers = [str(c).strip() for c in df.columns if str(c).strip() and not str(c).startswith("Unnamed")]
        lines = []
        for _, row in df.head(self.max_lines).iterrows():
            cells = [cell.strip() for cell in row if cell.strip()]
            lines.append(" ".join(cells))

        text = " ".join(headers + lines)

        # ✅ Keep dates but remove isolated numbers (not part of a date)
        # Keep things like 2023-10-09, 10/02/2024, 2024.03.15
        text = re.sub(r"\b(?<!\d)(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})(?!\d)\b", lambda m: f" {m.group(0)} ", text)
        # Remove remaining pure numbers and floats
        text = re.sub(r"\b\d+(\.\d+)?\b", " ", text)

        # Normalize spacing and punctuation
        text = self._normalize_text(text)

        # Remove duplicates while preserving order
        seen = set()
        words = []
        for word in text.split():
            if word not in seen:
                seen.add(word)
                words.append(word)

        cleaned_text = " ".join(words)
        return cleaned_text

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
