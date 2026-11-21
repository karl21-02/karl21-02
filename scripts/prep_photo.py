"""One-time portrait prep, following the article's rembg / CLAHE / white pipeline.

Install scripts/portrait-requirements.txt locally before running this script.
The daily workflow never needs to process a photo or download a model.
"""
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import new_session, remove


ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    source = Image.open(ROOT / "assets/avatar.png").convert("RGB")
    portrait = remove(source, session=new_session("u2net_human_seg"))
    bounds = portrait.getchannel("A").getbbox()
    if not bounds:
        raise ValueError("No portrait subject found")
    portrait = portrait.crop(bounds)
    rgb = np.asarray(portrait.convert("RGB"))
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    gray = cv2.createCLAHE(clipLimit=2.5, tileGridSize=(8, 8)).apply(gray)
    contrast = Image.fromarray(gray).convert("RGBA")
    contrast.putalpha(portrait.getchannel("A"))
    white = Image.new("RGBA", contrast.size, "white")
    white.alpha_composite(contrast)
    white.convert("L").save(ROOT / "assets/source-prepped.png")
    print("Wrote assets/source-prepped.png")


if __name__ == "__main__":
    main()
