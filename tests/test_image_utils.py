from pathlib import Path

from PIL import Image

from social_campaign.utils.image_utils import (
    center_crop_to_ratio,
    overlay_logo,
    overlay_text,
)


def test_center_crop_1_1():
    img = Image.new("RGB", (1024, 1024), "red")
    result = center_crop_to_ratio(img, "1:1")
    assert result.size == (1080, 1080)


def test_center_crop_9_16():
    img = Image.new("RGB", (1024, 1024), "red")
    result = center_crop_to_ratio(img, "9:16")
    assert result.size == (1080, 1920)


def test_center_crop_16_9():
    img = Image.new("RGB", (1024, 1024), "red")
    result = center_crop_to_ratio(img, "16:9")
    assert result.size == (1920, 1080)


def test_overlay_text_returns_image():
    img = Image.new("RGB", (1080, 1080), "blue")
    result = overlay_text(img, headline="Hello World", body="This is a test.")
    assert isinstance(result, Image.Image)
    assert result.size == (1080, 1080)


def test_overlay_logo(tmp_path: Path):
    img = Image.new("RGB", (1080, 1080), "blue")
    logo = Image.new("RGBA", (200, 100), (255, 0, 0, 200))
    logo_path = tmp_path / "logo.png"
    logo.save(logo_path)

    result = overlay_logo(img, str(logo_path))
    assert isinstance(result, Image.Image)
    assert result.size == (1080, 1080)
