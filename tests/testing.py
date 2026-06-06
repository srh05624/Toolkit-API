import json, sys, os
from pathlib import Path
from fastapi.testclient import TestClient

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from main import aop

SAMPLES_DIR = ROOT_DIR/"samples"

IMAGE_1 = SAMPLES_DIR/"images"/"sample_1.jpg"
IMAGE_2 = SAMPLES_DIR/"images"/"sample_2.png"

PDF_SAMPLE = SAMPLES_DIR/"pdfs"/"sample.pdf"
PDF_1 = SAMPLES_DIR/"pdfs"/"page_1.pdf"
PDF_2 = SAMPLES_DIR/"pdfs"/"page_2.pdf"


client = TestClient(aop)

# ==================================================
#          -- Health testing functions --
# ==================================================
def test_health():
    response = client.get("/health")
    assert response.status_code == 200

# ==================================================
#           -- Image testing functions --
# ==================================================
def test_image_convert():
    with open(IMAGE_1, "rb") as f:
        response = client.post(
            "/images/convert",
            files={"file": ("sample_1.jpg", f, "image/jpeg")},
            data={"target_format": "png"}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_image_resize():
    with open(IMAGE_2, "rb") as f:
        response = client.post(
            "/images/resize",
            files={"file": ("sample_2.png", f, "image/png")},
            data={"width": 100, "height": 100}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_image_rotate():
    with open(IMAGE_1, "rb") as f:
        response = client.post(
            "/images/rotate",
            files={"file": ("sample_2.png", f, "image/jpeg")},
            data={"angle": 90}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

def test_image_compress():
    with open(IMAGE_1, "rb") as f:
        response = client.post(
            "/images/compress",
            files={"file": ("sample_1.jpg", f, "image/jpeg")},
            data={"quality": 50}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/jpeg"

def test_image_watermark():
    with open(IMAGE_2, "rb") as f:
        response = client.post(
            "/images/watermark",
            files={"file": ("sample_2.png", f, "image/png")},
            data={"text": "Test Watermark"}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

def test_image_process():
    with open(IMAGE_2, "rb") as f:
        response = client.post(
            "/images/process",
            files={"file": ("sample_2.png", f, "image/png")},
            data={"operations": json.dumps([
                {"type": "rotate", "params":{"angle": 90}},
                {"type": "resize", "params":{"width": 50, "height": 50}},
                {"type": "watermark", "params":{"text": "Test"}},
                {"type": "compress", "params":{"quality": 30}}
            ])}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

# ==================================================
#            -- PDF Testing functions --
# ==================================================
def test_pdf_merge():
    with open(PDF_1, "rb") as f1, open(PDF_2, "rb") as f2:
        response = client.post(
            "/documents/pdf/merge",
            files=[
                ("files", ("page_1.pdf", f1, "application/pdf")),
                ("files", ("page_2.pdf", f2, "application/pdf")),
            ],
            data={}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/pdf"

def test_pdf_split():
    with open(PDF_SAMPLE, "rb") as f:
        response = client.post(
            "/documents/pdf/split",
            files={"file": ("sample.pdf", f, "application/pdf")},
            data={}
        )

    assert response.status_code == 200
    assert response.headers["content-type"] == "application/zip"

def test_extract_text():
    with open(PDF_SAMPLE, "rb") as f:
        response = client.post(
            "/documents/pdf/extract-text",
            files={"file": ("sample.pdf", f, "application/pdf")},
            data={}
        )

    assert response.status_code == 200
    assert response.headers["content-type"].split(";")[0] == "text/plain"

# ==================================================
#           -- Invalid testing functions --
# ==================================================
def test_invalid_image_operation():
    with open(IMAGE_1, "rb") as f:
        response = client.post(
            "/images/process",
            files={"file": ("sample_1.jpg", f, "image/jpeg")},
            data={"operations": json.dumps([
                {"type": "invalid_operation", "params":{}}
            ])}
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported operation: invalid_operation"

def test_invalid_pdf_operation():
    with open(PDF_SAMPLE, "rb") as f:
        response = client.post(
            "/documents/pdf/invalid_operation",
            files={"file": ("sample.pdf", f, "application/pdf")},
            data={}
        )

    assert response.status_code == 404

def test_invalid_file_size():
    # Create a dummy file larger than 10MB
    large_file_path = SAMPLES_DIR/"large_file.png"
    with open(large_file_path, "wb") as f:
        f.seek((10 * 1024 * 1024) + 1)  # Seek to 10MB + 1 byte
        f.write(b"\0")  # Write a null byte to create the file

    with open(large_file_path, "rb") as f:
        response = client.post(
            "/images/convert",
            files={"file": ("large_file.png", f, "image/png")},
            data={"target_format": "png"}
        )

    assert response.status_code == 413
    assert response.json()["detail"] == "File size exceeds the maximum limit of 10MB"

    # Clean up the large file after testing
    os.remove(large_file_path)