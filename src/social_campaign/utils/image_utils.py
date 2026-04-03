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

# Font paths — headline uses a bold display font, body uses an elegant sans-serif
_FONTS_DIR = Path(__file__).parent.parent.parent.parent / "fonts"
_HEADLINE_FONT_PATH = _FONTS_DIR / "BebasNeue-Regular.ttf"
_BODY_FONT_PATH = _FONTS_DIR / "Raleway-Medium.ttf"
_FALLBACK_FONT_PATH = _FONTS_DIR / "Inter-Bold.ttf"


def _load_font(size: int, role: str = "headline") -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    """Load a font by role: 'headline' for display font, 'body' for body font."""
    primary = _HEADLINE_FONT_PATH if role == "headline" else _BODY_FONT_PATH
    for path in [primary, _FALLBACK_FONT_PATH]:
        try:
            return ImageFont.truetype(str(path), size)
        except OSError:
            continue
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
    hero_fill_ratio: float = 0.85,
    vertical_offset_ratio: float = -0.05,
) -> Image.Image:
    """Place a product hero centered on a full-bleed background.

    The product is scaled so its largest dimension fills exactly
    ``hero_fill_ratio`` of the corresponding image dimension (85% by default).
    """
    tw, th = background.size
    background = background.convert("RGBA")
    hero = hero.convert("RGBA")

    hw, hh = hero.size
    if hw == 0 or hh == 0:
        return background

    # Scale so the dominant axis fills exactly hero_fill_ratio of the frame
    scale = max((tw * hero_fill_ratio) / hw, (th * hero_fill_ratio) / hh)
    # Don't exceed frame bounds
    scale = min(scale, tw * 0.95 / hw, th * 0.92 / hh)
    nw, nh = max(1, int(hw * scale)), max(1, int(hh * scale))
    hero = hero.resize((nw, nh), Image.LANCZOS)

    # Center horizontally, center vertically with slight upward offset
    x = (tw - nw) // 2
    y = (th - nh) // 2 + int(th * vertical_offset_ratio)
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


def overlay_text_behind(
    img: Image.Image,
    headline: str,
    body: str,
) -> Image.Image:
    """Overlay a large headline in the lower-center that the product will intersect.

    This is drawn BEFORE the product is composited, so the product appears
    in front of the text for an editorial, eye-catching look.
    The headline is big and bold; the body sits below it in a smaller font.
    """
    img = img.convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Large headline — sized to be impactful and overlap with the product area
    headline_size = max(int(h * 0.07), 28)
    body_size = max(int(headline_size * 0.35), 12)
    headline_font = _load_font(headline_size, role="headline")
    body_font = _load_font(body_size, role="body")

    headline = headline.upper()

    padding = int(w * 0.05)
    text_max_width = w - padding * 2
    headline = _wrap_text(draw, headline, headline_font, text_max_width)
    body = _wrap_text(draw, body, body_font, text_max_width)

    headline_bbox = draw.multiline_textbbox((0, 0), headline, font=headline_font)
    body_bbox = draw.multiline_textbbox((0, 0), body, font=body_font)
    headline_h = headline_bbox[3] - headline_bbox[1]
    body_h = body_bbox[3] - body_bbox[1]

    # Position headline in the lower third — product will overlap it from above
    headline_y = int(h * 0.68)
    body_y = headline_y + headline_h + int(padding * 0.4)

    # Draw headline with a subtle shadow for depth
    for dx, dy in [(2, 2), (-1, -1)]:
        draw.multiline_text(
            (padding + dx, headline_y + dy), headline,
            fill=(0, 0, 0, 100), font=headline_font,
        )
    draw.multiline_text(
        (padding, headline_y), headline,
        fill=(255, 255, 255, 240), font=headline_font,
    )

    # Body text below with slight transparency
    draw.multiline_text(
        (padding, body_y), body,
        fill=(255, 255, 255, 190), font=body_font,
    )

    result = Image.alpha_composite(img, overlay)
    return result.convert("RGBA")


def overlay_logo(
    img: Image.Image,
    logo_path: str,
    max_ratio: float = 0.22,
    padding_ratio: float = 0.025,
) -> Image.Image:
    """Place the brand logo in the top-right corner, sized prominently."""
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

    pad = int(w * padding_ratio)
    x = w - logo_w - pad
    y = pad

    img.paste(logo, (x, y), logo)
    return img.convert("RGB")
