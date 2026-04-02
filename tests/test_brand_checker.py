from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from social_campaign.agents.brand_checker import check_brand
from social_campaign.models import (
    BrandConfig,
    CampaignBrief,
    CampaignState,
    CheckResult,
    LocalizedCopy,
    ProductConfig,
)


def _make_state(tmp_path: Path) -> CampaignState:
    asset_dir = tmp_path / "output" / "product-a" / "1_1"
    asset_dir.mkdir(parents=True)
    img_path = asset_dir / "campaign.png"
    Image.new("RGB", (1080, 1080), "red").save(img_path)

    return CampaignState(
        brief=CampaignBrief(
            campaign_name="Test",
            brand=BrandConfig(
                name="FreshCo", colors=["#00A86B", "#FFFFFF"], logo_path="logo.png",
                guidelines="Tone: upbeat. Always include logo.",
            ),
            products=[ProductConfig(name="Product A", description="D", hero_image=None, key_features=["x"])],
            target_region="US", target_language="en", target_audience="All",
            campaign_message="Go", aspect_ratios=["1:1"],
        ),
        copy_variants={},
        localized_copy={"product-a": LocalizedCopy(language="en", headline="Go!", body="Try it.")},
        generated_images={},
        composited_assets={"product-a": {"1_1": str(img_path)}},
        brand_check_results={},
        legal_check_results={},
        output_dir=str(tmp_path / "output"),
    )


@patch("social_campaign.agents.brand_checker.ChatOpenAI")
def test_check_brand_returns_results(mock_chat_cls, tmp_path):
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = MagicMock(
        content='{"passed": true, "details": "Brand compliant.", "flags": []}'
    )
    mock_chat_cls.return_value = mock_llm

    state = _make_state(tmp_path)
    result = check_brand(state)

    assert "brand_check_results" in result
    assert "product-a" in result["brand_check_results"]
    cr = result["brand_check_results"]["product-a"]
    assert isinstance(cr, CheckResult)
    assert cr.passed is True
