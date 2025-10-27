import docx 
import os 

### FILE READER ###

class FileReader(): 
    
    def __init__(self,path,max_lines=20): 
        self.path = path 
        _ , self.ext = os.path.splitext()
        self.max_lines = max_lines
        
    def text_reader(self):
        lines = []
        with open(self.path, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                clean_line = line.strip()
                if not clean_line:
                    continue  # skip the empty lines
                lines.append(clean_line)
                if len(lines) >= self.max_lines:  # only counts the non empty lines
                    break
        return "\n".join(lines)

        
    def json_reader(self): 
        import json 
        with open(self.path, "r", encoding = "utf-8", errors="ignore") as f: 
            data = json.load(f)
        json_str = json.dumps(data,indent=2) # we convert the json as a string
        lines = json_str.splitlines()  # we split the returned string as a list.
        return "\n".join(lines[:self.max_lines]) # we join the list and returns everything until max_lines
            
    def csv_reader(self): 
        import csv 
        lines = []
        with open (self.path,"r" , encoding="utf-8", errors="ignore") as f: 
            reader = csv.reader(f)
            for i , row in enumerate (reader): # iterate on the lines (i = index , row = values of this line)
                lines.append (", ".join(row)) # transform the list in chain separated with commas. 
                if i >= 20: # we only get the 20 first lines 
                    break
                return "\n".join(lines)
            
    def pdf_reader(self): 
        import PyPDF2 
        text = "" 
        with open(self.path , "rb") as f: 
            reader = PyPDF2.PdfReader(f)
            for i , page in enumerate(reader.pages): 
                text += page.extract_text() or "" 
                if i + 1 >= self.max_lines: 
                    break 
        return text 
                
    def docx_reader(self): 
        from docx import Document
        lines = []
        doc = Document(self.path) 
        for para in doc.paragraphs: 
            text = para.text.strip() 
            if not text: 
                continue 
            lines.append(text) 
            if len(lines) >= self.max_lines: 
                break
            return "\n".join(lines) 
        
    def excel_reader(self):
        import openpyxl 
        lines = []
        workbook = openpyxl.load_workbook(self.path , read_only=True)
        sheet = workbook.active 
        # read the first line as header
        header_row = next(sheet.iter_rows(values_only=True))
        if header_row and any(header_row):
            header = ", ".join(str(cell) for cell in header_row if cell is not None)
            lines.append(f"[Columns] {header}")
        else: 
            lines.append("")
            
        # read the next lines
        count = 0 
        # for row in sheet.iter_rows(values_only=True , min_row=2)  #starts at line 2 
            
            
            