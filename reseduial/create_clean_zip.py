
import os
import zipfile

# Define the files and folders to include
BASE_DIR = os.getcwd()

# Whitelist of files/folders
FILES_TO_INCLUDE = [
    # Root level
    "requirements.txt",
    ".env",
    "README.md",
    
    # Backend (Python/Streamlit)
    os.path.join("backend", "routes"), 
    os.path.join("backend", "models"),
    os.path.join("backend", "utils.py"),
    os.path.join("backend", "main.py"),
    
    # ML Models (Important!)
    os.path.join("backend", "diabetes_model.sav"),
    os.path.join("backend", "diabetes_scaler.sav"),
    os.path.join("backend", "heart_disease_model.sav"),
    os.path.join("backend", "heart_scaler.sav"),
    os.path.join("backend", "parkinsons_model.sav"),
    os.path.join("backend", "parkinsons_scaler.sav"),

    # Frontend (HTML/JS/CSS)
    "frontend" 
]

OUTPUT_ZIP = "updated.zip"

def main():
    print(f"Creating {OUTPUT_ZIP}...")
    with zipfile.ZipFile(OUTPUT_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for item in FILES_TO_INCLUDE:
            path = os.path.join(BASE_DIR, item)
            
            if os.path.isfile(path):
                # Write file directly
                print(f"Adding file: {item}")
                zipf.write(path, arcname=item)
            elif os.path.isdir(path):
                # Walk through directory
                print(f"Adding folder: {item}")
                for root, dirs, files in os.walk(path):
                    # Skip __pycache__ and other hidden junk
                    dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
                    
                    for file in files:
                        if file.endswith('.pyc') or file.endswith('.bak'):
                            continue
                            
                        file_path = os.path.join(root, file)
                        # Relative path for the zip archive
                        rel_path = os.path.relpath(file_path, BASE_DIR)
                        print(f"  -> {rel_path}")
                        zipf.write(file_path, arcname=rel_path)
            else:
                print(f"⚠️ Warning: {item} not found, skipping.")

    print(f"\n✅ Successfully created {OUTPUT_ZIP}")

if __name__ == "__main__":
    main()
