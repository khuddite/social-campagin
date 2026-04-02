"""Node 2: Generate ad copy for each product using GPT-4o."""

from __future__ import annotations

import json

from langchain_openai import ChatOpenAI

from social_campaign.models import CampaignState, CopyVariant


def write_copy(state: CampaignState) -> dict:
    """Generate headline + body copy for every product in the brief."""
    brief = state["brief"]
    llm = ChatOpenAI(model="gpt-4o", temperature=0.7)

    copy_variants: dict[str, CopyVariant] = {}

    for product in brief.products:
        prompt = (
            f"You are an expert social media ad copywriter.\n"
            f"Brand: {brief.brand.name}\n"
            f"Brand guidelines: {brief.brand.guidelines}\n"
            f"Product: {product.name} — {product.description}\n"
            f"Key features: {', '.join(product.key_features)}\n"
            f"Target audience: {brief.target_audience}\n"
            f"Target region: {brief.target_region}\n"
            f"Campaign message: {brief.campaign_message}\n\n"
            f"Write a short, punchy ad copy with a headline (max 8 words) and body text (max 20 words). "
            f"The copy should resonate with the target audience and align with brand guidelines.\n\n"
            f'Respond ONLY with JSON: {{"headline": "...", "body": "..."}}'
        )

        response = llm.invoke(prompt)
        data = json.loads(response.content)
        copy_variants[product.slug] = CopyVariant(**data)

    return {"copy_variants": copy_variants}
