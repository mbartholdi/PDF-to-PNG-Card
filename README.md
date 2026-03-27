# PDF / PNG → Transparent PNG

Removes white backgrounds from card images (PNG or PDF) and saves them as transparent PNGs. Built for MTG card art but works for any card image with a white border.

**What it does:**
- Flood-fills outward from the white edges/corners, making them transparent
- Handles anti-aliased edges cleanly (no fringing)
- Converts PDFs to PNG automatically at 300 DPI
- Saves all results to an `output/` folder — originals are never touched

---

## Setup (one time only)

### 1. Install Python
Download and install Python 3 from [python.org](https://www.python.org/downloads/).

### 2. Install dependencies
Open Terminal and run:

```
pip3 install -r requirements.txt
```

---

## How to use

### Option A — Double-click (easiest)
Double-click `remove_white_bg.py`. A folder picker will appear — select the folder containing your images. Processed files are saved to an `output/` subfolder inside that folder.

> **Note (Mac):** You may need to right-click → Open the first time due to Gatekeeper.

### Option B — Terminal
```
python3 remove_white_bg.py /path/to/your/folder
```

---

## Supported formats
| Input | Output |
|-------|--------|
| `.png` | `.png` (transparent background) |
| `.pdf` | `.png` (converted at 300 DPI, transparent background) |

Multi-page PDFs produce one PNG per page: `filename_1.png`, `filename_2.png`, etc.

---

## Tips
- Drop your images into any folder and point the script at it — you don't need to move the script
- Re-running the script will overwrite files in the `output/` folder
- The script only removes background connected to the edges — white areas inside the card (like text boxes) are left untouched
