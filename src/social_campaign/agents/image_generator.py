"""Node: Generate transparent product cutout images using gpt-image-1."""

from __future__ import annotations

from pathlib import Path

from social_campaign.models import CampaignState
from social_campaign.utils.image_client import generate_image


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

        brand = brief.brand
        features_str = ", ".join(product.key_features)

        prompt_parts = [
            f"Professional product photograph of {product.name} on a transparent background.",
            f"Product: {product.description}.",
            "",
            "Framing & background:",
            "- Single hero product, centered, with completely transparent background.",
            "- No surface, shadow, gradient, or props.",
            "",
            "Packaging & branding:",
            f"- Brand: {brand.name}. Product label reads '{product.name}'.",
            f"- Label callouts: {features_str}.",
            "",
            "Brand visual guidelines (adapt lighting, palette, and texture cues):",
            brand.guidelines,
            "",
            "Style: photorealistic, high-end product photography.",
            "Should look like a real retail item — not a plain unlabeled mockup.",
        ]

        prompt = "\n".join(prompt_parts)
        img = generate_image(prompt, background="transparent")

        product_dir = output_dir / slug
        product_dir.mkdir(parents=True, exist_ok=True)
        hero_path = product_dir / "hero_base.png"
        img.save(hero_path, "PNG")
        images[slug] = str(hero_path)

    return {"generated_images": images}
