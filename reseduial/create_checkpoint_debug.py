import zipfile
import os
import datetime

# Configuration
checkpoint_name = "checkpoint_5_visual_meter"
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
archive_name = f"{checkpoint_name}_{timestamp}.zip"
output_dir = "backups"
source_dir = "."

# Ensure output directory exists (create absolute path)
abs_output = os.path.abspath(output_dir)
if not os.path.exists(abs_output):
    os.makedirs(abs_output)

output_path = os.path.join(abs_output, archive_name)

# Exclude list
exclude_dirs = {'.venv', '.git', '__pycache__', 'node_modules', 'backups', 'zip'}
exclude_extensions = {'.pyc', '.pyo', '.pyd', '.mp4', '.7z'}

with open("checkpoint_debug.log", "w") as log:
    log.write(f"Starting backup: {output_path}\n")

    try:
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(source_dir):
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    _, ext = os.path.splitext(file)
                    if ext in exclude_extensions: continue
                    
                    file_path = os.path.join(root, file)
                    arcname = os.path.relpath(file_path, source_dir)
                    
                    if output_dir in file_path: continue
                    if "checkpoint_debug.log" in file: continue

                    log.write(f"Zipping: {arcname}\n")
                    zipf.write(file_path, arcname)

        log.write("Backup complete successfully.\n")
        with open("CHECKPOINT_DONE", "w") as f:
            f.write("done")

    except Exception as e:
        log.write(f"Error: {str(e)}\n")
