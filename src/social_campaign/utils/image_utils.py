"""Pillow helpers for image resizing, cropping, and text overlay."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont, ImageText

# Target sizes for each aspect ratio
ASPECT_SIZES: dict[str, tuple[int, int]] = {
    "1:1": (1080, 1080),
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
}

# Font paths — headline uses a playful cinematic font, body uses an elegant sans-serif
_FONTS_DIR = Path(__file__).parent.parent.parent.parent / "fonts"
_HEADLINE_FONT_PATH = _FONTS_DIR / "PermanentMarker-Regular.ttf"
_BODY_FONT_PATH = _FONTS_DIR / "Raleway-Medium.ttf"
_FALLBACK_FONT_PATH = _FONTS_DIR / "Righteous-Regular.ttf"

# Universal fallback for non-Latin scripts (Japanese, Chinese, Korean, Arabic, etc.)
_CJK_FONT_PATH = _FONTS_DIR / "ArialUnicode.ttf"


def _has_non_latin(text: str) -> bool:
    """Return True if text contains characters outside the Basic Latin + Latin Extended range."""
    for ch in text:
        cp = ord(ch)
        if cp > 0x024F and ch not in " \t\n\r.,!?;:'\"-—–…()[]{}":
            return True
    return False


def _load_font(size: int, role: str = "headline", text: str = "") -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a font by role, falling back to a CJK-capable font for non-Latin text."""
    if text and _has_non_latin(text):
        try:
            return ImageFont.truetype(str(_CJK_FONT_PATH), size)
        except OSError:
            pass
    primary = _HEADLINE_FONT_PATH if role == "headline" else _BODY_FONT_PATH
    for path in [primary, _FALLBACK_FONT_PATH]:
        try:
            return ImageFont.truetype(str(path), size)
        except OSError:
            continue
    return ImageFont.load_default(size)


def composite_hero_over_background(
    background: Image.Image,
    hero: Image.Image,
    *,
    vertical_offset_ratio: float = -0.05,
) -> Image.Image:
    """Place a product hero centered on a full-bleed background.

    The hero is scaled so its largest side fits within *fill_ratio* of the
    background's smaller dimension — simple, works for any aspect ratio.
    """
    FILL_RATIO = 0.5

    tw, th = background.size
    background = background.convert("RGBA")
    hero = hero.convert("RGBA")

    # Trim transparent padding so we scale based on actual product pixels
    bbox = hero.getchannel("A").getbbox()
    if bbox:
        hero = hero.crop(bbox)

    hw, hh = hero.size
    if hw == 0 or hh == 0:
        return background

    scale = FILL_RATIO / max(hw / tw, hh / th)

    nw, nh = int(hw * scale), int(hh * scale)
    hero = hero.resize((nw, nh), Image.LANCZOS)

    # Center horizontally, center vertically with slight upward offset
    x = (tw - nw) // 2
    y = (th - nh) // 2 + int(th * vertical_offset_ratio)

    canvas = background.copy()
    canvas.paste(hero, (x, y), hero)
    return canvas


def center_crop_to_ratio(img: Image.Image, ratio: str) -> Image.Image:
    """Crop from center and resize to the target aspect ratio dimensions."""
    target_w, target_h = ASPECT_SIZES[ratio]
    target_aspect = target_w / target_h
    src_w, src_h = img.size
    src_aspect = src_w / src_h

    if src_aspect > target_aspect:
        new_w = int(src_h * target_aspect)
        left = (src_w - new_w) // 2
        img = img.crop((left, 0, left + new_w, src_h))
    elif src_aspect < target_aspect:
        new_h = int(src_w / target_aspect)
        top = (src_h - new_h) // 2
        img = img.crop((0, top, src_w, top + new_h))

    return img.resize((target_w, target_h), Image.LANCZOS)


def overlay_text_panel(
    img: Image.Image,
    headline: str,
    body: str,
    *,
    padding_ratio: float = 0.025,
) -> Image.Image:
    """Overlay headline + body at the bottom with a semi-transparent panel.

    *padding_ratio* controls the bottom margin between the panel and the
    image edge, expressed as a fraction of the background height.
    """
    img = img.convert("RGBA")
    w, h = img.size
    bmargin = int(h * padding_ratio)
    hpad = int(w * 0.04)

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    headline_size = int(h * 0.048)
    body_size = int(headline_size * 0.35)
    headline_font = _load_font(headline_size, role="headline", text=headline)
    body_font = _load_font(body_size, role="body", text=body)

    if not _has_non_latin(headline):
        headline = headline.upper()

    text_max_width = w - hpad * 2
    hl = ImageText.Text(headline, headline_font)
    hl.wrap(text_max_width)
    bd = ImageText.Text(body, body_font)
    bd.wrap(text_max_width)

    hl_bbox = hl.get_bbox()
    bd_bbox = bd.get_bbox()
    headline_h = hl_bbox[3] - hl_bbox[1]
    body_h = bd_bbox[3] - bd_bbox[1]
    vpad = int(h * 0.02)

    panel_bottom = h - bmargin
    text_overlay_height = 3 * vpad + headline_h + body_h
    panel_top = panel_bottom - text_overlay_height
    draw.rectangle([(0, panel_top), (w, panel_bottom)], fill=(0, 0, 0, 160))

    headline_y = panel_top + vpad
    draw.text((hpad, headline_y), hl, fill=(255, 255, 255, 255))

    body_y = headline_y + headline_h + vpad
    draw.text((hpad, body_y), bd, fill=(255, 255, 255, 200))

    return Image.alpha_composite(img, overlay)


def overlay_logo(
    img: Image.Image,
    logo_path: str,
    max_ratio: float = 0.22,
    padding_ratio: float = 0.025,
) -> Image.Image:
    """Place the brand logo in the top-right corner with a glow for visibility."""
    img = img.convert("RGBA")
    w, h = img.size

    try:
        logo = Image.open(logo_path).convert("RGBA")
    except FileNotFoundError:
        return img.convert("RGB")

    logo_aspect = logo.width / logo.height
    logo_w = int(w * max_ratio)
    logo_h = int(logo_w / logo_aspect)
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

    pad = int(w * padding_ratio)
    x = w - logo_w - pad
    y = pad

    img.paste(logo, (x, y), logo)
    return img.convert("RGB")
