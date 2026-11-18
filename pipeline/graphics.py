import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

def get_font(size: int, bold: bool = True):
    font_candidates = [
        "C:\\Windows\\Fonts\\segoeuib.ttf" if bold else "C:\\Windows\\Fonts\\segoeui.ttf",
        "C:\\Windows\\Fonts\\arialbd.ttf" if bold else "C:\\Windows\\Fonts\\arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf" if bold else "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
    ]
    for fp in font_candidates:
        if os.path.exists(fp):
            try:
                return ImageFont.truetype(fp, size)
            except Exception:
                pass
    return ImageFont.load_default()

def create_graphic_card(
    output_path: Path,
    tag: str,
    title: str,
    subtext: str,
    badge_text: str,
    accent_rgb=(59, 130, 246)
):
    im = Image.new("RGBA", (720, 360), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    
    # Shadow
    d.rounded_rectangle([45, 15, 685, 345], radius=26, fill=(0, 0, 0, 160))
    
    # Main Glass Card Base
    d.rounded_rectangle(
        [40, 10, 680, 340],
        radius=24,
        fill=(15, 23, 42, 250),
        outline=accent_rgb + (255,),
        width=3
    )
    
    # Top Tag Pill
    d.rounded_rectangle([65, 30, 360, 72], radius=12, fill=accent_rgb + (255,))
    d.ellipse([80, 44, 94, 58], fill=(255, 255, 255))
    d.text((105, 36), tag, font=get_font(21, True), fill=(255, 255, 255))
    
    # Title & Subtext
    d.text((65, 95), title[:38], font=get_font(28, True), fill=(255, 255, 255))
    d.text((65, 135), subtext[:50], font=get_font(21, False), fill=(148, 163, 184))
    
    # Content Pill Display
    d.rounded_rectangle([65, 180, 650, 235], radius=10, fill=(30, 41, 59, 255), outline=(71, 85, 105, 255), width=2)
    d.text((80, 195), f">> {badge_text}", font=get_font(20, True), fill=accent_rgb)
    
    # Bottom Callout Banner
    d.rounded_rectangle([65, 260, 650, 312], radius=12, fill=accent_rgb + (240,))
    d.text((120, 271), "100% Free & Beginner Friendly Setup", font=get_font(22, True), fill=(15, 23, 42))
    
    im.save(output_path)
    return output_path
