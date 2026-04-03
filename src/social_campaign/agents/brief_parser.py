"""Node 1: Parse and validate the campaign brief JSON."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from social_campaign.models import CampaignBrief, CampaignState


def parse_brief(state: dict[str, Any]) -> CampaignState:
    """Load the brief JSON, validate it, and resolve asset paths."""
    brief_path = Path(state["brief_path"])
    output_dir = state["output_dir"]

    raw = json.loads(brief_path.read_text())
    brief = CampaignBrief.model_validate(raw)

    # Resolve hero_image paths: nullify if file doesn't exist
    for product in brief.products:
        if product.hero_image and not Path(product.hero_image).is_file():
            product.hero_image = None

    return CampaignState(
        brief=brief,
        copy_variants={},
        localized_copy={},
        generated_images={},
        composited_assets={},
        output_dir=output_dir,
    )
