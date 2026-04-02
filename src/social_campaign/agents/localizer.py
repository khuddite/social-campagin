"""Node 3: Translate and culturally adapt copy for the target market."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from social_campaign.models import CampaignState, LocalizedCopy
from social_campaign.utils.llm_utils import parse_llm_json


def localize_copy(state: CampaignState) -> dict:
    """Translate and culturally adapt copy for each product."""
    brief = state["brief"]
    copy_variants = state["copy_variants"]
    llm = ChatOpenAI(model="gpt-4o", temperature=0.4)

    localized: dict[str, LocalizedCopy] = {}

    for product in brief.products:
        slug = product.slug
        original = copy_variants[slug]

        prompt = (
            f"You are an expert localization specialist.\n"
            f"Translate AND culturally adapt the following ad copy for the "
            f"{brief.target_region} market in {brief.target_language}.\n\n"
            f"Original headline: {original.headline}\n"
            f"Original body: {original.body}\n\n"
            f"Don't just translate literally — adapt idioms, cultural references, "
            f"and tone to resonate with {brief.target_audience} in {brief.target_region}.\n\n"
            f'Respond ONLY with JSON: {{"headline": "...", "body": "..."}}'
        )

        response = llm.invoke(prompt)
        data = parse_llm_json(response.content)
        localized[slug] = LocalizedCopy(
            language=brief.target_language,
            headline=data["headline"],
            body=data["body"],
        )

    return {"localized_copy": localized}
