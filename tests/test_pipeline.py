import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from PIL import Image

from social_campaign.pipeline import build_pipeline


@patch("social_campaign.agents.brand_checker.ChatOpenAI")
@patch("social_campaign.agents.legal_checker.ChatOpenAI")
@patch("social_campaign.agents.localizer.ChatOpenAI")
@patch("social_campaign.agents.copy_writer.ChatOpenAI")
@patch("social_campaign.agents.image_generator.generate_image")
def test_full_pipeline(
    mock_gen_image,
    mock_copy_chat,
    mock_local_chat,
    mock_legal_chat,
    mock_brand_chat,
    tmp_path: Path,
):
    mock_gen_image.return_value = Image.new("RGB", (1024, 1024), "green")

    for mock_cls in [mock_copy_chat, mock_local_chat]:
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(
            content='{"headline": "Test Head", "body": "Test body text."}'
        )
        mock_cls.return_value = llm

    for mock_cls in [mock_brand_chat, mock_legal_chat]:
        llm = MagicMock()
        llm.invoke.return_value = MagicMock(
            content='{"passed": true, "details": "All good.", "flags": []}'
        )
        mock_cls.return_value = llm

    logo_path = tmp_path / "logo.png"
    Image.new("RGBA", (200, 100), (255, 255, 255, 200)).save(logo_path)

    brief = {
        "campaign_name": "Integration Test",
        "brand": {
            "name": "TestBrand",
            "colors": ["#FF0000"],
            "logo_path": str(logo_path),
            "guidelines": "Be awesome.",
        },
        "products": [
            {
                "name": "Test Product",
                "description": "A test product",
                "hero_image": None,
                "key_features": ["great"],
            }
        ],
        "target_region": "US",
        "target_language": "en",
        "target_audience": "Everyone",
        "campaign_message": "Try it",
        "aspect_ratios": ["1:1", "9:16", "16:9"],
    }
    brief_file = tmp_path / "brief.json"
    brief_file.write_text(json.dumps(brief))

    output_dir = tmp_path / "output"

    pipeline = build_pipeline()
    result = pipeline.invoke({
        "brief_path": str(brief_file),
        "output_dir": str(output_dir),
    })

    assert (output_dir / "test-product" / "1_1" / "campaign.png").exists()
    assert (output_dir / "test-product" / "9_16" / "campaign.png").exists()
    assert (output_dir / "test-product" / "16_9" / "campaign.png").exists()
    assert (output_dir / "campaign-report.html").exists()
