"""OCR processing module. Images -> Tesseract; PDFs -> embedded text first, then OCR of rendered pages."""
from pathlib import Path


class OCRUnavailable(Exception):
    """OCR engine (Tesseract / poppler) is not installed or failed."""


def extract_text(path: str, file_type: str) -> str:
    try:
        if file_type == "pdf":
            return _pdf_text(path)
        return _image_text(path)
    except OCRUnavailable:
        raise
    except Exception as exc:  # corrupt file, missing binary, etc.
        raise OCRUnavailable(f"OCR failed: {exc}") from exc


def _image_text(path: str) -> str:
    import pytesseract
    from PIL import Image
    with Image.open(path) as img:
        return pytesseract.image_to_string(img)


def _pdf_text(path: str) -> str:
    from pypdf import PdfReader
    text = "\n".join((page.extract_text() or "") for page in PdfReader(path).pages)
    if text.strip():
        return text
    # scanned PDF: render pages and OCR them
    import pytesseract
    from pdf2image import convert_from_path
    return "\n".join(pytesseract.image_to_string(img) for img in convert_from_path(path))
