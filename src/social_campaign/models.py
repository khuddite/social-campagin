"""Pydantic models for campaign brief, pipeline state, and results."""

from __future__ import annotations

import re
from typing import TypedDict

from pydantic import BaseModel, Field, field_validator


class BrandConfig(BaseModel):
    """Brand identity and guidelines."""

    name: str
    colors: list[str]
    logo_path: str
    guidelines: str


class ProductConfig(BaseModel):
    """A single product in the campaign."""

    name: str
    description: str
    hero_image: str | None = None
    key_features: list[str]

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")


class CampaignBrief(BaseModel):
    """The full campaign brief input."""

    campaign_name: str
    brand: BrandConfig
    products: list[ProductConfig]
    target_region: str
    target_language: str
    target_audience: str
    campaign_message: str
    aspect_ratios: list[str] = Field(default=["1:1", "9:16", "16:9"])

    @field_validator("products")
    @classmethod
    def at_least_one_product(cls, v: list[ProductConfig]) -> list[ProductConfig]:
        if len(v) == 0:
            raise ValueError("At least one product is required.")
        return v


class CopyVariant(BaseModel):
    """Generated ad copy for a product."""

    headline: str
    body: str


class LocalizedCopy(BaseModel):
    """Localized version of ad copy."""

    language: str
    headline: str
    body: str


class BackgroundPlan(BaseModel):
    """Creative direction for an AI-generated ad background (environment only, no product)."""

    slug: str = Field(default="", description="Product slug this plan belongs to.")
    scene_description: str = Field(
        ...,
        description="Full-bleed environment or abstract space; must not include the product itself.",
    )
    mood: str = Field(..., description="Emotional tone for the scene (e.g. energetic, serene).")
    color_direction: str = Field(
        ...,
        description="Palette and lighting cues that harmonize with brand colors.",
    )


class BackgroundPlansResponse(BaseModel):
    """Structured output wrapper: one BackgroundPlan per product."""

    plans: list[BackgroundPlan] = Field(
        ...,
        description="One entry per product slug.",
    )


class CampaignState(TypedDict, total=False):
    """Shared state flowing through the LangGraph pipeline."""

    brief: CampaignBrief
    copy_variants: dict[str, CopyVariant]
    localized_copy: dict[str, LocalizedCopy]
    background_plans: dict[str, BackgroundPlan]
    generated_images: dict[str, str]
    generated_backgrounds: dict[str, str]
    composited_assets: dict[str, dict[str, str]]
    output_dir: str
    report_path: str
