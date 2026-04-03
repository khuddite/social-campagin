"""Pillow helpers for image resizing, cropping, and text overlay."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

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
    vertical_offset_ratio: float = -0.05,
) -> Image.Image:
    """Place a product hero centered on a full-bleed background.

    Scaling adapts to aspect ratio: tall frames (9:16) use the width as the
    constraint so the product fills the horizontal space aggressively.
    Square and wide frames use the larger dimension.
    """
    tw, th = background.size
    background = background.convert("RGBA")
    hero = hero.convert("RGBA")

    hw, hh = hero.size
    if hw == 0 or hh == 0:
        return background

    aspect = tw / th  # <1 = tall, 1 = square, >1 = wide

    hero_aspect = hw / hh  # >1 = landscape hero, <1 = portrait hero

    if aspect < 0.7:
        # Tall frame (9:16)
        if hero_aspect > 1.2:
            # Landscape hero on tall frame — scale by height to make it
            # dominant. Width will bleed past edges (common ad technique).
            scale = (th * 0.55) / hh
        else:
            # Portrait/square hero — fill 95% width
            scale = (tw * 0.95) / hw
            scale = min(scale, th * 0.75 / hh)
    elif aspect > 1.3:
        # Wide frame (16:9)
        scale = (th * 0.80) / hh
        scale = min(scale, tw * 0.70 / hw)
    else:
        # Square (1:1)
        scale = (tw * 0.90) / hw
        scale = min(scale, th * 0.80 / hh)

    nw, nh = max(1, int(hw * scale)), max(1, int(hh * scale))
    hero = hero.resize((nw, nh), Image.LANCZOS)

    # Center horizontally, center vertically with slight upward offset
    x = (tw - nw) // 2
    y = (th - nh) // 2 + int(th * vertical_offset_ratio)

    # Composite on an oversized canvas then crop — handles bleed gracefully
    canvas_w = max(tw, nw + abs(x) * 2)
    canvas_h = max(th, nh + abs(y) * 2)
    ox = (canvas_w - tw) // 2  # offset to center the background on canvas
    oy = (canvas_h - th) // 2

    canvas = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    canvas.paste(background, (ox, oy))
    layer = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    layer.paste(hero, (ox + x, oy + y), hero)
    canvas = Image.alpha_composite(canvas, layer)

    # Crop back to target size
    return canvas.crop((ox, oy, ox + tw, oy + th))


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
    """Overlay headline + body in the lower portion with a frosted backing.

    Drawn BEFORE the product is composited so the product overlaps the top
    edge of the text area, creating an editorial intersecting layout.
    A semi-transparent dark panel behind the text ensures readability
    regardless of the background image.
    """
    img = img.convert("RGBA")
    w, h = img.size

    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    # Smaller, tighter text
    headline_size = max(int(h * 0.048), 22)
    body_size = max(int(headline_size * 0.35), 11)
    headline_font = _load_font(headline_size, role="headline", text=headline)
    body_font = _load_font(body_size, role="body", text=body)

    # Only uppercase for Latin scripts — CJK scripts don't have case
    if not _has_non_latin(headline):
        headline = headline.upper()

    padding = int(w * 0.04)
    text_max_width = w - padding * 2
    headline = _wrap_text(draw, headline, headline_font, text_max_width)
    body = _wrap_text(draw, body, body_font, text_max_width)

    headline_bbox = draw.multiline_textbbox((0, 0), headline, font=headline_font)
    body_bbox = draw.multiline_textbbox((0, 0), body, font=body_font)
    headline_h = headline_bbox[3] - headline_bbox[1]
    body_h = body_bbox[3] - body_bbox[1]

    gap = int(padding * 0.6)
    total_text_h = headline_h + gap + body_h
    panel_pad = int(padding * 0.7)
    total_block_h = total_text_h + panel_pad * 2

    # Position: anchor the bottom of the text block to the bottom of the image
    margin_bottom = int(h * 0.02)
    panel_bottom = h - margin_bottom
    panel_top = panel_bottom - total_block_h
    text_top = panel_top + panel_pad

    # Frosted dark panel behind text for readability
    draw.rectangle(
        [(0, panel_top), (w, panel_bottom)],
        fill=(0, 0, 0, 160),
    )

    # Headline
    headline_y = text_top
    draw.multiline_text(
        (padding, headline_y), headline,
        fill=(255, 255, 255, 255), font=headline_font,
    )

    # Body text
    body_y = headline_y + headline_h + gap
    draw.multiline_text(
        (padding, body_y), body,
        fill=(255, 255, 255, 200), font=body_font,
    )

    result = Image.alpha_composite(img, overlay)
    return result.convert("RGBA")


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

    max_logo_w = int(w * max_ratio)
    logo_aspect = logo.width / logo.height
    logo_w = min(logo.width, max_logo_w)
    logo_h = int(logo_w / logo_aspect)
    logo = logo.resize((logo_w, logo_h), Image.LANCZOS)

    pad = int(w * padding_ratio)
    x = w - logo_w - pad
    y = pad

    # Soft dark glow behind logo for visibility on any background.
    # Paint the logo silhouette in black, then Gaussian-blur it for a smooth halo.
    glow_expand = max(4, int(logo_w * 0.03))
    glow_canvas = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    shadow = Image.new("RGBA", logo.size, (0, 0, 0, 0))
    shadow_pixels = shadow.load()
    logo_pixels = logo.load()
    for sy in range(logo.height):
        for sx in range(logo.width):
            a = logo_pixels[sx, sy][3]
            if a > 30:
                shadow_pixels[sx, sy] = (0, 0, 0, min(200, a))
    glow_canvas.paste(shadow, (x, y), shadow)
    # Blur for a soft halo
    glow_alpha = glow_canvas.split()[3]
    glow_alpha = glow_alpha.filter(ImageFilter.GaussianBlur(radius=glow_expand))
    glow_result = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    glow_result.putalpha(glow_alpha)
    img = Image.alpha_composite(img, glow_result)

    img.paste(logo, (x, y), logo)
    return img.convert("RGB")
