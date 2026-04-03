"""Node: Generate transparent product cutout images using gpt-image-1."""

from __future__ import annotations

from pathlib import Path

from social_campaign.models import CampaignState
from social_campaign.utils.image_client import generate_transparent_image


def _build_hero_prompt(product_name: str, description: str) -> str:
    return (
        f"Product cutout of {product_name} on a transparent background. "
        f"{description}.\n\n"
        f"The product must be centered, well-lit with soft studio lighting. "
        f"The background must be completely transparent — no surface, no shadow, "
        f"no gradient, no props, no other objects. ONLY the product itself.\n\n"
        f"Do NOT render any text, letters, logos, labels, or typography on the product. "
        f"Show it as a clean, unlabeled version with a plain matte surface.\n\n"
        f"Style: high-end e-commerce product photography cutout."
    )


def generate_images(state: CampaignState) -> dict:
    """Generate hero images for products without existing assets."""
    brief = state["brief"]
    output_dir = Path(state["output_dir"])
    images: dict[str, str] = {}

    for product in brief.products:
        slug = product.slug

        if product.hero_image:
            images[slug] = product.hero_image
            continue

        prompt = _build_hero_prompt(product.name, product.description)
        img = generate_transparent_image(prompt)

        product_dir = output_dir / slug
        product_dir.mkdir(parents=True, exist_ok=True)
        hero_path = product_dir / "hero_base.png"
        img.save(hero_path, "PNG")
        images[slug] = str(hero_path)

    return {"generated_images": images}
