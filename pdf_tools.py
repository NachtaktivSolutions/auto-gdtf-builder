from __future__ import annotations

import io
from typing import List, Tuple

import fitz
from PIL import Image


def extract_pdf_text(pdf_bytes: bytes, max_pages: int = 40, max_chars: int = 80000) -> str:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    chunks = []
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        text = page.get_text("text") or ""
        if text.strip():
            chunks.append(f"--- PAGE {i+1} ---\n{text}")
    doc.close()
    combined = "\n\n".join(chunks).strip()
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n\n[TRUNCATED]"
    return combined


def pdf_to_page_images(pdf_bytes: bytes, max_pages: int = 9, dpi: int = 120) -> List[Tuple[str, bytes]]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images = []
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        pix = page.get_pixmap(matrix=mat, alpha=False)
        images.append((f"page_{i+1}.png", pix.tobytes("png")))
    doc.close()
    return images


def image_to_png_bytes(file_bytes: bytes) -> bytes:
    with Image.open(io.BytesIO(file_bytes)) as img:
        img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
