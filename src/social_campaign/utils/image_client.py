"""Image generation via FLUX.1 on HuggingFace Inference API."""

from __future__ import annotations

import os

from huggingface_hub import InferenceClient
from PIL import Image

MODEL = "black-forest-labs/FLUX.1-dev"


def generate_image(prompt: str, aspect_ratio: str = "1:1") -> Image.Image:
    """Generate a 1024x1024 image from a text prompt using FLUX.1-schnell.

    The ``aspect_ratio`` parameter is accepted for API compatibility but
    FLUX.1 via HF Inference only produces square images. The pipeline
    crops to the target ratio in a later compositing step.
    """
    token = os.environ.get("HF_API_TOKEN")
    client = InferenceClient(token=token)
    image = client.text_to_image(
        prompt,
        model=MODEL,
        width=1024,
        height=1024,
    )
    return image.convert("RGB")
