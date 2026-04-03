"""Plan full-bleed ad backgrounds tailored to audience, region, and campaign message."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from social_campaign.models import BackgroundPlan, CampaignState, LocalizedCopy
from social_campaign.utils.llm_utils import LLM_MODEL, parse_llm_json


def plan_backgrounds(state: CampaignState) -> dict:
    """Produce a BackgroundPlan per product for GPT Image scene integration (one edit per product)."""
    brief = state["brief"]
    localized: dict[str, LocalizedCopy] = state["localized_copy"]

    # Only pass slugs + headline tone hints — NO product names, descriptions, or features
    # to prevent the image model from generating bottles/tubs in the background.
    slug_lines: list[str] = []
    for product in brief.products:
        slug = product.slug
        loc = localized[slug]
        slug_lines.append(
            f"- slug `{slug}`: headline tone hint={loc.headline!r}"
        )

    prompt = (
        "You are a senior art director designing BACKGROUNDS for paid social ads. "
        "A product will be composited on top later — you describe ONLY the backdrop: "
        "surface, environment, lighting, and color.\n\n"
        f"Campaign: {brief.campaign_name!r}\n"
        f"Campaign message: {brief.campaign_message!r}\n"
        f"Target audience: {brief.target_audience}\n"
        f"Region / market: {brief.target_region} ({brief.target_language})\n"
        f"Brand: {brief.brand.name}\n"
        f"Brand colors: {', '.join(brief.brand.colors)}\n"
        f"Brand guidelines: {brief.brand.guidelines}\n\n"
        "Slugs (one background per slug):\n"
        + "\n".join(slug_lines)
        + "\n\n"
        "DESIGN DIRECTION:\n"
        f"- Brand colors: {', '.join(brief.brand.colors)} — background must complement these.\n"
        f"- Derive the visual aesthetic from: {brief.brand.guidelines}\n"
        "- Premium, intentional lighting. Each background should feel different.\n"
        "- The center must be relatively clear for the product overlay.\n\n"
        "CRITICAL — your scene_description will be sent directly to an image generator. "
        "The image generator will literally draw anything you mention. Therefore:\n"
        "- NEVER mention any physical object in your scene_description: no bottles, "
        "no containers, no cups, no tubs, no packaging, no drinkware, no food, no equipment.\n"
        "- NEVER mention the product name or category.\n"
        "- Describe ONLY: surfaces (stone, wood, concrete, fabric), lighting (golden hour, "
        "studio, neon), atmosphere (mist, bokeh, reflections), and color moods.\n"
        "- If you mention an object, the image generator WILL draw it and ruin the background.\n\n"
        "Hard rules:\n"
        "- NO text, letters, numbers, logos, UI, watermarks, or people.\n"
        "- NO objects of any kind — only surfaces, light, and atmosphere.\n\n"
        "Respond ONLY with JSON: an object whose keys are product slugs (strings) and values are objects "
        'with keys "scene_description", "mood", "color_direction" (all strings).'
    )

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0.65)
    response = llm.invoke(prompt)
    raw = parse_llm_json(response.content)

    plans: dict[str, BackgroundPlan] = {}
    for product in brief.products:
        slug = product.slug
        if slug not in raw:
            raise ValueError(f"Background plan missing slug {slug!r} in model output.")
        plans[slug] = BackgroundPlan.model_validate(raw[slug])

    return {"background_plans": plans}
