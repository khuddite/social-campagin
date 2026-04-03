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


class CampaignState(TypedDict, total=False):
    """Shared state flowing through the LangGraph pipeline."""

    brief: CampaignBrief
    copy_variants: dict[str, CopyVariant]
    localized_copy: dict[str, LocalizedCopy]
    generated_images: dict[str, str]
    composited_assets: dict[str, dict[str, str]]
    output_dir: str
    report_path: str
