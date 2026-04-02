"""Node 4: Generate hero images for products missing assets."""

from __future__ import annotations

from pathlib import Path

from social_campaign.models import CampaignState
from social_campaign.utils.hf_client import generate_image


def generate_images(state: CampaignState) -> dict:
    """Generate hero images for products without existing assets."""
    brief = state["brief"]
    output_dir = Path(state["output_dir"])
    images: dict[str, str] = {}

    for product in brief.products:
        slug = product.slug

        if product.hero_image:
            # Reuse existing asset
            images[slug] = product.hero_image
            continue

        # Generate new image
        prompt = (
            f"Professional product photography for a social media ad. "
            f"Product: {product.name} — {product.description}. "
            f"Style: modern, clean, vibrant. "
            f"Brand: {brief.brand.name}. "
            f"Target market: {brief.target_region}. "
            f"No text in the image."
        )

        img = generate_image(prompt)

        # Save to output directory
        product_dir = output_dir / slug
        product_dir.mkdir(parents=True, exist_ok=True)
        hero_path = product_dir / "hero_base.png"
        img.save(hero_path)
        images[slug] = str(hero_path)

    return {"generated_images": images}
