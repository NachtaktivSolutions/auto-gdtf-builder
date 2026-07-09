from __future__ import annotations

import io
from typing import List, Tuple
from PIL import Image
import pytesseract


def ocr_image_bytes(image_bytes: bytes, lang: str = "deu+eng") -> str:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    return pytesseract.image_to_string(img, lang=lang, config="--psm 6")


def ocr_images(images: List[Tuple[str, bytes]], lang: str = "deu+eng", max_chars: int = 60000) -> str:
    chunks = []
    for name, img in images:
        try:
            txt = ocr_image_bytes(img, lang=lang)
        except Exception as exc:
            txt = f"[OCR ERROR on {name}: {exc}]"
        chunks.append(f"--- {name} ---\n{txt}")
    text = "\n\n".join(chunks)
    if len(text) > max_chars:
        text = text[:max_chars] + "\n\n[TRUNCATED]"
    return text
