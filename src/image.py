from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

def create_image(text: str):
    cache_dir = Path("cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    font = ImageFont.load_default(16)
    temp = Image.new("RGB", (1, 1))
    temp_draw = ImageDraw.Draw(temp)
    bbox = temp_draw.multiline_textbbox((0, 0), text, font=font)
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    padding = 25
    img = Image.new("RGB", (width + 2 * padding, height + 2 * padding), "brown")
    draw = ImageDraw.Draw(img)
    draw.multiline_text((padding, padding), text, fill="white", font=font)
    img.save(cache_dir / "summary.png")
