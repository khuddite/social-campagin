"""Shared test fixtures."""

import pytest

from social_campaign.models import (
    BrandConfig,
    CampaignBrief,
    CampaignState,
    CopyVariant,
    ProductConfig,
)


@pytest.fixture()
def campaign_state() -> CampaignState:
    """A minimal CampaignState useful for testing copy_writer, localizer, etc."""
    return CampaignState(
        brief=CampaignBrief(
            campaign_name="Test",
            brand=BrandConfig(
                name="FreshCo",
                colors=["#00A86B"],
                logo_path="logo.png",
                guidelines="Tone: upbeat.",
            ),
            products=[
                ProductConfig(
                    name="Product A",
                    description="A great product",
                    hero_image=None,
                    key_features=["fast", "cool"],
                ),
                ProductConfig(
                    name="Product B",
                    description="Another product",
                    hero_image=None,
                    key_features=["smart"],
                ),
            ],
            target_region="Brazil",
            target_language="pt-BR",
            target_audience="Millennials",
            campaign_message="Stay fresh",
            aspect_ratios=["1:1"],
        ),
        copy_variants={
            "product-a": CopyVariant(headline="Stay Fresh", body="Keep it cool."),
            "product-b": CopyVariant(headline="Be Smart", body="Think ahead."),
        },
        localized_copy={},
        generated_images={},
        composited_assets={},
        output_dir="/tmp/out",
    )
