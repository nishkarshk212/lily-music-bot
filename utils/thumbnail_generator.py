"""
Advanced Thumbnail Generator for Music Bot
Creates beautiful thumbnails with blurred background, circular cover image, and adaptive ring color
"""

from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests
from io import BytesIO
import os
import logging
import colorsys

logger = logging.getLogger(__name__)

# Path to playback icons
PLAY_ICONS_PATH = "play_icons.png"

def get_dominant_color(image):
    """Calculate the dominant/average color of an image"""
    # Resize image to 1x1 to get the average color
    img = image.copy()
    img = img.resize((1, 1), resample=Image.Resampling.LANCZOS)
    res = img.getpixel((0, 0))
    return res

def adjust_color_brightness(rgb, factor):
    """Adjust the brightness of an RGB color"""
    h, l, s = colorsys.rgb_to_hls(rgb[0]/255.0, rgb[1]/255.0, rgb[2]/255.0)
    l = max(0, min(1, l * factor))
    r, g, b = colorsys.hls_to_rgb(h, l, s)
    return (int(r*255), int(g*255), int(b*255))

def truncate_text(text, max_len=30):
    """Truncate text to a maximum length"""
    if len(text) > max_len:
        return text[:max_len-3] + "..."
    return text

def crop_center_circle(img, output_size, border_width, ring_color):
    """Crop image into a circle with a ring around it"""
    # Scale up for anti-aliasing
    scale = 2
    size = output_size * scale
    border = border_width * scale
    
    img = img.copy()
    # Crop to square first
    w, h = img.size
    min_dim = min(w, h)
    left = (w - min_dim) / 2
    top = (h - min_dim) / 2
    right = (w + min_dim) / 2
    bottom = (h + min_dim) / 2
    img = img.crop((left, top, right, bottom))
    img = img.resize((size - 2*border, size - 2*border), Image.Resampling.LANCZOS)
    
    # Create final circular image
    final_img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    
    # Draw the adaptive ring
    draw = ImageDraw.Draw(final_img)
    draw.ellipse((0, 0, size, size), fill=ring_color)
    
    # Create mask for the inner image
    mask = Image.new("L", (size - 2*border, size - 2*border), 0)
    draw_mask = ImageDraw.Draw(mask)
    draw_mask.ellipse((0, 0, size - 2*border, size - 2*border), fill=255)
    
    # Paste the image inside the ring
    final_img.paste(img, (border, border), mask)
    
    # Downscale for anti-aliasing
    final_img = final_img.resize((output_size, output_size), Image.Resampling.LANCZOS)
    return final_img

def create_thumbnail(
    title="Unknown Title",
    artist="Unknown Artist",
    views="0 views",
    duration="0:00",
    cover_url=None,
    output="thumb.png"
):
    """
    Create a professional adaptive thumbnail
    """
    try:
        # 1. Load the original thumbnail
        if cover_url:
            response = requests.get(cover_url, timeout=10)
            img_data = BytesIO(response.content)
            original_img = Image.open(img_data).convert("RGBA")
        else:
            # Fallback if no cover URL
            original_img = Image.new("RGBA", (1280, 720), (50, 50, 50))

        # 2. Get dominant color for the ring
        dom_color = get_dominant_color(original_img)
        # Make the ring color lighter to make it pop
        ring_color = adjust_color_brightness(dom_color, 1.5)
        # Ensure it's not too dark or too bright
        h, l, s = colorsys.rgb_to_hls(ring_color[0]/255.0, ring_color[1]/255.0, ring_color[2]/255.0)
        if l < 0.4: l = 0.6
        r, g, b = colorsys.hls_to_rgb(h, l, s)
        ring_color = (int(r*255), int(g*255), int(b*255))

        # 3. Create blurred background
        background = original_img.resize((1280, 720), Image.Resampling.LANCZOS)
        background = background.filter(ImageFilter.GaussianBlur(radius=20))
        # Darken the background
        enhancer = ImageEnhance.Brightness(background)
        background = enhancer.enhance(0.4)
        
        draw = ImageDraw.Draw(background)

        # 4. Draw circular thumbnail
        circle_size = 400
        circle_img = crop_center_circle(original_img, circle_size, 15, ring_color)
        background.paste(circle_img, (100, 160), circle_img)

        # 5. Load Fonts
        try:
            # Try to use common system fonts (macOS, Linux, etc.)
            font_paths = [
                "/Library/Fonts/Arial Unicode.ttf",
                "/System/Library/Fonts/Supplemental/Arial.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "assets/font.ttf"
            ]
            font_path = None
            for path in font_paths:
                if os.path.exists(path):
                    font_path = path
                    break
            
            if font_path:
                font_bold = ImageFont.truetype(font_path, 45)
                font_regular = ImageFont.truetype(font_path, 30)
                font_small = ImageFont.truetype(font_path, 25)
            else:
                raise Exception("No font found")
        except:
            # Fallback to default
            font_bold = ImageFont.load_default()
            font_regular = ImageFont.load_default()
            font_small = ImageFont.load_default()

        # 6. Draw Text
        text_x = 550
        draw.text((text_x, 230), truncate_text(title, 35), fill="white", font=font_bold)
        draw.text((text_x, 300), f"{truncate_text(artist, 25)} | {views}", fill=(200, 200, 200), font=font_regular)

        # 7. Draw Progress Bar
        bar_x = text_x
        bar_y = 380
        bar_width = 600
        bar_height = 8
        progress = 0.6 # Static 60% for thumbnail
        
        # Background bar
        draw.rounded_rectangle((bar_x, bar_y, bar_x + bar_width, bar_y + bar_height), radius=4, fill=(100, 100, 100))
        # Progress bar (using adaptive ring color)
        draw.rounded_rectangle((bar_x, bar_y, bar_x + int(bar_width * progress), bar_y + bar_height), radius=4, fill=ring_color)
        # Progress dot
        dot_x = bar_x + int(bar_width * progress)
        dot_y = bar_y + bar_height // 2
        dot_radius = 8
        draw.ellipse((dot_x - dot_radius, dot_y - dot_radius, dot_x + dot_radius, dot_y + dot_radius), fill=ring_color)

        # 8. Draw Time
        draw.text((bar_x, bar_y + 20), "00:00", fill="white", font=font_small)
        draw.text((bar_x + bar_width - 50, bar_y + 20), duration, fill="white", font=font_small)

        # 9. Draw Playback Icons
        if os.path.exists(PLAY_ICONS_PATH):
            try:
                icons = Image.open(PLAY_ICONS_PATH).convert("RGBA")
                # Resize icons to fit nicely
                icon_w, icon_h = icons.size
                new_h = 60
                new_w = int(icon_w * (new_h / icon_h))
                icons = icons.resize((new_w, new_h), Image.Resampling.LANCZOS)
                
                # Center icons below progress bar
                icons_x = bar_x + (bar_width - new_w) // 2
                background.paste(icons, (icons_x, 450), icons)
            except Exception as e:
                logger.error(f"Failed to load icons: {e}")

        # 10. Save result
        os.makedirs(os.path.dirname(output) if os.path.dirname(output) else ".", exist_ok=True)
        background.save(output, "PNG")
        logger.info(f"✅ Adaptive thumbnail created: {output}")
        return output

    except Exception as e:
        logger.error(f"❌ Failed to create thumbnail: {e}")
        import traceback
        traceback.print_exc()
        return None
