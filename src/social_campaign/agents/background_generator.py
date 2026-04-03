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
        "An empty scene with absolutely nothing in it except a surface and atmosphere. "
        "There are ZERO objects in this image. No bottle, no cup, no container, no tube, "
        "no jar, no can, no package, no box, no bag, no food, no drink, no equipment. "
        "ONLY a surface, lighting, and atmospheric effects.\n\n"
        f"Surface and atmosphere: {plan.scene_description}\n"
        f"Mood: {plan.mood}\n"
        f"Color & lighting: {plan.color_direction}\n\n"
        f"Color palette: tones that harmonize with {', '.join(brand_colors)}.\n"
        f"Feel: {brand_guidelines}\n\n"
        "COMPOSITION:\n"
        "- The center of the image must be empty open space\n"
        "- A surface or ground plane in the lower portion (stone, wood, fabric, concrete)\n"
        "- Beautiful lighting and atmospheric depth (bokeh, mist, reflections, color gels)\n"
        "- Photorealistic, premium quality\n\n"
        "THE IMAGE MUST BE COMPLETELY EMPTY — ONLY SURFACES AND LIGHT:\n"
        "- ZERO objects, items, things, or artifacts of any kind\n"
        "- ZERO bottles, containers, cups, vessels, tubes, tubs, cans, jars, boxes, bags\n"
        "- ZERO food, drinks, liquids, powders, or consumables\n"
        "- ZERO text, letters, numbers, symbols, logos, or labels\n"
        "- ZERO people, hands, faces, body parts, or silhouettes\n"
        "- ZERO furniture, equipment, tools, or machines\n"
        "- If it is a THING, do not include it. Only surfaces, light, color, and air."
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

        img = generate_image(prompt)

        product_dir = output_dir / slug
        product_dir.mkdir(parents=True, exist_ok=True)
        bg_path = product_dir / "background.png"
        img.save(bg_path, "PNG")
        backgrounds[slug] = str(bg_path)

    return {"generated_backgrounds": backgrounds}
