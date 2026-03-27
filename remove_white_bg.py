"""
remove_white_bg.py

Converts PDFs to PNG and/or removes pure white/near-white backgrounds from
PNG card images by flood-filling from all border pixels, making them
transparent. Saves results to an 'output/' subfolder.

Usage:
    Double-click the script  →  a folder picker dialog opens
    python3 remove_white_bg.py            →  runs on the script's own folder
    python3 remove_white_bg.py <folder>   →  runs on the specified folder
"""

import sys
from collections import deque
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageFilter


# ---------------------------------------------------------------------------
# Folder picker
# ---------------------------------------------------------------------------

def pick_folder() -> Path:
    """Open a native folder-picker dialog. Falls back to the script's folder."""
    try:
        import tkinter as tk
        from tkinter import filedialog
        root = tk.Tk()
        root.withdraw()
        root.lift()
        root.attributes("-topmost", True)
        folder = filedialog.askdirectory(title="Select folder containing PNG/PDF card images")
        root.destroy()
        if not folder:
            print("No folder selected — exiting.")
            sys.exit(0)
        return Path(folder)
    except Exception:
        return Path(__file__).parent


# ---------------------------------------------------------------------------
# Core processing
# ---------------------------------------------------------------------------

def is_near_white(pixel, tolerance=100):
    r, g, b = pixel[:3]
    return r >= 255 - tolerance and g >= 255 - tolerance and b >= 255 - tolerance


def pdf_to_pil(pdf_path: Path) -> list:
    """Convert each page of a PDF to a PIL Image at 300 DPI."""
    doc = fitz.open(str(pdf_path))
    images = []
    for page in doc:
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images


def remove_white(image_path: Path = None, pil_image: Image.Image = None, tolerance: int = 100) -> Image.Image:
    img = pil_image.convert("RGBA") if pil_image is not None else Image.open(image_path).convert("RGBA")
    pixels = img.load()
    w, h = img.size

    visited = set()
    queue = deque()

    for x in range(w):
        for y in [0, h - 1]:
            if is_near_white(pixels[x, y], tolerance) and (x, y) not in visited:
                visited.add((x, y))
                queue.append((x, y))
    for y in range(h):
        for x in [0, w - 1]:
            if is_near_white(pixels[x, y], tolerance) and (x, y) not in visited:
                visited.add((x, y))
                queue.append((x, y))

    while queue:
        x, y = queue.popleft()
        r, g, b, a = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if is_near_white(pixels[nx, ny], tolerance):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    alpha = img.getchannel("A")
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    img.putalpha(alpha)

    return img


def process_folder(folder: Path):
    output_dir = folder / "output"
    output_dir.mkdir(exist_ok=True)

    files = sorted(folder.glob("*.png")) + sorted(folder.glob("*.pdf"))
    if not files:
        print("No PNG or PDF files found in the selected folder.")
        return

    count = 0
    for path in files:
        if path.suffix.lower() == ".pdf":
            print(f"Converting PDF: {path.name} ...")
            pages = pdf_to_pil(path)
            for i, page_img in enumerate(pages):
                suffix = f"_{i+1}" if len(pages) > 1 else ""
                out_name = path.stem + suffix + ".png"
                print(f"  Page {i+1}: removing white background ...")
                result = remove_white(pil_image=page_img)
                out_path = output_dir / out_name
                result.save(out_path, "PNG")
                print(f"  Saved → {out_path}")
                count += 1
        else:
            print(f"Processing {path.name} ...")
            result = remove_white(image_path=path)
            out_path = output_dir / path.name
            result.save(out_path, "PNG")
            print(f"  Saved → {out_path}")
            count += 1

    print(f"\nDone! {count} file(s) processed → {output_dir}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder = Path(sys.argv[1])
    else:
        folder = pick_folder()

    if not folder.is_dir():
        print(f"Error: '{folder}' is not a valid folder.")
        sys.exit(1)

    process_folder(folder)
