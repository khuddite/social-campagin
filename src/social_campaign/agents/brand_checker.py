"""Node 6: Check composited assets for brand compliance using GPT-4o vision."""

from __future__ import annotations

import base64
from pathlib import Path

from langchain_openai import ChatOpenAI

from social_campaign.models import CampaignState, CheckResult
from social_campaign.utils.llm_utils import parse_llm_json


def _image_to_base64(path: str) -> str:
    data = Path(path).read_bytes()
    return base64.b64encode(data).decode()


def check_brand(state: CampaignState) -> dict:
    """Analyze composited images for brand compliance."""
    brief = state["brief"]
    composited = state["composited_assets"]
    llm = ChatOpenAI(model="gpt-4o", temperature=0)

    results: dict[str, CheckResult] = {}

    for product in brief.products:
        slug = product.slug
        assets = composited[slug]

        check_path = assets.get("1_1") or next(iter(assets.values()))
        img_b64 = _image_to_base64(check_path)

        prompt = [
            {
                "type": "text",
                "text": (
                    f"You are a brand compliance reviewer.\n"
                    f"Brand: {brief.brand.name}\n"
                    f"Brand colors: {', '.join(brief.brand.colors)}\n"
                    f"Brand guidelines: {brief.brand.guidelines}\n\n"
                    f"Analyze this social media ad image for brand compliance:\n"
                    f"1. Is the brand logo visible?\n"
                    f"2. Are brand colors used appropriately?\n"
                    f"3. Does the tone match brand guidelines?\n\n"
                    f"Respond ONLY with JSON: "
                    f'{{"passed": true/false, "details": "...", "flags": ["issue1", ...]}}'
                ),
            },
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/png;base64,{img_b64}"},
            },
        ]

        response = llm.invoke([{"role": "user", "content": prompt}])
        data = parse_llm_json(response.content)
        results[slug] = CheckResult(**data)

    return {"brand_check_results": results}
