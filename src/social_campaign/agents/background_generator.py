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
        "Cinematic product-advertisement background for a premium paid social campaign. "
        "A product will be composited on top later — generate ONLY the background.\n\n"
        "STYLE: Hyper-cinematic, scroll-stopping, movie-poster-meets-luxury-product-photography. "
        "NOT a real room, NOT a landscape. This is an abstract, dramatic, visually stunning ad backdrop.\n\n"
        f"Scene: {plan.scene_description}\n"
        f"Mood: {plan.mood}\n"
        f"Color & lighting: {plan.color_direction}\n\n"
        "VISUAL QUALITIES (must have):\n"
        "- Dramatic cinematic lighting: neon glows, colored gel lights, volumetric fog, "
        "light rays cutting through haze, lens flares, or caustic reflections\n"
        "- Rich, deep color contrasts — shadows should be deep, highlights should pop\n"
        "- Depth through atmospheric effects: particles, mist, water droplets, bokeh, subtle smoke\n"
        "- A surface or ground plane in the lower portion where the product could sit "
        "(reflective wet surface, dark matte platform, glowing glass, or abstract ground)\n"
        "- The center-bottom area should be relatively clear for the product\n"
        "- Shot feels like it was lit by a Hollywood cinematographer, not a stock photographer\n\n"
        f"Brand palette (weave into the lighting and color grading): {', '.join(brand_colors)}\n"
        f"Market: {target_region}\n\n"
        "ABSOLUTE RULES:\n"
        "- ZERO text, letters, numbers, logos, watermarks, labels, UI of any kind\n"
        "- ZERO products, bottles, containers, packaging, or branded objects\n"
        "- ZERO people, hands, faces, silhouettes\n"
        "- ZERO real-world environments — no rooms, gyms, parks, kitchens, offices\n"
        "- ZERO clutter — this is abstract atmosphere + surface + cinematic light"
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
