"""Generate a clean FreshCo brand logo with white text on transparent background."""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

fonts_dir = Path("fonts")

# Canvas — wide enough for text + icon, transparent background
W, H = 600, 200
img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Load fonts
try:
    brand_font = ImageFont.truetype(str(fonts_dir / "Inter-Bold.ttf"), 72)
    small_font = ImageFont.truetype(str(fonts_dir / "Raleway-Medium.ttf"), 20)
except OSError:
    brand_font = ImageFont.load_default(72)
    small_font = ImageFont.load_default(20)

# Draw leaf icon (simple green leaf shape)
leaf_cx, leaf_cy = 70, 70
leaf_color = "#00D67E"  # Bright green
# Leaf body
draw.ellipse(
    [(leaf_cx - 28, leaf_cy - 40), (leaf_cx + 28, leaf_cy + 10)],
    fill=leaf_color,
)
# Leaf tip
draw.polygon(
    [(leaf_cx, leaf_cy - 55), (leaf_cx - 12, leaf_cy - 30), (leaf_cx + 12, leaf_cy - 30)],
    fill=leaf_color,
)
# Leaf stem
draw.line([(leaf_cx, leaf_cy + 10), (leaf_cx, leaf_cy + 30)], fill=leaf_color, width=3)
# Leaf vein
draw.line([(leaf_cx, leaf_cy - 40), (leaf_cx, leaf_cy + 5)], fill=(255, 255, 255, 150), width=2)

# Brand name — bright white
text_x = 115
draw.text((text_x, 35), "FRESHCO", fill="white", font=brand_font)

# Tagline
draw.text((text_x, 115), "NATURE · PERFORMANCE · HYDRATION", fill=(255, 255, 255, 180), font=small_font)

# Crop to content (remove excess transparent space)
bbox = img.getbbox()
if bbox:
    img = img.crop(bbox)

img.save("assets/freshco.png")
print(f"Logo saved to assets/freshco.png ({img.size[0]}x{img.size[1]})")
