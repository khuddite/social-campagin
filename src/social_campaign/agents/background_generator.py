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
        "Premium eco-friendly product-advertisement background. A product will be "
        "composited on top later — generate ONLY the natural background environment.\n\n"
        "STYLE: Organic, natural, premium — like a Patagonia or Hydro Flask ad. "
        "Photorealistic nature close-up with beautiful natural lighting. "
        "NOT synthetic, NOT neon, NOT a studio setup.\n\n"
        f"Scene: {plan.scene_description}\n"
        f"Mood: {plan.mood}\n"
        f"Color & lighting: {plan.color_direction}\n\n"
        "VISUAL QUALITIES (must have):\n"
        "- Natural lighting: golden hour sun, dappled forest light through leaves, "
        "soft overcast glow, warm sunrise, or misty morning light\n"
        "- Organic textures: wet stone, moss, wood grain, leaves, water droplets, "
        "earth, bark, condensation — things you can almost feel\n"
        "- A natural surface in the lower portion where the product could rest "
        "(flat stone slab, weathered wood, moss-covered rock, wet slate, leaf bed)\n"
        "- Depth through nature: soft bokeh from foliage, morning mist, "
        "gentle rain, light filtering through canopy, water reflections\n"
        "- The center area should be relatively clear for the product\n"
        "- Should feel like an outdoor editorial shoot in a pristine natural setting\n\n"
        f"COLOR HARMONY: Brand colors are {', '.join(brand_colors)}. "
        f"Use natural tones that complement these — deep forest greens, earthy browns, "
        f"cool water blues, warm amber sunlight. The product is green/black so "
        f"natural earth tones and rich greens will harmonize beautifully.\n"
        f"Market: {target_region}\n\n"
        "ABSOLUTE RULES (violating any of these makes the image unusable):\n"
        "- ZERO text, letters, numbers, logos, watermarks, labels, UI of any kind\n"
        "- ZERO bottles, cups, containers, tubs, cans, jars, packaging, or ANY man-made product\n"
        "- ZERO drinkware of any kind — no water bottles, no flasks, no glasses, no cups\n"
        "- ZERO people, hands, faces, silhouettes\n"
        "- ZERO artificial elements — no neon, no glass platforms, no studio gear\n"
        "- ZERO indoor environments — this is pure nature\n"
        "- The image must contain ONLY natural elements: rocks, water, plants, light, sky"
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
