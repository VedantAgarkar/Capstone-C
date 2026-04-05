
import os
import zipfile

files_to_zip = [
    'frontend', 
    'backend', 
    'requirements.txt', 
    '.env', 
    'README.md',
    'diabetes.csv',
    'heart.csv',
    'parkinsons.csv'
]

output_filename = 'updated_v2.zip'

print(f"Creating {output_filename}...")
with zipfile.ZipFile(output_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for item in files_to_zip:
        if os.path.isfile(item):
            print(f"Adding file: {item}")
            zipf.write(item)
        elif os.path.isdir(item):
            print(f"Adding folder: {item}")
            for root, dirs, files in os.walk(item):
                if '__pycache__' in dirs:
                    dirs.remove('__pycache__')
                
                for file in files:
                    # Skip .pyc and .bak files
                    if file.endswith('.pyc') or file.endswith('.bak'):
                        continue
                        
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, os.getcwd())
                    zipf.write(file_path, rel_path)

print(f"Done! Created {output_filename}")
