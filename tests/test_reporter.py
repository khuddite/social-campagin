from pathlib import Path

from PIL import Image

from social_campaign.agents.reporter import generate_report
from social_campaign.models import (
    BrandConfig,
    CampaignBrief,
    CampaignState,
    CopyVariant,
    LocalizedCopy,
    ProductConfig,
)


def test_generate_report_creates_html(tmp_path: Path):
    asset_dir = tmp_path / "output" / "product-a" / "1_1"
    asset_dir.mkdir(parents=True)
    img_path = asset_dir / "campaign.png"
    Image.new("RGB", (100, 100), "red").save(img_path)

    state = CampaignState(
        brief=CampaignBrief(
            campaign_name="Test Campaign",
            brand=BrandConfig(name="X", colors=["#000"], logo_path="logo.png", guidelines=""),
            products=[ProductConfig(name="Product A", description="D", hero_image=None, key_features=["x"])],
            target_region="US", target_language="en", target_audience="All",
            campaign_message="Go", aspect_ratios=["1:1"],
        ),
        copy_variants={"product-a": CopyVariant(headline="Go!", body="Try it.")},
        localized_copy={"product-a": LocalizedCopy(language="en", headline="Go!", body="Try it.")},
        generated_images={"product-a": str(img_path)},
        composited_assets={"product-a": {"1_1": str(img_path)}},
        output_dir=str(tmp_path / "output"),
    )

    result = generate_report(state)
    report_path = Path(tmp_path / "output" / "campaign-report.html")
    assert report_path.exists()

    html = report_path.read_text()
    assert "Test Campaign" in html
    assert "Product A" in html
    assert "Go!" in html
