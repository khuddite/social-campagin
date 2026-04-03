"""LangGraph StateGraph assembly for the campaign pipeline."""

from __future__ import annotations

from langgraph.graph import END, START, StateGraph

from social_campaign.agents.background_generator import generate_backgrounds
from social_campaign.agents.background_planner import plan_backgrounds
from social_campaign.agents.brief_parser import parse_brief
from social_campaign.agents.compositor import composite_assets
from social_campaign.agents.copy_writer import write_copy
from social_campaign.agents.image_generator import generate_images
from social_campaign.agents.localizer import localize_copy
from social_campaign.agents.reporter import generate_report


def build_pipeline() -> StateGraph:
    """Construct and compile the campaign pipeline."""
    builder = StateGraph(dict)

    builder.add_node("parse_brief", parse_brief)
    builder.add_node("write_copy", write_copy)
    builder.add_node("localize_copy", localize_copy)
    builder.add_node("plan_backgrounds", plan_backgrounds)
    builder.add_node("generate_images", generate_images)
    builder.add_node("generate_backgrounds", generate_backgrounds)
    builder.add_node("composite_assets", composite_assets)
    builder.add_node("generate_report", generate_report)

    builder.add_edge(START, "parse_brief")
    builder.add_edge("parse_brief", "write_copy")
    builder.add_edge("write_copy", "localize_copy")
    builder.add_edge("localize_copy", "plan_backgrounds")
    builder.add_edge("plan_backgrounds", "generate_images")
    builder.add_edge("generate_images", "generate_backgrounds")
    builder.add_edge("generate_backgrounds", "composite_assets")
    builder.add_edge("composite_assets", "generate_report")
    builder.add_edge("generate_report", END)

    return builder.compile()
