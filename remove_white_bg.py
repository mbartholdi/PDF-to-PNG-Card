"""
remove_white_bg.py

Converts PDFs to PNG and/or removes pure white backgrounds from PNG card
images by flood-filling from all border pixels, making them transparent.
Saves results to an 'output/' subfolder.

Usage:
    python3 remove_white_bg.py <folder>

If no folder is given, runs on the folder where this script lives.
"""

import sys
from collections import deque
from pathlib import Path
import fitz  # PyMuPDF
from PIL import Image, ImageFilter


def is_near_white(pixel, tolerance=100):
    r, g, b = pixel[:3]
    return r >= 255 - tolerance and g >= 255 - tolerance and b >= 255 - tolerance


def pdf_to_pil(pdf_path: Path) -> list:
    """Convert each page of a PDF to a PIL Image at 300 DPI."""
    doc = fitz.open(str(pdf_path))
    images = []
    for page in doc:
        mat = fitz.Matrix(300 / 72, 300 / 72)  # 300 DPI
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        images.append(img)
    doc.close()
    return images


def remove_white(image_path: Path = None, pil_image: Image.Image = None, tolerance: int = 100) -> Image.Image:
    if pil_image is not None:
        img = pil_image.convert("RGBA")
    else:
        img = Image.open(image_path).convert("RGBA")
    pixels = img.load()
    w, h = img.size

    visited = set()
    queue = deque()

    # Seed from all border pixels that are near-white
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

    # BFS flood fill — spreads through near-white pixels
    while queue:
        x, y = queue.popleft()
        r, g, b, a = pixels[x, y]
        pixels[x, y] = (r, g, b, 0)  # make transparent

        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < w and 0 <= ny < h and (nx, ny) not in visited:
                if is_near_white(pixels[nx, ny], tolerance):
                    visited.add((nx, ny))
                    queue.append((nx, ny))

    # Erode the alpha channel by 1 pixel to strip any remaining fringe
    alpha = img.getchannel("A")
    alpha = alpha.filter(ImageFilter.MinFilter(3))
    img.putalpha(alpha)

    return img


def process_folder(folder: Path):
    output_dir = folder / "output"
    output_dir.mkdir(exist_ok=True)

    files = sorted(folder.glob("*.png")) + sorted(folder.glob("*.pdf"))
    if not files:
        print("No PNG or PDF files found in folder.")
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

    print(f"\nDone. {count} file(s) processed → {output_dir}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        folder = Path(sys.argv[1])
    else:
        folder = Path(__file__).parent

    if not folder.is_dir():
        print(f"Error: '{folder}' is not a valid directory.")
        sys.exit(1)

    process_folder(folder)
