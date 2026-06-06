import os, sys, json
from datetime import datetime
from scripts.logger import Logger

LOGGER = Logger("Utils")

# ==================================================
#               -- File Utilities --
# ==================================================
def file_exists(file_path):
    try:
        return os.path.isfile(file_path)
    except OSError as e:
        LOGGER.error(f"Error checking file: {file_path} - {str(e)}")
        return False
    finally:
        LOGGER.debug(f"Checked file: {file_path}")

def dir_exists(dir_path):
    try:
        return os.path.isdir(dir_path)
    except OSError as e:
        LOGGER.error(f"Error checking directory: {dir_path} - {str(e)}")
        return False
    finally:
        LOGGER.debug(f"Checked directory: {dir_path}")

def create_dir(dir_path):
    try:
        os.makedirs(dir_path, exist_ok=True)
    except OSError as e:
        LOGGER.error(f"Error creating directory: {dir_path} - {str(e)}")
    finally:
        LOGGER.info(f"Directory created: {dir_path}")

def read_file(file_path):
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except IOError as e:
        LOGGER.error(f"Error reading file: {file_path} - {str(e)}")
    finally:
        LOGGER.info(f"File read: {file_path}")
    
def write_file(file_path, content):
    try:
        with open(file_path, 'w') as f:
            f.write(content)
    except IOError as e:
        LOGGER.error(f"Error writing file: {file_path} - {str(e)}")
    finally:
        LOGGER.info(f"File written: {file_path}")

# ==================================================
#               -- JSON Utilities --
# ==================================================
def read_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        LOGGER.error(f"Error reading JSON file: {file_path} - {str(e)}")
        return None
    finally:
        LOGGER.info(f"JSON file read: {file_path}")

def write_json(file_path, data):
    try:
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=4)
    except TypeError as e:
        LOGGER.error(f"Error writing JSON file: {file_path} - {str(e)}")
    finally:
        LOGGER.info(f"JSON file written: {file_path}")

