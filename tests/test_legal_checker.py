from unittest.mock import MagicMock, patch

from social_campaign.agents.legal_checker import check_legal
from social_campaign.models import (
    BrandConfig,
    CampaignBrief,
    CampaignState,
    CheckResult,
    CopyVariant,
    LocalizedCopy,
    ProductConfig,
)


def _make_state() -> CampaignState:
    return CampaignState(
        brief=CampaignBrief(
            campaign_name="Test",
            brand=BrandConfig(
                name="FreshCo", colors=["#00A86B"], logo_path="logo.png",
                guidelines="Never use 'cheap' or 'budget'.",
            ),
            products=[ProductConfig(name="Product A", description="D", hero_image=None, key_features=["x"])],
            target_region="US", target_language="en", target_audience="All",
            campaign_message="Go", aspect_ratios=["1:1"],
        ),
        copy_variants={"product-a": CopyVariant(headline="Go!", body="No added sugar.")},
        localized_copy={"product-a": LocalizedCopy(language="en", headline="Go!", body="No added sugar.")},
        generated_images={},
        composited_assets={},
        brand_check_results={},
        legal_check_results={},
        output_dir="/tmp/out",
    )


@patch("social_campaign.agents.legal_checker.ChatOpenAI")
def test_check_legal_returns_results(mock_chat_cls):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content='{"passed": false, "details": "Claim needs substantiation.", "flags": ["no added sugar — needs proof"]}'
    )
    mock_chat_cls.return_value = mock_llm

    state = _make_state()
    result = check_legal(state)

    assert "legal_check_results" in result
    cr = result["legal_check_results"]["product-a"]
    assert isinstance(cr, CheckResult)
    assert cr.passed is False
    assert len(cr.flags) == 1
