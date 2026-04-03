"""OpenAI DALL·E 3 image generation."""

from __future__ import annotations

import base64
import io
import os

from openai import OpenAI
from PIL import Image

MODEL = "dall-e-3"
SIZE = "1024x1024"


def generate_image(prompt: str) -> Image.Image:
    """Generate a 1024×1024 image from a text prompt using DALL·E 3."""
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=SIZE,
        quality="standard",
        n=1,
        response_format="b64_json",
    )
    b64 = response.data[0].b64_json
    if not b64:
        raise RuntimeError("DALL·E 3 returned no image data.")
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")
