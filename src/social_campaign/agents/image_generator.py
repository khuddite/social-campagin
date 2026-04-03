"""Node: Generate hero product images on white backgrounds, then remove the background."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from social_campaign.models import CampaignState
from social_campaign.utils.image_client import generate_image
from social_campaign.utils.image_utils import remove_white_background


def _build_hero_prompt(product_name: str, description: str, brand_name: str) -> str:
    return (
        f"Product photograph of {product_name} on a PURE WHITE background. "
        f"E-commerce product cutout style. {description}.\n\n"
        f"The product must be centered, well-lit with soft studio lighting, "
        f"and the background must be completely flat pure white (#FFFFFF). "
        f"No shadows on the background, no gradients, no surfaces, no props, "
        f"no other objects — ONLY the product floating on solid white.\n\n"
        f"Do NOT render any text, letters, logos, labels, or typography on the product. "
        f"Show it as a clean, unlabeled version with a plain matte surface.\n\n"
        f"Style: high-end commercial product photography, like an Amazon or Apple product listing."
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

        prompt = _build_hero_prompt(
            product.name,
            product.description,
            brief.brand.name,
        )

        img = generate_image(prompt)

        # Remove the white background to get a transparent PNG
        img = remove_white_background(img)

        product_dir = output_dir / slug
        product_dir.mkdir(parents=True, exist_ok=True)
        hero_path = product_dir / "hero_base.png"
        img.save(hero_path, "PNG")
        images[slug] = str(hero_path)

    return {"generated_images": images}
