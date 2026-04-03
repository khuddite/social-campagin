"""Image generation via OpenAI gpt-image-1.5."""

from __future__ import annotations

import base64
import io
import os

from openai import OpenAI
from PIL import Image

MODEL = "gpt-image-1.5"

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client


def generate_image(prompt: str) -> Image.Image:
    """Generate a 1024x1024 opaque image (for backgrounds)."""
    client = _get_client()
    response = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        background="opaque",
        output_format="png",
    )
    b64 = response.data[0].b64_json
    if not b64:
        raise RuntimeError(f"{MODEL} returned no image data.")
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def generate_transparent_image(prompt: str) -> Image.Image:
    """Generate a 1024x1024 RGBA image with transparent background (for product cutouts)."""
    client = _get_client()
    response = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        background="transparent",
        output_format="png",
    )
    b64 = response.data[0].b64_json
    if not b64:
        raise RuntimeError(f"{MODEL} returned no image data.")
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGBA")
