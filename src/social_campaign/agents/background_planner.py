"""Plan full-bleed ad backgrounds tailored to audience, region, and campaign message."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from social_campaign.models import BackgroundPlan, CampaignState, LocalizedCopy
from social_campaign.utils.llm_utils import parse_llm_json


def plan_backgrounds(state: CampaignState) -> dict:
    """Produce a BackgroundPlan per product for GPT Image scene integration (one edit per product)."""
    brief = state["brief"]
    localized: dict[str, LocalizedCopy] = state["localized_copy"]

    lines: list[str] = []
    for product in brief.products:
        slug = product.slug
        loc = localized[slug]
        lines.append(
            f"- slug `{slug}`: product={product.name!r}; description={product.description!r}; "
            f"localized headline={loc.headline!r} (hint for tone, not for the image text)"
        )

    prompt = (
        "You are a senior art director at a top creative agency, specialising in high-performance "
        "paid social ads (Instagram, TikTok, Facebook). Your job: design the BACKGROUND for each "
        "product ad. The product itself will be composited on top later — you are only describing "
        "the surface, environment, and lighting behind and beneath it.\n\n"
        f"Campaign: {brief.campaign_name!r}\n"
        f"Campaign message: {brief.campaign_message!r}\n"
        f"Target audience: {brief.target_audience}\n"
        f"Region / market: {brief.target_region} ({brief.target_language})\n"
        f"Brand: {brief.brand.name}\n"
        f"Brand colors: {', '.join(brief.brand.colors)}\n"
        f"Brand guidelines: {brief.brand.guidelines}\n\n"
        "Products:\n"
        + "\n".join(lines)
        + "\n\n"
        "DESIGN DIRECTION — think premium product-ad backgrounds, NOT landscape photography:\n"
        "- Use SIMPLE, CLEAN surfaces: polished concrete, marble slab, dark slate, wet stone, "
        "brushed metal, draped fabric, or bold gradient color wash.\n"
        "- Add atmosphere with dramatic studio lighting: rim lights, colored gels, light streaks, "
        "caustic reflections, bokeh orbs, or volumetric haze.\n"
        "- The bottom-center MUST have a flat, horizontal surface where the product appears to sit.\n"
        "- Keep the scene MINIMAL — a surface plus atmosphere. Do NOT create busy, cluttered, or "
        "literal real-world environments (no gyms, parks, kitchens, offices).\n"
        "- Think Nike, Apple, Gatorade product ads — bold, simple, dramatic.\n"
        "- Culturally resonate with the target market through color mood, not literal landmarks.\n\n"
        "Hard rules:\n"
        "- NO text, letters, numbers, logos, UI, watermarks, or people.\n"
        "- NO product, packaging, bottles, tubs, or branded items.\n"
        "- NO busy/cluttered scenes — simplicity is premium.\n\n"
        "Respond ONLY with JSON: an object whose keys are product slugs (strings) and values are objects "
        'with keys "scene_description", "mood", "color_direction" (all strings).'
    )

    llm = ChatOpenAI(model="gpt-4o", temperature=0.65)
    response = llm.invoke(prompt)
    raw = parse_llm_json(response.content)

    plans: dict[str, BackgroundPlan] = {}
    for product in brief.products:
        slug = product.slug
        if slug not in raw:
            raise ValueError(f"Background plan missing slug {slug!r} in model output.")
        plans[slug] = BackgroundPlan.model_validate(raw[slug])

    return {"background_plans": plans}
