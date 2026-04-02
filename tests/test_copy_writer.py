from unittest.mock import MagicMock, patch

from social_campaign.agents.copy_writer import write_copy
from social_campaign.models import (
    BrandConfig,
    CampaignBrief,
    CampaignState,
    CopyVariant,
    ProductConfig,
)


def _make_state() -> CampaignState:
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
        copy_variants={},
        localized_copy={},
        generated_images={},
        composited_assets={},
        brand_check_results={},
        legal_check_results={},
        output_dir="/tmp/out",
    )


@patch("social_campaign.agents.copy_writer.ChatOpenAI")
def test_write_copy_generates_for_all_products(mock_chat_cls):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content='{"headline": "Stay Fresh", "body": "Keep it cool all day."}'
    )
    mock_chat_cls.return_value = mock_llm

    state = _make_state()
    result = write_copy(state)

    assert "copy_variants" in result
    assert "product-a" in result["copy_variants"]
    assert "product-b" in result["copy_variants"]
    assert isinstance(result["copy_variants"]["product-a"], CopyVariant)
    assert mock_llm.invoke.call_count == 2
