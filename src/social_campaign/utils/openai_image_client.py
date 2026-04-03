"""OpenAI image API: DALL-E 3 generation."""

from __future__ import annotations

import base64
import io
import os

from openai import OpenAI
from PIL import Image

MODEL = "dall-e-3"

DALLE_SIZE_BY_ASPECT: dict[str, str] = {
    "1:1": "1024x1024",
    "16:9": "1792x1024",
    "9:16": "1024x1792",
}


def generate_image(prompt: str, aspect_ratio: str = "1:1") -> Image.Image:
    """Generate an image from a text prompt using DALL-E 3."""
    size = DALLE_SIZE_BY_ASPECT.get(aspect_ratio, "1024x1024")
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    response = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size=size,
        quality="standard",
        n=1,
        response_format="b64_json",
    )
    b64 = response.data[0].b64_json
    if not b64:
        raise RuntimeError("DALL-E 3 returned no image data.")
    raw = base64.b64decode(b64)
    return Image.open(io.BytesIO(raw)).convert("RGB")
