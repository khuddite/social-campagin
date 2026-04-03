"""Crop backgrounds, overlay text, composite hero ON TOP, then add logo."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from social_campaign.models import CampaignState
from social_campaign.utils.image_utils import (
    center_crop_to_ratio,
    composite_hero_over_background,
    overlay_logo,
    overlay_text_behind,
)


def composite_assets(state: CampaignState) -> dict:
    """Produce final campaign images for every product x aspect ratio.

    Compositing order: background → text → product → logo.
    Text is drawn BEFORE the product so the product overlaps the headline,
    creating an editorial, eye-catching intersecting layout.
    """
    brief = state["brief"]
    backgrounds = state["generated_backgrounds"]
    heroes = state["generated_images"]
    localized_copy = state["localized_copy"]
    output_dir = Path(state["output_dir"])

    composited: dict[str, dict[str, str]] = {}

    for product in brief.products:
        slug = product.slug
        bg = Image.open(backgrounds[slug]).convert("RGB")
        hero = Image.open(heroes[slug]).convert("RGBA")
        copy = localized_copy[slug]

        product_assets: dict[str, str] = {}

        for ratio in brief.aspect_ratios:
            ratio_key = ratio.replace(":", "_")

            # 1. Crop background to target aspect ratio
            cropped_bg = center_crop_to_ratio(bg, ratio)

            # 2. Overlay text BEHIND product (headline in lower-center)
            with_text = overlay_text_behind(
                cropped_bg, headline=copy.headline, body=copy.body,
            )

            # 3. Composite hero product ON TOP of text (product intersects headline)
            with_hero = composite_hero_over_background(with_text, hero)

            # 4. Add brand logo (top-right, always on top)
            final = overlay_logo(with_hero, brief.brand.logo_path)

            asset_dir = output_dir / slug / ratio_key
            asset_dir.mkdir(parents=True, exist_ok=True)
            asset_path = asset_dir / "campaign.png"
            final.save(asset_path, "PNG")
            product_assets[ratio_key] = str(asset_path)

        composited[slug] = product_assets

    return {"composited_assets": composited}
