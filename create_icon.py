from tkinter import Tk, Canvas
from PIL import Image, ImageDraw

def create_icon(path="resources/sysinfo_lite.png"):
    size = (256, 256)
    img = Image.new('RGBA', size, (0, 0, 0, 0)) # Transparent background
    draw = ImageDraw.Draw(img)

    # Draw rounded rectangle (Blue background)
    # Using a slightly different blue for better visibility
    draw.rounded_rectangle([10, 10, 246, 246], radius=40, fill="#2196F3", outline="#1565C0", width=5)

    # Draw a "Chip" like symbol (White lines and rectangles)
    # Center block
    draw.rectangle([80, 80, 176, 176], fill="white")
    
    # Lines connecting to edges (PCB traces logic)
    # Top
    draw.line([128, 10, 128, 80], fill="white", width=15)
    draw.line([100, 10, 100, 80], fill="white", width=8)
    draw.line([156, 10, 156, 80], fill="white", width=8)
    
    # Bottom
    draw.line([128, 176, 128, 246], fill="white", width=15)
    draw.line([100, 176, 100, 246], fill="white", width=8)
    draw.line([156, 176, 156, 246], fill="white", width=8)

    # Left
    draw.line([10, 128, 80, 128], fill="white", width=15)
    draw.line([10, 100, 80, 100], fill="white", width=8)
    draw.line([10, 156, 80, 156], fill="white", width=8)

    # Right
    draw.line([176, 128, 246, 128], fill="white", width=15)
    draw.line([176, 100, 246, 100], fill="white", width=8)
    draw.line([176, 156, 246, 156], fill="white", width=8)

    # Save
    img.save(path)
    print(f"Icon created at {path}")

if __name__ == "__main__":
    create_icon()
