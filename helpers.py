import os
import shutil
from datetime import datetime, timedelta


# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}


def allowed_file(filename):
    """Check if the file has an allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def ensure_directories(directories):
    """Create directories if they don't exist"""
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)


def clean_old_files(config):
    """Remove files older than 24 hours"""
    current_time = datetime.now()

    # Clean results folder
    try:
        for result_id in os.listdir(config['RESULT_FOLDER']):
            result_dir = os.path.join(config['RESULT_FOLDER'], result_id)
            timestamp_file = os.path.join(result_dir, "timestamp.txt")

            if os.path.exists(timestamp_file):
                with open(timestamp_file, "r") as f:
                    timestamp_str = f.read().strip()
                    timestamp = datetime.fromisoformat(timestamp_str)

                if (current_time - timestamp) > timedelta(hours=24):
                    shutil.rmtree(result_dir)
            else:
                # If there is no timestamp file, remove the directory as potentially outdated
                shutil.rmtree(result_dir)
    except Exception as e:
        print(f"Error cleaning results: {str(e)}")

    # Clean uploads folder
    try:
        for filename in os.listdir(config['UPLOAD_FOLDER']):
            filepath = os.path.join(config['UPLOAD_FOLDER'], filename)
            file_modified_time = datetime.fromtimestamp(os.path.getmtime(filepath))

            if (current_time - file_modified_time) > timedelta(hours=24):
                os.remove(filepath)
    except Exception as e:
        print(f"Error cleaning uploads: {str(e)}")