from pathlib import Path
from unittest.mock import patch

from PIL import Image

from social_campaign.agents.image_generator import generate_images
from social_campaign.models import (
    BrandConfig,
    CampaignBrief,
    CampaignState,
    ProductConfig,
)


def _make_state(tmp_path: Path) -> CampaignState:
    # Create a fake existing hero image for product B
    existing = tmp_path / "existing_hero.png"
    Image.new("RGB", (1024, 1024), "blue").save(existing)

    return CampaignState(
        brief=CampaignBrief(
            campaign_name="Test",
            brand=BrandConfig(
                name="X", colors=["#000"], logo_path="logo.png", guidelines=""
            ),
            products=[
                ProductConfig(
                    name="Product A",
                    description="Needs generation",
                    hero_image=None,
                    key_features=["new"],
                ),
                ProductConfig(
                    name="Product B",
                    description="Has existing image",
                    hero_image=str(existing),
                    key_features=["existing"],
                ),
            ],
            target_region="US",
            target_language="en",
            target_audience="All",
            campaign_message="Go",
            aspect_ratios=["1:1"],
        ),
        copy_variants={},
        localized_copy={},
        generated_images={},
        composited_assets={},
        output_dir=str(tmp_path / "output"),
    )


@patch("social_campaign.agents.image_generator.generate_transparent_image")
def test_generates_missing_and_skips_existing(mock_gen, tmp_path):
    fake_img = Image.new("RGBA", (1024, 1024), (0, 128, 0, 200))
    mock_gen.return_value = fake_img

    state = _make_state(tmp_path)
    result = generate_images(state)

    assert "product-a" in result["generated_images"]
    assert "product-b" in result["generated_images"]
    mock_gen.assert_called_once()  # Only called for Product A

    assert Path(result["generated_images"]["product-a"]).exists()
    assert Path(result["generated_images"]["product-b"]).exists()
