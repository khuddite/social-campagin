"""Pillow helpers for image resizing, cropping, and text overlay."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Target sizes for each aspect ratio
ASPECT_SIZES: dict[str, tuple[int, int]] = {
    "1:1": (1080, 1080),
    "9:16": (1080, 1920),
    "16:9": (1920, 1080),
}

# Try to load bundled font, fall back to default
_FONT_PATH = Path(__file__).parent.parent.parent.parent / "fonts" / "Inter-Bold.ttf"


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    try:
        return ImageFont.truetype(str(_FONT_PATH), size)
    except OSError:
        return ImageFont.load_default(size)


def prepare_hero_edit_canvas(
    hero: Image.Image,
    canvas_size: int = 1024,
    hero_width_ratio: float = 0.78,
    bottom_margin_ratio: float = 0.06,
) -> Image.Image:
    """Place the hero on a square transparent canvas for GPT Image edit (inpainting).

    Transparent pixels are filled by the API; the product stays anchored bottom-center
    so crops to 1:1, 9:16, and 16:9 keep the subject usable.
    """
    hero = hero.convert("RGBA")
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    hw, hh = hero.size
    if hw == 0 or hh == 0:
        return canvas

    max_w = int(canvas_size * hero_width_ratio)
    max_h = int(canvas_size * 0.88)
    scale = min(max_w / hw, max_h / hh)
    nw, nh = max(1, int(hw * scale)), max(1, int(hh * scale))
    hero = hero.resize((nw, nh), Image.LANCZOS)

    x = (canvas_size - nw) // 2
    y = canvas_size - nh - int(canvas_size * bottom_margin_ratio)
    y = max(0, min(y, canvas_size - nh))
    canvas.paste(hero, (x, y), hero)
    return canvas


def composite_hero_over_background(
    background: Image.Image,
    hero: Image.Image,
    *,
    hero_width_ratio: float = 0.78,
    bottom_margin_ratio: float = 0.06,
) -> Image.Image:
    """Place a product hero (e.g. transparent PNG cutout) on a full-bleed background, bottom-centered."""
    tw, th = background.size
    background = background.convert("RGBA")
    hero = hero.convert("RGBA")

    hw, hh = hero.size
    if hw == 0 or hh == 0:
        return background

    max_w = int(tw * hero_width_ratio)
    max_h = int(th * 0.88)
    scale = min(max_w / hw, max_h / hh)
    nw, nh = max(1, int(hw * scale)), max(1, int(hh * scale))
    hero = hero.resize((nw, nh), Image.LANCZOS)

    x = (tw - nw) // 2
    y = th - nh - int(th * bottom_margin_ratio)
    y = max(0, min(y, th - nh))

    layer = Image.new("RGBA", (tw, th), (0, 0, 0, 0))
    layer.paste(hero, (x, y), hero)
    return Image.alpha_composite(background, layer)


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


def _wrap_text(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    """Wrap text to fit within max_width pixels."""
    words = text.split()
    if not words:
        return text
    lines: list[str] = []
    current = words[0]
    for word in words[1:]:
        test = f"{current} {word}"
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] > max_width:
            lines.append(current)
            current = word
        else:
            current = test
    lines.append(current)
    return "\n".join(lines)


def overlay_text(
    img: Image.Image,
    headline: str,
    body: str,
    max_font_ratio: float = 0.06,
) -> Image.Image:
    """Overlay headline and body text with a semi-transparent background strip."""
    img = img.convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    headline_size = max(int(h * max_font_ratio), 20)
    body_size = max(int(headline_size * 0.6), 14)
    headline_font = _load_font(headline_size)
    body_font = _load_font(body_size)

    padding = int(w * 0.05)
    margin_bottom = int(h * 0.08)

    # Wrap text to fit within image
    text_max_width = w - padding * 2
    headline = _wrap_text(draw, headline, headline_font, text_max_width)
    body = _wrap_text(draw, body, body_font, text_max_width)

    body_bbox = draw.multiline_textbbox((0, 0), body, font=body_font)
    headline_bbox = draw.multiline_textbbox((0, 0), headline, font=headline_font)
    body_h = body_bbox[3] - body_bbox[1]
    headline_h = headline_bbox[3] - headline_bbox[1]

    total_text_h = headline_h + body_h + int(padding * 0.5)
    strip_top = h - margin_bottom - total_text_h - padding * 2

    draw.rectangle(
        [(0, strip_top), (w, strip_top + total_text_h + padding * 2)],
        fill=(0, 0, 0, 140),
    )

    headline_y = strip_top + padding
    draw.multiline_text((padding, headline_y), headline, fill="white", font=headline_font)

    body_y = headline_y + headline_h + int(padding * 0.5)
    draw.multiline_text((padding, body_y), body, fill=(255, 255, 255, 220), font=body_font)

    result = Image.alpha_composite(img, overlay)
    return result.convert("RGB")


def overlay_logo(
    img: Image.Image,
    logo_path: str,
    max_ratio: float = 0.12,
    padding: int = 20,
) -> Image.Image:
    """Place the brand logo in the top-right corner."""
    img = img.convert("RGBA")
    w, h = img.size

    try:
        logo = Image.open(logo_path).convert("RGBA")
    except FileNotFoundError:
        return img.convert("RGB")

    max_logo_w = int(w * max_ratio)
    logo_aspect = logo.width / logo.height
    logo_w = min(logo.width, max_logo_w)
    logo_h = int(logo_w / logo_aspect)
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

    x = w - logo_w - padding
    y = padding

    img.paste(logo, (x, y), logo)
    return img.convert("RGB")
