"""
Create Tauri icon from generated image
"""
from PIL import Image
import os

# Load the generated icon
icon_path = r"C:\Users\ADMIN\.gemini\antigravity\brain\9c87ecb2-d122-4660-85d2-0db5638bb023\game_icon.png"
output_dir = r"D:\GameBuild\game-ui\src-tauri\icons"

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Open image
img = Image.open(icon_path)

# Convert to RGBA if needed
if img.mode != 'RGBA':
    img = img.convert('RGBA')

# Create different sizes for Windows
sizes = [(256, 256), (128, 128), (32, 32)]

# Save as ICO
img.save(os.path.join(output_dir, "icon.ico"), format='ICO', sizes=sizes)

print(f"✅ Icon created at: {output_dir}\\icon.ico")
print("You can now run: start_ui.bat")
