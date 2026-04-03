"""Generate full-bleed background scenes with DALL-E 3 (one call per product)."""

from __future__ import annotations

from pathlib import Path

from social_campaign.models import BackgroundPlan, CampaignState
from social_campaign.utils.openai_image_client import generate_image


def _as_plan(obj: BackgroundPlan | dict) -> BackgroundPlan:
    if isinstance(obj, BackgroundPlan):
        return obj
    return BackgroundPlan.model_validate(obj)


def _build_background_prompt(
    *,
    plan: BackgroundPlan,
    brand_name: str,
    brand_colors: list[str],
    brand_guidelines: str,
    target_region: str,
) -> str:
    return (
        "Full-bleed advertising background photograph. This image will be used as the "
        "background for a product ad — the actual product will be composited on top later.\n\n"
        f"Scene: {plan.scene_description}\n"
        f"Mood: {plan.mood}\n"
        f"Color & lighting: {plan.color_direction}\n\n"
        f"Brand palette hints (use as subtle accents): {', '.join(brand_colors)}\n"
        f"Brand: {brand_name}. Guidelines: {brand_guidelines}\n"
        f"Market: {target_region}\n\n"
        "Requirements:\n"
        "- Leave clear space in the lower-center area for a product to be placed on top\n"
        "- Photorealistic, premium quality, suitable for paid social advertising\n"
        "- Shallow depth of field, natural lighting, no CGI or synthetic look\n"
        "- NO text, letters, numbers, logos, watermarks, UI elements, or people\n"
        "- NO product or packaging — just the environment/surface/background\n"
        "- The bottom-center should have a flat surface, table, or ground where a product could naturally sit"
    )


def generate_backgrounds(state: CampaignState) -> dict:
    """Generate one DALL-E 3 background scene per product."""
    brief = state["brief"]
    raw_plans = state["background_plans"]
    plans: dict[str, BackgroundPlan] = {
        slug: _as_plan(p) for slug, p in raw_plans.items()
    }
    output_dir = Path(state["output_dir"])

    backgrounds: dict[str, str] = {}

    for product in brief.products:
        slug = product.slug
        plan = plans[slug]

        prompt = _build_background_prompt(
            plan=plan,
            brand_name=brief.brand.name,
            brand_colors=brief.brand.colors,
            brand_guidelines=brief.brand.guidelines,
            target_region=brief.target_region,
        )

        img = generate_image(prompt, aspect_ratio="1:1")

        product_dir = output_dir / slug
        product_dir.mkdir(parents=True, exist_ok=True)
        bg_path = product_dir / "background.png"
        img.save(bg_path, "PNG")
        backgrounds[slug] = str(bg_path)

    return {"generated_backgrounds": backgrounds}
