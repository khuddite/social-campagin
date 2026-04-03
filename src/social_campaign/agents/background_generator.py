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
        "Premium product-advertisement background for a paid social campaign. "
        "A product will be composited on top later — generate ONLY the background.\n\n"
        "STYLE REFERENCE: Think Nike, Apple, or Gatorade hero-product ads — bold, minimal, dramatic. "
        "NOT a landscape photo. NOT a room interior. This is a studio/abstract ad backdrop.\n\n"
        f"Scene: {plan.scene_description}\n"
        f"Mood: {plan.mood}\n"
        f"Color & lighting: {plan.color_direction}\n\n"
        "COMPOSITION (critical):\n"
        "- Bottom third: a clean, flat, horizontal surface (stone, concrete, metal, glass, fabric) "
        "where the product will appear to rest. Must be visible and uncluttered.\n"
        "- Upper two-thirds: atmospheric backdrop — bold color gradients, volumetric light, "
        "subtle bokeh, light streaks, colored gel lighting, or soft haze. Keep it SIMPLE.\n"
        "- Strong contrast between the surface and background to create depth.\n\n"
        f"Brand palette (weave subtly into lighting/color): {', '.join(brand_colors)}\n"
        f"Market: {target_region}\n\n"
        "ABSOLUTE RULES:\n"
        "- ZERO text, letters, numbers, logos, watermarks, labels, UI of any kind\n"
        "- ZERO products, bottles, containers, packaging, or branded objects\n"
        "- ZERO people, hands, faces, silhouettes\n"
        "- ZERO clutter — no gym equipment, no furniture, no props, no gadgets\n"
        "- The image should be MINIMAL: a surface + atmosphere + dramatic lighting. That's it."
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
