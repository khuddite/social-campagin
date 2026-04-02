import json
from pathlib import Path

import pytest
from social_campaign.agents.brief_parser import parse_brief
from social_campaign.models import CampaignBrief, CampaignState


@pytest.fixture
def sample_brief_path(tmp_path: Path) -> Path:
    brief = {
        "campaign_name": "Test Campaign",
        "brand": {
            "name": "TestBrand",
            "colors": ["#FF0000"],
            "logo_path": "assets/logo.png",
            "guidelines": "Be fun.",
        },
        "products": [
            {
                "name": "Product A",
                "description": "Desc A",
                "hero_image": None,
                "key_features": ["fast"],
            },
            {
                "name": "Product B",
                "description": "Desc B",
                "hero_image": str(tmp_path / "existing.png"),
                "key_features": ["cool"],
            },
        ],
        "target_region": "US",
        "target_language": "en",
        "target_audience": "Everyone",
        "campaign_message": "Try it now",
        "aspect_ratios": ["1:1", "16:9"],
    }
    (tmp_path / "existing.png").write_bytes(b"fake png")
    brief_file = tmp_path / "brief.json"
    brief_file.write_text(json.dumps(brief))
    return brief_file


def test_parse_brief_returns_state(sample_brief_path: Path):
    state = parse_brief({"brief_path": str(sample_brief_path), "output_dir": "/tmp/out"})
    assert "brief" in state
    assert isinstance(state["brief"], CampaignBrief)
    assert len(state["brief"].products) == 2


def test_parse_brief_validates_existing_assets(sample_brief_path: Path, tmp_path: Path):
    state = parse_brief({"brief_path": str(sample_brief_path), "output_dir": "/tmp/out"})
    assert state["brief"].products[1].hero_image is not None
    assert state["brief"].products[0].hero_image is None


def test_parse_brief_nullifies_missing_asset(tmp_path: Path):
    brief = {
        "campaign_name": "Test",
        "brand": {"name": "X", "colors": ["#000"], "logo_path": "nonexistent.png", "guidelines": ""},
        "products": [{"name": "P", "description": "D", "hero_image": "/nonexistent/image.png", "key_features": ["x"]}],
        "target_region": "US",
        "target_language": "en",
        "target_audience": "All",
        "campaign_message": "Go",
        "aspect_ratios": ["1:1"],
    }
    brief_file = tmp_path / "brief.json"
    brief_file.write_text(json.dumps(brief))
    state = parse_brief({"brief_path": str(brief_file), "output_dir": "/tmp/out"})
    assert state["brief"].products[0].hero_image is None
