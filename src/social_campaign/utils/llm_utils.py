"""Utilities for working with LLM responses."""

from __future__ import annotations

import json
import re

LLM_MODEL = "gpt-4o"


def parse_llm_json(raw: str) -> dict:
    """Parse JSON from LLM response, stripping markdown code fences if present."""
    text = raw.strip()
    # Strip markdown code fences
    if text.startswith("```"):
        text = re.sub(r"^```\w*\n?", "", text)
        text = re.sub(r"\n?```$", "", text)
    return json.loads(text.strip())
