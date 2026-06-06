import io
from PIL import Image, ImageDraw, ImageFont

def convert(file, target_format: str, file_format: str | None = None):
    try:
        if isinstance(file, bytes):
            file = io.BytesIO(file)
        
        with Image.open(file) as img:
            if img.mode in ("RGBA", "LA", "P") and target_format.lower() in ["jpeg", "jpg"]:
                img = img.convert("RGB")

            buffer = io.BytesIO()
            format = "JPEG" if target_format.upper() in ["JPEG", "JPG"] else target_format.upper()
            img.save(buffer, format=format)

            buffer.seek(0)

            return buffer, format
        
    except Exception:
        return None, None

def resize(file, width: int, height: int, file_format: str | None = None):
    try:
        if isinstance(file, bytes):
            file = io.BytesIO(file)

        with Image.open(file) as img:
            img = img.resize((width, height))

            buffer = io.BytesIO()

            if file_format:
                img.save(buffer, format=file_format)
            else:
                img.save(buffer, format="JPEG")

            buffer.seek(0)

            return buffer, file_format if file_format else "JPEG"
    except Exception:
        return None, None
    
def rotate(file, angle: float, file_format: str | None = None):
    try:
        if isinstance(file, bytes):
            file = io.BytesIO(file)

        with Image.open(file) as img:
            img = img.rotate(angle, expand=True, fillcolor=(0, 0, 0, 0))

            buffer = io.BytesIO()

            if file_format:
                img.save(buffer, format=file_format)
            else:
                img.save(buffer, format="JPEG")

            buffer.seek(0)

            return buffer, file_format if file_format else "JPEG"
    except Exception:
        return None, None
    
def compress(file, quality: int, file_format: str | None = None):
    try:
        if isinstance(file, bytes):
            file = io.BytesIO(file)

        with Image.open(file) as img:
            buffer = io.BytesIO()
            
            if file_format:
                img.save(buffer, format=file_format, quality=quality)
            else:
                img.save(buffer, format="JPEG", quality=quality)

            buffer.seek(0)

            return buffer, file_format if file_format else "JPEG"
    except Exception:
        return None, None
    
def watermark(file, text: str, file_format: str | None = None):
    try:
        if isinstance(file, bytes):
            file = io.BytesIO(file)

        with Image.open(file) as img:
            watermark = Image.new("RGBA", img.size)
            watermark_draw = ImageDraw.Draw(watermark)
            font_size = min(img.size) // 10
            font = ImageFont.truetype("arial.ttf", font_size)
            left, top, right, bottom = watermark_draw.textbbox(xy=(0, 0), text=text, font=font)
            text_width = right - left
            text_height = bottom - top
            position = ((img.size[0] - text_width) // 2, (img.size[1] - text_height) // 2)
            watermark_draw.text(position, text, font=font, fill=(255, 255, 255, 128))

            watermarked = Image.alpha_composite(img.convert("RGBA"), watermark)

            buffer = io.BytesIO()

            if file_format:
                watermarked.save(buffer, format=file_format)
            else:
                watermarked.save(buffer, format="PNG")

            buffer.seek(0)

            return buffer, file_format if file_format else "PNG"
    except Exception:
        return None, None
    
PROCESSES = {
    "convert": convert,
    "resize": resize,
    "rotate": rotate,
    "compress": compress,
    "watermark": watermark
}

ALLOWED_EXTENSIONS = {
    "jpeg",
    "jpg",
    "png",
    "bmp",
    "gif",
    "tiff"
}