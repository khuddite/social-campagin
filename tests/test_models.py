import pytest
from social_campaign.models import (
    BrandConfig,
    CampaignBrief,
    CopyVariant,
    ProductConfig,
)


def test_valid_brief():
    brief = CampaignBrief(
        campaign_name="Summer Refresh",
        brand=BrandConfig(
            name="FreshCo",
            colors=["#00A86B", "#FFFFFF"],
            logo_path="assets/logo.png",
            guidelines="Tone: upbeat.",
        ),
        products=[
            ProductConfig(
                name="Citrus Water",
                description="Sparkling water",
                hero_image="assets/citrus.png",
                key_features=["refreshing"],
            ),
            ProductConfig(
                name="Berry Smoothie",
                description="Mixed berry smoothie",
                hero_image=None,
                key_features=["real fruit"],
            ),
        ],
        target_region="Brazil",
        target_language="pt-BR",
        target_audience="Millennials, 25-35",
        campaign_message="Beat the heat",
        aspect_ratios=["1:1", "9:16", "16:9"],
    )
    assert brief.campaign_name == "Summer Refresh"
    assert len(brief.products) == 2
    assert brief.products[1].hero_image is None


def test_brief_requires_at_least_one_product():
    with pytest.raises(ValueError):
        CampaignBrief(
            campaign_name="Empty",
            brand=BrandConfig(
                name="X", colors=["#000"], logo_path="logo.png", guidelines=""
            ),
            products=[],
            target_region="US",
            target_language="en",
            target_audience="Everyone",
            campaign_message="Hello",
            aspect_ratios=["1:1"],
        )


def test_product_slug():
    p = ProductConfig(
        name="Citrus Burst Sparkling Water",
        description="Water",
        hero_image=None,
        key_features=["fresh"],
    )
    assert p.slug == "citrus-burst-sparkling-water"


def test_copy_variant():
    cv = CopyVariant(headline="Fresh & Cool", body="Stay refreshed all summer.")
    assert cv.headline == "Fresh & Cool"
