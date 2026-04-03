"""Generate background scenes with FLUX.1 (one call per product)."""

from __future__ import annotations

from pathlib import Path

from social_campaign.models import BackgroundPlan, CampaignState
from social_campaign.utils.image_client import generate_image


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
    campaign_name: str,
    campaign_message: str,
    target_audience: str,
) -> str:
    """Build a prompt driven by the planner's scene description and the brief context.

    The planner already factored in audience, region, brand, and campaign theme
    when crafting the BackgroundPlan. This prompt passes that through faithfully
    instead of overriding it with hardcoded aesthetics.
    """
    return (
        f"Photorealistic advertising background photograph for a {target_region} market.\n\n"
        f"Scene direction: {plan.scene_description}\n"
        f"Mood: {plan.mood}\n"
        f"Color & lighting: {plan.color_direction}\n\n"
        f"Context: This is a background for a '{campaign_name}' campaign targeting "
        f"{target_audience} in {target_region}. Campaign message: '{campaign_message}'. "
        f"Brand: {brand_name}. Brand tone: {brand_guidelines}\n\n"
        f"Color palette: use tones that harmonize with {', '.join(brand_colors)}.\n\n"
        "COMPOSITION:\n"
        "- The center of the image should be relatively open/clear\n"
        "- Include a surface or ground plane in the lower portion\n"
        "- Beautiful lighting and atmospheric depth (bokeh, mist, reflections)\n"
        "- Premium quality suitable for paid social advertising\n\n"
        "DO NOT INCLUDE:\n"
        "- Any object, item, or artifact made by humans (no containers, no vessels, no drinkware)\n"
        "- Any text, letters, numbers, symbols, logos, or labels\n"
        "- Any person, hand, face, body part, or silhouette\n"
        "- Any building, room, wall, furniture, or indoor structure"
    )


def generate_backgrounds(state: CampaignState) -> dict:
    """Generate one background scene per product."""
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
            campaign_name=brief.campaign_name,
            campaign_message=brief.campaign_message,
            target_audience=brief.target_audience,
        )

        img = generate_image(prompt, aspect_ratio="1:1")

        product_dir = output_dir / slug
        product_dir.mkdir(parents=True, exist_ok=True)
        bg_path = product_dir / "background.png"
        img.save(bg_path, "PNG")
        backgrounds[slug] = str(bg_path)

    return {"generated_backgrounds": backgrounds}
