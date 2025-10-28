import ollama 
from file_io import read_text_file
import os 

class GemmaAgent(): 
    def __init__(self,paths):
        self.paths = paths
        
    def describe_text_with_gemma(self,paths):
        results = []
        for path in paths:
            name = os.path.basename(path)
            ext = os.path.splitext(path)[1]
            try:
                content = read_text_file(paths)
                response = ollama.chat(
                    model="gemma3:12b",
                    messages=[{
                        "role": "user",
                        "content": "Summarize this text in 1-2 concise English sentences:\n\n" + content
                    }]
                )
                description = response["message"]["content"].strip()
            except Exception as e:
                description = f"Error: {e}"
            results.append({"name": name, "path": path, "description": description, "ext": ext})
        return results

    def describe_images_with_gemma(self,paths):
        results = []
        for path in self.paths:
            name = os.path.basename(path)
            ext = os.path.splitext(path)[1]
            try:
                response = ollama.chat(
                    model="gemma3:12b",
                    messages=[{
                        "role": "user",
                        "content": "Describe this image in 1-2 short natural English sentences.",
                        "images": [path]
                    }]
                )
                description = response["message"]["content"].strip()
            except Exception as e:
                description = f"Error: {e}"
            results.append({"name": name, "path": path, "description": description, "ext": ext})
        return results

    def clean_descriptions_with_gemma(results):
        cleaned = []
        for item in results:
            try:
                response = ollama.chat(
                    model="gemma3:12b",
                    messages=[{
                        "role": "user",
                        "content": (
                            "Clean this short description by removing phrases like "
                            "'this image', 'this document', etc. Keep only the factual description:\n\n"
                            + item["description"]
                        )
                    }]
                )
                item["clean_description"] = response["message"]["content"].strip()
            except Exception as e:
                item["clean_description"] = f"Error cleaning: {e}"
            cleaned.append(item)
        return cleaned

    def generate_filenames_with_gemma(results):
        renamed = []
        for item in results:
            try:
                original_name = os.path.splitext(item["name"])[0]

                response = ollama.chat(
                    model="gemma3:12b",
                    messages=[{
                        "role": "user",
                        "content": (
                            "You will receive a short description and the original file name.\n"
                            "Generate a short descriptive filename (max 6 words) based on both.\n"
                            "Use clues from the original file name if they are meaningful (dates, subjects, etc.).\n"
                            "Keep it natural, relevant, and readable.\n\n"
                            "Rules:\n"
                            "- Use only lowercase letters, numbers, and underscores.\n"
                            "- Do NOT include the file extension.\n"
                            "- Return only the filename text.\n\n"
                            f"Original filename: {original_name}\n\n"
                            f"Description:\n{item.get('clean_description', item.get('description', ''))}"
                        )
                    }]
                )
                item["generated_filename"] = response["message"]["content"].strip()
            except Exception as e:
                item["generated_filename"] = f"Error generating filename: {e}"
            renamed.append(item)
        return renamed
    
   
    
