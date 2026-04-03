"""Node: Generate transparent product cutout images using gpt-image-1."""

from __future__ import annotations

from pathlib import Path

from social_campaign.models import CampaignState
from social_campaign.utils.image_client import generate_transparent_image


def _build_hero_prompt(
    product_name: str,
    description: str,
    brand_name: str,
    key_features: list[str],
) -> str:
    features_str = ", ".join(key_features) if key_features else ""
    return (
        f"Professional product photograph of {product_name} on a transparent background. "
        f"{description}.\n\n"
        f"The product must be centered, well-lit with soft studio lighting and a subtle "
        f"green glow/rim light to give it a premium feel. The background must be "
        f"completely transparent — no surface, no shadow, no gradient, no props.\n\n"
        f"The product SHOULD have realistic branded packaging with:\n"
        f"- The brand name '{brand_name}' and a leaf icon/logo on the product\n"
        f"- The product name '{product_name}' clearly visible on the label\n"
        f"- Key features or tagline: {features_str}\n"
        f"- Premium, professional label design with the brand's green (#00A86B) and black color scheme\n\n"
        f"Style: high-end product photography like Nike, Gatorade, or Hydro Flask packaging. "
        f"Photorealistic, detailed, polished. The product should look like a real item "
        f"you'd find on a store shelf — not a plain unlabeled mockup."
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
            product.key_features,
        )
        img = generate_transparent_image(prompt)

        product_dir = output_dir / slug
        product_dir.mkdir(parents=True, exist_ok=True)
        hero_path = product_dir / "hero_base.png"
        img.save(hero_path, "PNG")
        images[slug] = str(hero_path)

    return {"generated_images": images}
