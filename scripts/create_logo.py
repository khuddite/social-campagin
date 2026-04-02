"""Generate a simple placeholder brand logo."""
from PIL import Image, ImageDraw, ImageFont

img = Image.new("RGBA", (400, 200), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Green rounded rectangle background
draw.rounded_rectangle([(10, 10), (390, 190)], radius=20, fill="#00A86B")

# Brand text
try:
    font = ImageFont.truetype("fonts/Inter-Bold.ttf", 60)
except OSError:
    font = ImageFont.load_default(60)

draw.text((50, 55), "FreshCo", fill="white", font=font)
img.save("assets/logo.png")
print("Logo saved to assets/logo.png")
