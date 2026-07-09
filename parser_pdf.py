from __future__ import annotations

import io
from typing import List, Tuple
from PIL import Image
import fitz  # PyMuPDF


def pdf_to_page_images(pdf_bytes: bytes, max_pages: int = 12, dpi: int = 180) -> List[Tuple[str, bytes]]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images: List[Tuple[str, bytes]] = []

    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)

    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img_bytes = pix.tobytes("png")
        images.append((f"page_{i+1}.png", img_bytes))

    doc.close()
    return images


def image_file_to_png_bytes(file_bytes: bytes) -> bytes:
    with Image.open(io.BytesIO(file_bytes)) as img:
        img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()
