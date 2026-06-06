import uvicorn, json
from fastapi import FastAPI, Request, UploadFile, HTTPException, File, Form
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from modules import images, documents, compression

aop = FastAPI(
    title="Toolkit API",
    description="Image and PDF processing toolkit built with FastAPI.",
    version="1.0.0"
)

size_limit = 10485760 # 10 MB (10 * 1024 * 1024)

MEDIA_TYPES = {
    "pdf": "application/pdf",
    "txt": "text/plain",
    "zip": "application/zip",
    "png": "image/png",
    "jpg": "image/jpeg",
    "jpeg": "image/jpeg",
    "webp": "image/webp",
}

class LimitUploadSize(BaseHTTPMiddleware):
    def __init__(self, app, max_upload_size: int):
        super().__init__(app)
        self.max_upload_size = max_upload_size

    async def dispatch(self, request: Request, call_next):
        content_length = request.headers.get("content-length")

        if (
            request.method == "POST"
            and content_length
            and int(content_length) > self.max_upload_size
        ):
            return JSONResponse(
                status_code=413,
                content={"detail": "File size exceeds the maximum limit of 10MB"}
            )

        return await call_next(request)

# Example: Apply a 10 MB limit
aop.add_middleware(LimitUploadSize, max_upload_size=size_limit)

class Operation(BaseModel):
    type: str
    params: dict = {}

def is_file_too_large(file) -> bool:
    file.seek(0, 2)
    size = file.tell()
    file.seek(0)
    return size > size_limit

def get_file_size(file) -> int:
    current_pos = file.tell()
    file.seek(0, 2)
    size = file.tell()
    file.seek(current_pos)
    return size

def zip_response(file_buffer, file_format, zip_filename):
    if file_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="No file to compress"
        )

    if isinstance(file_buffer, list):
        zip_buffer = compression.zip_files(file_buffer, arcname=file_format)
    else:
        zip_buffer = compression.zip_file(file_buffer, zip_filename)

    if zip_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error compressing file into ZIP"
        )

    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename={zip_filename}"}
    )

def buffer_response(file_buffer, file_format, filename):
    if file_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error processing file"
        )

    file_format = file_format.lower()

    if not filename.endswith(f".{file_format}"):
        filename += f".{file_format}"

    file_buffer.seek(0)

    if is_file_too_large(file_buffer):
        response = zip_response(
            file_buffer,
            file_format=file_format,
            zip_filename=f"{filename}.zip"
        )
        return response
    
    media_type = MEDIA_TYPES.get(
        file_format.lower(),
        "application/octet-stream"
    )

    return StreamingResponse(
        file_buffer,
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

# ==================================================
#              -- Image processing --
# ==================================================
@aop.post(
        "/images/convert",
        summary="Convert an image to a different format",
        description="Convert an uploaded image to a specified format (e.g., PNG, JPEG, WEBP). The original image format is detected automatically. Supported formats include PNG, JPEG, and WEBP.",
        tags=["Images"]
    )
async def convert_image(
    file: UploadFile = File(...),
    target_format: str = Form(...)
):
    if is_file_too_large(file.file):
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the maximum limit of 10MB"
        )
    
    file_format = file.content_type.split("/")[-1].upper()
    img = file.file

    img_buffer, file_format = images.convert(img, target_format=target_format, file_format=file_format)

    if img_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error converting image"
        )

    return buffer_response(img_buffer, file_format, "converted")

@aop.post(
        "/images/resize",
        summary="Resize an image to specified dimensions",
        description="Resize an uploaded image to the specified width and height. The original image format is detected automatically and preserved in the output. Supported formats include PNG, JPEG, and WEBP.",
        tags=["Images"]
    )
async def resize_image(
    file: UploadFile = File(...),
    width: int = Form(..., ge=1),
    height: int = Form(..., ge=1)
):
    if is_file_too_large(file.file):
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the maximum limit of 10MB"
        )

    file_format = file.content_type.split("/")[-1].upper()
    img = file.file

    img_buffer, file_format = images.resize(img, width, height, file_format=file_format)

    if img_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error converting image"
        )
    
    return buffer_response(img_buffer, file_format, "resized")

@aop.post(
        "/images/rotate",
        summary="Rotate an image by a specified angle",
        description="Rotate an uploaded image by the specified angle in degrees. The original image format is detected automatically and preserved in the output. Supported formats include PNG, JPEG, and WEBP.",
        tags=["Images"]
    )
async def rotate_image(
    file: UploadFile = File(...),
    angle: float | int = Form(...)
):
    if is_file_too_large(file.file):
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the maximum limit of 10MB"
        )

    file_format = file.content_type.split("/")[-1].upper()
    img = file.file

    img_buffer, file_format = images.rotate(img, angle, file_format=file_format)

    if img_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error converting image"
        )

    return buffer_response(img_buffer, file_format, "rotated")

@aop.post(
        "/images/compress",
        summary="Compress an image to reduce its file size",
        description="Compress an uploaded image by specifying the quality level (1-100). The original image format is detected automatically and preserved in the output. Supported formats include PNG, JPEG, and WEBP.",
        tags=["Images"]
    )
