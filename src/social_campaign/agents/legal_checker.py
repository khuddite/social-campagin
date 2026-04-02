"""Node 7: Scan ad copy for legal compliance issues."""

from __future__ import annotations

from langchain_openai import ChatOpenAI

from social_campaign.models import CampaignState, CheckResult
from social_campaign.utils.llm_utils import parse_llm_json


def check_legal(state: CampaignState) -> dict:
    """Check all copy variants for legal issues."""
    brief = state["brief"]
    copy_variants = state["copy_variants"]
    localized_copy = state["localized_copy"]
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    results: dict[str, CheckResult] = {}

    for product in brief.products:
        slug = product.slug
        original = copy_variants[slug]
        localized = localized_copy[slug]

        prompt = (
            f"You are a legal compliance reviewer for advertising content.\n"
            f"Brand: {brief.brand.name}\n"
            f"Brand guidelines: {brief.brand.guidelines}\n"
            f"Target region: {brief.target_region}\n\n"
            f"Review the following ad copy for legal issues:\n"
            f"Original headline: {original.headline}\n"
            f"Original body: {original.body}\n"
            f"Localized headline ({localized.language}): {localized.headline}\n"
            f"Localized body ({localized.language}): {localized.body}\n\n"
            f"Check for:\n"
            f"1. Prohibited words from brand guidelines\n"
            f"2. Unsubstantiated health/nutrition claims\n"
            f"3. Misleading statements\n"
            f"4. Region-specific advertising regulations\n\n"
            f"Respond ONLY with JSON: "
            f'{{"passed": true/false, "details": "...", "flags": ["issue1", ...]}}'
        )

        response = llm.invoke(prompt)
        data = parse_llm_json(response.content)
        results[slug] = CheckResult(**data)

    return {"legal_check_results": results}
