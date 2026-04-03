"""Image generation via OpenAI: DALL-E 3 for backgrounds, gpt-image-1 for transparent product cutouts."""

from __future__ import annotations

import base64
import io
import os

from openai import OpenAI
from PIL import Image

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client


def generate_image(prompt: str) -> Image.Image:
    """Generate a 1024x1024 image using DALL-E 3 (opaque RGB)."""
    client = _get_client()
    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="standard",
        n=1,
        response_format="b64_json",
    )
    b64 = response.data[0].b64_json
    if not b64:
        raise RuntimeError("DALL-E 3 returned no image data.")
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")


def generate_transparent_image(prompt: str) -> Image.Image:
    """Generate a 1024x1024 RGBA image with transparent background using gpt-image-1."""
    client = _get_client()
    response = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        quality="high",
        n=1,
        background="transparent",
        output_format="png",
    )
    b64 = response.data[0].b64_json
    if not b64:
        raise RuntimeError("gpt-image-1 returned no image data.")
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGBA")
