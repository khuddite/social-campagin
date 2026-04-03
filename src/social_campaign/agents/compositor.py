"""Crop backgrounds to each aspect ratio, composite hero, then overlay logo and copy."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from social_campaign.models import CampaignState
from social_campaign.utils.image_utils import (
    center_crop_to_ratio,
    composite_hero_over_background,
    overlay_logo,
    overlay_text,
)


def composite_assets(state: CampaignState) -> dict:
    """Produce final campaign images for every product x aspect ratio."""
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
            cropped_bg = center_crop_to_ratio(bg, ratio)
            with_hero = composite_hero_over_background(cropped_bg, hero)
            with_logo = overlay_logo(with_hero, brief.brand.logo_path)
            final = overlay_text(with_logo, headline=copy.headline, body=copy.body)

            asset_dir = output_dir / slug / ratio_key
            asset_dir.mkdir(parents=True, exist_ok=True)
            asset_path = asset_dir / "campaign.png"
            final.save(asset_path, "PNG")
            product_assets[ratio_key] = str(asset_path)

        composited[slug] = product_assets

    return {"composited_assets": composited}
