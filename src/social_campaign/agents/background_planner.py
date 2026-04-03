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
        "You are a senior art director for social display ads.\n"
        "For EACH product below, describe the ENVIRONMENT and LIGHTING that should surround the product "
        "in a single photorealistic shot (the image model will see the product and fill transparent areas).\n\n"
        f"Campaign: {brief.campaign_name!r}\n"
        f"Campaign message: {brief.campaign_message!r}\n"
        f"Target audience: {brief.target_audience}\n"
        f"Region / market: {brief.target_region} ({brief.target_language})\n"
        f"Brand: {brief.brand.name}\n"
        f"Brand colors (use as harmonizing accents, not loud logos): {', '.join(brief.brand.colors)}\n"
        f"Brand guidelines: {brief.brand.guidelines}\n\n"
        "Products:\n"
        + "\n".join(lines)
        + "\n\n"
        "Requirements for every background scene:\n"
        "- Eye-catching, premium, suitable for paid social.\n"
        "- Culturally appropriate for the target region and audience.\n"
        "- Leave clear negative space toward the lower-center where a product will be composited.\n"
        "- NO text, letters, numbers, logos, UI, watermarks, or people faces.\n"
        "- Do NOT depict the product, packaging, or branded items.\n\n"
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
