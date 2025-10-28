import os 
import shutil 

def upload_files(uploaded_files:list , TEMP_DIR:str ="uploaded_temp") -> list :
    """
    Uploads streamlit files to a TEMP_DIR 
    """
    file_paths = []

    os.makedirs(TEMP_DIR , exist_ok=True)
    
    for f in uploaded_files: 
        save_path = os.path.join(TEMP_DIR , f.name)
        with open(save_path,"wb") as out: 
            out.write(f.read()) 
        file_paths.append(save_path)
            
        
    return file_paths 

def clear_temp_dir(TEMP_DIR: str ="uploaded_temp") -> None : 
    """
    Clears uploaded files from TEMP_DIR 
    """
    if os.path.exists(TEMP_DIR): 
        shutil.rmtree(TEMP_DIR)
        os.makedirs(TEMP_DIR)