from pathlib import Path

from PIL import Image

from social_campaign.utils.image_utils import (
    center_crop_to_ratio,
    composite_hero_over_background,
    overlay_logo,
    overlay_text,
    prepare_hero_edit_canvas,
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


def test_prepare_hero_edit_canvas_is_square_rgba():
    hero = Image.new("RGBA", (200, 200), (255, 0, 0, 255))
    canvas = prepare_hero_edit_canvas(hero, canvas_size=1024)
    assert canvas.size == (1024, 1024)
    assert canvas.mode == "RGBA"


def test_composite_hero_over_background():
    bg = Image.new("RGB", (1080, 1080), "gray")
    hero = Image.new("RGBA", (400, 400), (255, 0, 0, 200))
    out = composite_hero_over_background(bg, hero)
    assert out.size == (1080, 1080)
    assert out.mode == "RGBA"


def test_overlay_logo(tmp_path: Path):
    img = Image.new("RGB", (1080, 1080), "blue")
    logo = Image.new("RGBA", (200, 100), (255, 0, 0, 200))
    logo_path = tmp_path / "logo.png"
    logo.save(logo_path)

    result = overlay_logo(img, str(logo_path))
    assert isinstance(result, Image.Image)
    assert result.size == (1080, 1080)
