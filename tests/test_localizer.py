from unittest.mock import MagicMock, patch

from social_campaign.agents.localizer import localize_copy
from social_campaign.models import (
    BrandConfig,
    CampaignBrief,
    CampaignState,
    CopyVariant,
    LocalizedCopy,
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
                    key_features=["fast"],
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
        },
        localized_copy={},
        generated_images={},
        composited_assets={},
        output_dir="/tmp/out",
    )


@patch("social_campaign.agents.localizer.ChatOpenAI")
def test_localize_copy_translates_and_adapts(mock_chat_cls):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content='{"headline": "Fique Fresco", "body": "Mantenha a frescura."}'
    )
    mock_chat_cls.return_value = mock_llm

    state = _make_state()
    result = localize_copy(state)

    assert "localized_copy" in result
    assert "product-a" in result["localized_copy"]
    lc = result["localized_copy"]["product-a"]
    assert isinstance(lc, LocalizedCopy)
    assert lc.language == "pt-BR"
    assert lc.headline == "Fique Fresco"
