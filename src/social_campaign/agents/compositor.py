"""Node 5: Resize, crop, overlay text and logo to produce final campaign assets."""

from __future__ import annotations

from pathlib import Path

from PIL import Image

from social_campaign.models import CampaignState
from social_campaign.utils.image_utils import (
    center_crop_to_ratio,
    overlay_logo,
    overlay_text,
)


def composite_assets(state: CampaignState) -> dict:
    """Produce final campaign images for every product × aspect ratio."""
    brief = state["brief"]
    generated_images = state["generated_images"]
    localized_copy = state["localized_copy"]
    output_dir = Path(state["output_dir"])

    composited: dict[str, dict[str, str]] = {}

    for product in brief.products:
        slug = product.slug
        hero_path = generated_images[slug]
        hero = Image.open(hero_path)
        copy = localized_copy[slug]

        product_assets: dict[str, str] = {}

        for ratio in brief.aspect_ratios:
            ratio_key = ratio.replace(":", "_")

            cropped = center_crop_to_ratio(hero, ratio)
            cropped = overlay_logo(cropped, brief.brand.logo_path)
            final = overlay_text(cropped, headline=copy.headline, body=copy.body)

            asset_dir = output_dir / slug / ratio_key
            asset_dir.mkdir(parents=True, exist_ok=True)
            asset_path = asset_dir / "campaign.png"
            final.save(asset_path, "PNG")
            product_assets[ratio_key] = str(asset_path)

        composited[slug] = product_assets

    return {"composited_assets": composited}
