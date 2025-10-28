import os 

def identify_extension(path:str) -> tuple :
    _ , ext = os.path.splitext(path)
    if ext in [".png" , ".jpg" , ".bmp" , ".tiff"]:
        filetype = "image"
    if ext in [".txt" , ".docx" , ".pdf" , ".csv" , ".xlsx" , ".json"]:
        filetype = "text"
    else: 
        filetype = "unknown"
    return ext.lower() , filetype

def check_gemma_response(self): 
    pass 