async def compress_image(
    file: UploadFile = File(...),
    quality: int = Form(..., ge=1, le=100)
):
    if is_file_too_large(file.file):
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the maximum limit of 10MB"
        )

    file_format = file.content_type.split("/")[-1].upper()
    img = file.file

    img_buffer, file_format = images.compress(img, quality, file_format=file_format)

    if img_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error converting image"
        )

    return buffer_response(img_buffer, file_format, "compressed")

@aop.post(
        "/images/watermark",
        summary="Add a text watermark to an image",
        description="Add a text watermark to an uploaded image. The original image format is detected automatically and preserved in the output. Supported formats include PNG, JPEG, and WEBP.",
        tags=["Images"]
    )
async def watermark_image(
    file: UploadFile = File(...),
    text: str = Form(...)
):
    if is_file_too_large(file.file):
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the maximum limit of 10MB"
        )

    file_format = file.content_type.split("/")[-1].upper()
    img = file.file

    img_buffer, file_format = images.watermark(img, text, file_format=file_format)

    if img_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error converting image"
        )

    return buffer_response(img_buffer, file_format, "watermarked")

@aop.post(
        "/images/process",
        summary="Apply multiple operations to an image in sequence",
        description="Apply a sequence of operations (e.g., resize, rotate, compress) to an uploaded image. The operations are specified in a JSON array, and the original image format is detected automatically and preserved in the output. Supported formats include PNG, JPEG, and WEBP.",
        tags=["Images"]
    )
async def process_image(
    file: UploadFile = File(...),
    operations: str = Form(...)
):
    if is_file_too_large(file.file):
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the maximum limit of 10MB"
        )

    try:
        operation_list = [Operation(**op) for op in json.loads(operations)]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid operations JSON")
    
    img_buffer = file.file
    file_format = file.content_type.split("/")[-1].upper()

    for operation in operation_list:
        if operation.type not in images.PROCESSES:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported operation: {operation.type}"
            )
        
        try:
            img_buffer, file_format = images.PROCESSES[operation.type](
                img_buffer, 
                **operation.params,
                file_format=file_format
            )
        except TypeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid parameters for operation {operation.type}: {str(e)}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error processing image with operation {operation.type}: {str(e)}"
            )

    if img_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error converting image"
        )

    return buffer_response(img_buffer, file_format, "processed")

# ==================================================
#             -- Document processing --
# ==================================================
@aop.post(
        "/documents/pdf/split",
        summary="Split a PDF into separate pages",
        description="Split an uploaded PDF document into separate pages. You can specify a password if the PDF is encrypted, and optionally specify which pages to split (e.g., '1,3,5' to split pages 1, 3, and 5). The output will be a ZIP file containing the individual page PDFs.",
        tags=["PDF"]
    )
async def split_document(
    file: UploadFile = File(...),
    password: str | None = Form(""),
    pages: str | None = Form("")
):
    if is_file_too_large(file.file):
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the maximum limit of 10MB"
        )

    page_numbers = [int(p.strip()) for p in pages.split(",") if p.strip().isdigit()] if pages else None

    files_buffer = documents.split_pdf(file.file, password=password, pages=page_numbers)
    filename = "split_files"

    if files_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error splitting PDF"
        )

    return zip_response(files_buffer, filename, "pdf")

@aop.post(
        "/documents/pdf/merge",
        summary="Merge multiple PDF documents into one",
        description="Merge multiple uploaded PDF documents into a single PDF. You can specify a password if the PDFs are encrypted.",
        tags=["PDF"]
    )
async def merge_documents(
    files: list[UploadFile] = File(...),
    password: str | None = Form("")
):
    total_size = 0

    for f in files:
        file_size = get_file_size(f.file)
        if file_size > size_limit:
            raise HTTPException(
                status_code=413,
                detail=f"File {f.filename} too large"
            )

        total_size += file_size

    if total_size > size_limit:
        raise HTTPException(
            status_code=413,
            detail="Total file size exceeds limit"
        )

    file_buffer = documents.merge_pdfs([f.file for f in files], password=password)

    if file_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error merging PDFs"
        )

    return buffer_response(file_buffer, "pdf", "merged")

@aop.post(
        "/documents/pdf/extract-text",
        summary="Extract text from a PDF document",
        description="Extract text from an uploaded PDF document. You can specify a password if the PDF is encrypted.",
        tags=["PDF"]
    )
async def extract_text(
    file: UploadFile = File(...),
    password: str | None = Form("")
):
    if is_file_too_large(file.file):
        raise HTTPException(
            status_code=413,
            detail="File size exceeds the maximum limit of 10MB"
        )

    text_buffer = documents.extract_text(file.file, password=password)

    if text_buffer is None:
        raise HTTPException(
            status_code=500,
            detail="Error extracting text from PDF"
        )

    return buffer_response(text_buffer, "txt", "extracted_text")

# ==================================================
#                -- Health Check --
# ==================================================
@aop.get(
        "/health",
        summary="Health check endpoint",
        description="Check the health status of the API",
        tags=["Utility"]
    )
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    uvicorn.run(aop, host="0.0.0.0", port=8000)