import zipfile
import os
import datetime

# Configuration
checkpoint_name = "checkpoint_1"
timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
archive_name = f"{checkpoint_name}_{timestamp}.zip"
output_dir = "backups"
source_dir = "."

# Ensure output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

output_path = os.path.join(output_dir, archive_name)

# Exclude list
exclude_dirs = {'.venv', '.git', '__pycache__', 'node_modules', 'backups', 'zip'}
exclude_extensions = {'.pyc', '.pyo', '.pyd', '.mp4', '.7z'} # Exclude large media files to save space/time

print(f"Starting backup: {output_path}")

try:
    with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_dir):
            # filter directories
            dirs[:] = [d for d in dirs if d not in exclude_dirs]
            
            for file in files:
                # filter files
                _, ext = os.path.splitext(file)
                if ext in exclude_extensions:
                    continue
                
                file_path = os.path.join(root, file)
                # calculate archive name
                arcname = os.path.relpath(file_path, source_dir)
                
                # avoid recursively zipping the backup itself or other backups
                if output_dir in file_path:
                    continue
                    
                print(f"Adding: {arcname}")
                zipf.write(file_path, arcname)

    print(f"Backup successfully created at: {output_path}")

except Exception as e:
    print(f"Error creating backup: {e}")
