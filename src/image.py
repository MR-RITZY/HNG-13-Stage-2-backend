from PIL import Image, ImageDraw, ImageFont

def create_image(text: str):
    font = ImageFont.load_default(14)
    temp = Image.new("RGB", (1, 1))
    draw = ImageDraw.Draw(temp)
    bbox = draw.multiline_textbbox((0, 0), text, font=font)
    width, height = bbox[2] - bbox[0], bbox[3] - bbox[1]
    padding = 25
    img = Image.new("RGB", (width + 2*padding, height + 2*padding), "brown")
    draw = ImageDraw.Draw(img)
    draw.text((padding, padding), text, fill="white", font=font)
    img.save("cache/summary.png")
