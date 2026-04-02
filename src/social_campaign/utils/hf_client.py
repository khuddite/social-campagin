"""HuggingFace Inference API wrapper for image generation."""

from __future__ import annotations

import os

from huggingface_hub import InferenceClient
from PIL import Image

MODEL = "black-forest-labs/FLUX.1-schnell"


def generate_image(prompt: str) -> Image.Image:
    """Generate a 1024x1024 image from a text prompt using FLUX.1-schnell."""
    token = os.environ.get("HF_API_TOKEN")
    client = InferenceClient(token=token)
    image = client.text_to_image(
        prompt,
        model=MODEL,
        width=1024,
        height=1024,
    )
    return image
