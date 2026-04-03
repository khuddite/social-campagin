"""Image generation via FLUX.1 on HuggingFace Inference API."""

from __future__ import annotations

import os

from huggingface_hub import InferenceClient
from PIL import Image

MODEL = "black-forest-labs/FLUX.1-schnell"

_client: InferenceClient | None = None


def _get_client() -> InferenceClient:
    global _client
    if _client is None:
        token = os.environ.get("HF_API_TOKEN")
        _client = InferenceClient(token=token)
    return _client


def generate_image(prompt: str) -> Image.Image:
    """Generate a 1024x1024 image from a text prompt using FLUX.1."""
    client = _get_client()
    image = client.text_to_image(
        prompt,
        model=MODEL,
        width=1024,
        height=1024,
    )
    return image.convert("RGB")
