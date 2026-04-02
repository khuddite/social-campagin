from pathlib import Path

from PIL import Image

from social_campaign.agents.compositor import composite_assets
from social_campaign.models import (
    BrandConfig,
    CampaignBrief,
    CampaignState,
    LocalizedCopy,
    ProductConfig,
)


def test_composite_creates_all_ratio_files(tmp_path: Path):
    hero_path = tmp_path / "hero.png"
    Image.new("RGB", (1024, 1024), "green").save(hero_path)

    logo_path = tmp_path / "logo.png"
    Image.new("RGBA", (200, 100), (255, 0, 0, 200)).save(logo_path)

    output_dir = tmp_path / "output"

    state = CampaignState(
        brief=CampaignBrief(
            campaign_name="Test",
            brand=BrandConfig(
                name="X", colors=["#000"], logo_path=str(logo_path), guidelines="",
            ),
            products=[
                ProductConfig(name="Product A", description="D", hero_image=None, key_features=["x"]),
            ],
            target_region="US",
            target_language="en",
            target_audience="All",
            campaign_message="Go",
            aspect_ratios=["1:1", "9:16", "16:9"],
        ),
        copy_variants={},
        localized_copy={
            "product-a": LocalizedCopy(language="en", headline="Test Headline", body="Test body text."),
        },
        generated_images={"product-a": str(hero_path)},
        composited_assets={},
        brand_check_results={},
        legal_check_results={},
        output_dir=str(output_dir),
    )

    result = composite_assets(state)

    assert "product-a" in result["composited_assets"]
    assets = result["composited_assets"]["product-a"]
    assert set(assets.keys()) == {"1_1", "9_16", "16_9"}

    for ratio_key, path in assets.items():
        assert Path(path).exists()
        img = Image.open(path)
        if ratio_key == "1_1":
            assert img.size == (1080, 1080)
        elif ratio_key == "9_16":
            assert img.size == (1080, 1920)
        elif ratio_key == "16_9":
            assert img.size == (1920, 1080)
