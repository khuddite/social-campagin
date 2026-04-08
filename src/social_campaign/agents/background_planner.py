"""Plan full-bleed ad backgrounds tailored to audience, region, and campaign message."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from social_campaign.models import (
    BackgroundPlansResponse,
    CampaignState,
    LocalizedCopy,
)
from social_campaign.utils.llm_utils import LLM_MODEL


def plan_backgrounds(state: CampaignState) -> dict:
    """Produce a BackgroundPlan per product for GPT Image scene integration (one edit per product)."""
    brief = state["brief"]
    localized: dict[str, LocalizedCopy] = state["localized_copy"]

    slug_lines: list[str] = []
    for product in brief.products:
        slug = product.slug
        loc = localized[slug]
        slug_lines.append(
            f"- slug `{slug}`: tone hint={loc.headline!r}"
        )

    prompt = (
        "You are a senior art director designing BACKGROUNDS for paid social ads. "
        "A product will be composited on top later — you describe ONLY the backdrop.\n\n"
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
        "- Create rich, immersive environments that match the campaign's energy and audience.\n"
        "- Use interesting locations, textures, weather, nature, architecture, or abstract settings.\n"
        "- Premium, intentional lighting. Each background should feel different.\n"
        "- The center should have some open space for a product overlay.\n\n"
        "IMPORTANT — your scene_description goes directly to an image generator:\n"
        "- NEVER mention bottles, containers, cups, tubs, tubes, drinks, or packaging.\n"
        "- NEVER mention the product name or any product-category words.\n"
        "- The image generator draws anything you mention, so only describe the ENVIRONMENT.\n"
        "- Rich scenes are great — just no product-like objects.\n\n"
        "Hard rules:\n"
        "- NO text, letters, numbers, logos, UI, watermarks, or people.\n"
        "- NO bottles, containers, cups, tubes, tubs, drinks, or packaging.\n\n"
        "Return one entry per slug in the `plans` list."
    )

    llm = ChatOpenAI(model=LLM_MODEL, temperature=0.65).with_structured_output(
        BackgroundPlansResponse, method="function_calling"
    )
    response = llm.invoke(prompt)

    plans = {plan.slug: plan for plan in response.plans}

    return {"background_plans": plans}
