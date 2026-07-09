from __future__ import annotations

import io
from typing import List, Tuple

import fitz
import numpy as np
from PIL import Image
from rapidocr_onnxruntime import RapidOCR


_ocr_engine = None


def get_ocr_engine():
    global _ocr_engine
    if _ocr_engine is None:
        _ocr_engine = RapidOCR()
    return _ocr_engine


def pdf_to_page_images(pdf_bytes: bytes, max_pages: int = 12, dpi: int = 180) -> List[Tuple[str, bytes]]:
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    images: List[Tuple[str, bytes]] = []
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    for i, page in enumerate(doc):
        if i >= max_pages:
            break
        pix = page.get_pixmap(matrix=mat, alpha=False)
        images.append((f"page_{i+1}.png", pix.tobytes("png")))
    doc.close()
    return images


def image_file_to_png_bytes(file_bytes: bytes) -> bytes:
    with Image.open(io.BytesIO(file_bytes)) as img:
        img = img.convert("RGB")
        out = io.BytesIO()
        img.save(out, format="PNG")
        return out.getvalue()


def prepare_images(uploaded_file, max_pages: int) -> List[Tuple[str, bytes]]:
    raw = uploaded_file.getvalue()
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        return pdf_to_page_images(raw, max_pages=max_pages)
    return [(uploaded_file.name, image_file_to_png_bytes(raw))]


def ocr_image_bytes(image_bytes: bytes) -> str:
    engine = get_ocr_engine()
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    arr = np.array(img)
    result, _ = engine(arr)
    if not result:
        return ""
    lines = []
    # result items: [box, text, score]
    for item in result:
        try:
            text = item[1]
            score = float(item[2])
        except Exception:
            continue
        if text and score >= 0.35:
            lines.append(str(text))
    return "\n".join(lines)


def ocr_images(images: List[Tuple[str, bytes]], max_chars: int = 60000) -> str:
    chunks = []
    for name, img_bytes in images:
        txt = ocr_image_bytes(img_bytes)
        chunks.append(f"--- {name} ---\n{txt}")
    combined = "\n\n".join(chunks)
    if len(combined) > max_chars:
        combined = combined[:max_chars] + "\n\n[TRUNCATED]"
    return combined
