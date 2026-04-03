"""Node 4: Generate hero images for products missing assets."""

from __future__ import annotations

from pathlib import Path

from social_campaign.models import CampaignState
from social_campaign.utils.openai_image_client import generate_image


def _build_hero_prompt(product_name: str, description: str, brand_name: str, region: str) -> str:
    """Prompt tuned to minimise illegible / hallucinated text on packaging (image model weakness)."""
    return (
        f"Professional advertising product photograph, square composition, studio lighting, "
        f"shallow depth of field, photorealistic.\n\n"
        f"Subject: {product_name}. Context: {description}. "
        f"Inspired by brand mood for {brand_name}, market {region}.\n\n"
        f"CRITICAL — no typography in the scene: do not render any letters, words, numbers, "
        f"logos, nutrition labels, ingredient lists, barcodes, URLs, or packaging mockups with text. "
        f"Show the product as a plain unlabeled bottle, tub, or vessel with a blank matte surface, "
        f"OR show only ingredients, ice, fruit, liquid, or equipment with no branded packaging. "
        f"No fake product names, no gibberish text, no watermarks, no subtitles, no signs.\n\n"
        f"High-end commercial look, vibrant but natural colours."
    )


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

        # Generate new image (text-free hero — real ad copy is composited later in Pillow).
        prompt = _build_hero_prompt(
            product.name,
            product.description,
            brief.brand.name,
            brief.target_region,
        )

        img = generate_image(prompt)

        # Save to output directory
        product_dir = output_dir / slug
        product_dir.mkdir(parents=True, exist_ok=True)
        hero_path = product_dir / "hero_base.png"
        img.save(hero_path)
        images[slug] = str(hero_path)

    return {"generated_images": images}
