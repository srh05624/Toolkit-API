import io, zipfile
from scripts.utils import Logger

LOGGER = Logger("Compression")

# ==================================================
#             -- Basic File compression --
# ==================================================
def zip_files(files: list[io.BytesIO], names=None, arcname=None):
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for i, file in enumerate(files):
                if not isinstance(file, io.BytesIO):
                    file = io.BytesIO(file.read())
                file.seek(0)
                zip_file.writestr(names[i] if names and i < len(names) else f"file_{i+1}.{arcname if arcname else 'bin'}", file.getvalue())
        buffer.seek(0)
        return buffer
    except Exception as e:
        LOGGER.error(f"Error creating ZIP file: {e}")
        return None

def zip_file(file: io.BytesIO, name=None):
    try:
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            if not isinstance(file, io.BytesIO):
                file = io.BytesIO(file.read())
            file.seek(0)
            zip_file.writestr(name if name else "file.zip", file.getvalue())
        buffer.seek(0)
        return buffer
    except Exception as e:
        LOGGER.error(f"Error creating ZIP file: {e}")
        return None