"""Generate full-bleed background scenes with DALL-E 3 (one call per product)."""

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
) -> str:
    return (
        "Photorealistic nature scene. An empty natural landscape close-up "
        "with no objects, no items, no man-made things — ONLY nature.\n\n"
        f"Scene: {plan.scene_description}\n"
        f"Mood: {plan.mood}\n"
        f"Color & lighting: {plan.color_direction}\n\n"
        "WHAT TO SHOW:\n"
        "- Natural lighting: golden hour sun, dappled forest light through leaves, "
        "soft overcast glow, warm sunrise, or misty morning light\n"
        "- Organic textures: wet stone, moss, wood grain, leaves, water droplets, "
        "earth, bark, condensation\n"
        "- A natural flat surface in the lower portion "
        "(flat stone slab, weathered wood, moss-covered rock, wet slate, leaf bed)\n"
        "- Depth: soft bokeh from foliage, morning mist, "
        "gentle rain, light filtering through canopy, water reflections\n"
        "- The center area should be open empty space\n"
        "- Editorial nature photography feel, pristine untouched environment\n\n"
        f"COLOR: natural tones — deep forest greens, earthy browns, "
        f"cool water blues, warm amber sunlight. "
        f"Accent colors inspired by: {', '.join(brand_colors)}\n\n"
        "THIS IMAGE MUST CONTAIN ONLY NATURAL ELEMENTS:\n"
        "rocks, water, plants, moss, wood, leaves, sky, light, mist, earth.\n\n"
        "DO NOT INCLUDE ANY OF THESE:\n"
        "- Any object, item, thing, or artifact made by humans\n"
        "- Any container, vessel, or receptacle of any kind\n"
        "- Any text, letters, numbers, symbols, logos, or labels\n"
        "- Any person, hand, face, body part, or silhouette\n"
        "- Any building, room, wall, floor, furniture, or structure"
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
