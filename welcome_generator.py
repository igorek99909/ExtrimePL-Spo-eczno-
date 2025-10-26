from PIL import Image, ImageDraw, ImageFont
import os
import asyncio
import requests
from io import BytesIO


class WelcomeImageGenerator:

    def __init__(self):
        self.width = 1920
        self.height = 1080
        self.template_path = "attached_assets/image_remplate.png"  # Clean background template
        self.welcome_text_color = (139, 69, 19)  # Brown color for "Witaj" text
        self.footer_text_color = (255, 255, 255)  # White text for footer

    def load_background_template(self):
        """Load the custom background template"""
        try:
            template = Image.open(self.template_path)
            # Ensure it's the right size
            if template.size != (self.width, self.height):
                template = template.resize((self.width, self.height),
                                           Image.Resampling.LANCZOS)
            return template
        except Exception as e:
            print(f"Error loading background template: {e}")
            # Create a fallback background if template fails to load
            return Image.new('RGB', (self.width, self.height), (54, 57, 63))

    async def create_welcome_image(self, username, member_count, guild_name):
        """Create a welcome image using custom background template"""
        # Load the custom background template
        img = self.load_background_template()
        draw = ImageDraw.Draw(img)

        # Try to load fonts with appropriate sizes for 1920x1080
        try:
            welcome_font = ImageFont.truetype(
                "attached_assets/DejaVuSans-Bold.ttf",
                90)  # Large font for "Witaj"
            footer_font = ImageFont.truetype(
                "attached_assets/DejaVuSans-Bold.ttf",
                60)  # Font for footer
        except:
            # Fallback to default font
            welcome_font = ImageFont.load_default()
            footer_font = ImageFont.load_default()

        # Add welcome text "Witaj, {username}!" in lower left area
        # Positioning it higher up in the main image area, not in the orange footer
        welcome_text = f"Witaj, {username}!"
        draw.text((120, 720),
                  welcome_text,
                  fill=self.welcome_text_color,
                  font=welcome_font)

        # Add member count in the orange footer bar
        # Always use "ExtrimePL" regardless of actual server name
        member_text = f"Jesteś {member_count}. graczem na ExtrimePL!"

        # Center the text horizontally in the footer
        bbox = draw.textbbox((0, 0), member_text, font=footer_font)
        text_width = bbox[2] - bbox[0]
        footer_text_x = (self.width - text_width) // 2
        draw.text((footer_text_x, 853),
                  member_text,
                  fill=self.footer_text_color,
                  font=footer_font)

        # Save image with sanitized filename
        import re
        safe_username = re.sub(r'[^\w\-_]', '_',
                               username)[:20]  # Sanitize and limit length
        output_path = f"welcome_{safe_username}_{member_count}.png"
        img.save(output_path)

        return output_path
