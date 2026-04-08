"""Image generation via OpenAI gpt-image-1.5."""

from __future__ import annotations

import base64
import io
import os
from typing import Literal

from openai import OpenAI
from PIL import Image

MODEL = "gpt-image-1.5"

_client: OpenAI | None = None


def _get_client() -> OpenAI:
    global _client
    if _client is None:
        _client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
    return _client


def generate_image(
    prompt: str,
    background: Literal["opaque", "transparent"] = "opaque",
) -> Image.Image:
    """Generate a 1024x1024 image.

    Args:
        prompt: Text description of the desired image.
        background: ``"opaque"`` for solid backgrounds (scenes),
            ``"transparent"`` for RGBA cutouts (product heroes).
    """
    client = _get_client()
    response = client.images.generate(
        model=MODEL,
        prompt=prompt,
        size="1024x1024",
        quality="auto",
        n=1,
        background=background,
        output_format="png",
    )
    b64 = response.data[0].b64_json
    if not b64:
        raise RuntimeError(f"{MODEL} returned no image data.")
    raw = base64.b64decode(b64)
    color_mode = "RGBA" if background == "transparent" else "RGB"
    return Image.open(io.BytesIO(raw)).convert(color_mode)
