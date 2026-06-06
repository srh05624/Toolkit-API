## Toolkit - API

A FastAPI-based toolkit for image and PDF processing.

The API performs all operations in memory and returns the processed file directly to the client.

---

## Key Features

✓ Automated API Tests

---

## Features:

### Image Processing
- Convert Image format to another format
- Resize Images to desired width and height
- Rotate Image by desired angle
- Compress Image to desired Quality
- Add a text watermark to Image

### PDF Processing
- Split PDF file into each page
- Merge PDF files together
- Extract all text from PDF file

---

## Project Structure

    Toolkit-API/
    ├── modules/
    │   ├── compression.py
    │   ├── documents.py
    │   └── images.py
    │
    ├── samples/
    │   ├── pdfs/
    │   │   ├── page_1.pdf
    │   │   ├── page_2.pdf
    │   │   ├── page_3.pdf
    │   │   ├── page_4.pdf
    │   │   ├── page_5.pdf
    │   │   ├── page_6.pdf
    │   │   ├── page_7.pdf
    │   │   ├── page_8.pdf
    │   │   └── sample.pdf
    │   │
    │   └── images/
    │       ├── sample_1.jpg
    │       └── sample_2.png
    │
    ├── tests/
    │   └── testing.py
    │
    ├── main.py
    ├── requirements.txt
    └── README.md

---

## Safety features:
- The Middleware detects any files over the limit (Default 10Mb)
- The API avoids processing files over the limit (Default 10Mb)
- The API only accepts files in the list of accepted formats.

### Allowed File Extensions:
- jpeg
- jpg
- png
- bmp
- gif
- tiff
- pdf
  
---

## Technologies Used:
- Python 3
- FastAPI
- Pydantic
- Starlette Middleware
- pytest
- Pillow
- PyPDF2
  
---

## Installation Steps:

### Method 1: (Python)
1) Clone Repository
```bash
git clone https://github.com/srh05624/Toolkit-API.git
cd Toolkit-API
```

2) Install Dependencies (Generated via pipreqs)

```bash
pip install -r requirements.txt
```

3) Run Application

```bash
python main.py
```

---

## API Documentation

Once the server is running, FastAPI automatically generates interactive API documentation.

### Swagger UI

```text
http://localhost:8000/docs
```

Swagger UI allows you to:
- View all available endpoints
- Inspect request parameters
- Upload files directly from the browser
- Execute requests without writing code
- View API responses

### ReDoc

```text
http://localhost:8000/redoc
```

Alternative documentation view generated automatically by FastAPI.

---

## Available Endpoints

### Images

| Method | Endpoint |
|----------|----------|
| POST | /images/convert |
| POST | /images/resize |
| POST | /images/rotate |
| POST | /images/compress |
| POST | /images/watermark |
| POST | /images/process |

### Documents

| Method | Endpoint |
|----------|----------|
| POST | /documents/pdf/split |
| POST | /documents/pdf/merge |
| POST | /documents/pdf/extract_text |

### Utility

| Method | Endpoint |
|----------|----------|
| GET | /health |

---

## Example Multi-Step Processing

```json
[
    {
        "type": "convert",
        "params": {
            "target_format": "png"
        }
    },
    {
        "type": "watermark",
        "params": {
            "watermark_text": "Toolkit API"
        }
    }
]
```

---

## Running Tests

```bash
python -m pytest tests/testing.py
```
---

## Live Demo

https://toolkit-api-ct6k.onrender.com

Note: The public demo is hosted on Render's free tier and may take a short time to wake up after periods of inactivity.

---

## Author

Samuel Rodriguez
