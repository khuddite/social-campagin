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
            f"key features={product.key_features!r}; "
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
        "CRITICAL CONTEXT — the product will be composited as a large centered element:\n"
        f"- Brand primary colors are: {', '.join(brief.brand.colors)}\n"
        "- The background MUST complement and harmonize with these colors.\n"
        "- The background should make the product POP — e.g. earthy dark tones behind a "
        "bright green product, warm natural tones behind cool products.\n\n"
        "DESIGN DIRECTION — natural, organic, premium:\n"
        "- This is an ECO-FRIENDLY brand. Backgrounds must feel NATURAL and ORGANIC.\n"
        "- Use real-world natural textures and elements: wet moss, river stones, damp earth, "
        "raw wood grain, condensation on leaves, morning dew, rainforest canopy light, "
        "ocean mist, sunlit fern fronds, volcanic rock, bark, tropical foliage.\n"
        "- Lighting should be NATURAL: golden hour sunlight, dappled forest light filtering "
        "through leaves, soft overcast diffusion, warm sunrise glow, or cool blue twilight.\n"
        "- Surfaces: natural stone slab, weathered driftwood, moss-covered rock, "
        "wet slate, reclaimed wood, or a bed of fresh green leaves.\n"
        "- Add depth with water droplets, morning mist, bokeh from foliage, "
        "soft rain, or light filtering through canopy.\n"
        "- Think Patagonia, Hydro Flask, or premium organic brand aesthetics.\n"
        "- Each product background should feel DIFFERENT — vary the natural setting.\n\n"
        "Hard rules:\n"
        "- NO text, letters, numbers, logos, UI, watermarks, or people.\n"
        "- NO product, packaging, bottles, tubs, cups, containers, drinkware, or branded items.\n"
        "- NO man-made objects at all — ONLY natural elements (rocks, water, plants, light, sky).\n"
        "- NO artificial/synthetic elements — no neon, no glass platforms, no studio setups.\n"
        "- Keep the center area relatively clear — the product will be composited there large.\n\n"
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
