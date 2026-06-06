import io, zipfile
from scripts.utils import Logger
from pypdf import PdfReader, PdfWriter
LOGGER = Logger("Documents")

# ==================================================
#               -- PDF processing --
# ==================================================
def split_pdf(file, password: str | None = None, pages: list[int] | None = None):
    try:
        if not isinstance(file, io.BytesIO):
            file = io.BytesIO(file.read())

        reader = PdfReader(file)

        if password:
            reader.decrypt(password)

        page_numbers = range(len(reader.pages)) if pages is None else pages
        
        output_files = []
        names = []

        for i in page_numbers:
            writer = PdfWriter()
            writer.add_page(reader.pages[i])
            buffer = io.BytesIO()
            writer.write(buffer)
            buffer.seek(0)
            output_files.append(buffer)
            names.append(f"page_{i+1}.pdf")
        
        return output_files
    except Exception as e:
        LOGGER.error(f"Error splitting PDF: {e}")
        return None
    
def merge_pdfs(files, password: str | None = None):
    try:
        writer = PdfWriter()

        for file in files:
            if not isinstance(file, io.BytesIO):
                file = io.BytesIO(file.read())

            reader = PdfReader(file)

            for page in reader.pages:
                writer.add_page(page)

            if password:
                writer.encrypt(password)

        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)

        return output_buffer
    except Exception as e:
        LOGGER.error(f"Error merging PDFs: {e}")
        return None
    
def extract_text(file, password: str | None = None):
    try:
        if not isinstance(file, io.BytesIO):
            file = io.BytesIO(file.read())

        reader = PdfReader(file)

        if password:
            reader.decrypt(password)

        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"
        
        buffer = io.BytesIO(text.encode("utf-8"))
        buffer.seek(0)

        return buffer
    except Exception as e:
        LOGGER.error(f"Error extracting text from PDF: {e}")
        return None

PDF_SINGLE_PROCESSES = {
    "split": split_pdf,
    "extract_text": extract_text
}

PDF_MULTI_PROCESSES = {
    "merge": merge_pdfs
}

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt"
}