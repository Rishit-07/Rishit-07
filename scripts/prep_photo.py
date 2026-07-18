from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "assets" / "photo.jpg"
OUTPUT_PATH = ROOT / "assets" / "source-prepped.png"


def load_photo(path: Path) -> Image.Image:
    """Load the source photo as RGB so rembg receives a predictable image mode."""
    if not path.exists():
        raise FileNotFoundError(f"Missing input photo: {path}")

    return Image.open(path).convert("RGB")


def remove_background(image: Image.Image) -> Image.Image:
    """Remove the image background and return an RGBA cutout."""
    return remove(image).convert("RGBA")


def enhance_grayscale(image: Image.Image) -> np.ndarray:
    """Convert the cutout to grayscale and enhance contrast with CLAHE."""
    rgba = np.array(image)
    rgb = cv2.cvtColor(rgba, cv2.COLOR_RGBA2RGB)
    grayscale = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)

    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(grayscale)


def composite_on_white(grayscale: np.ndarray, alpha: np.ndarray) -> Image.Image:
    """Use the rembg alpha mask to place the enhanced subject on white."""
    normalized_alpha = alpha.astype(np.float32) / 255.0
    white = np.full_like(grayscale, 255, dtype=np.uint8)

    composite = (grayscale * normalized_alpha + white * (1.0 - normalized_alpha)).astype(
        np.uint8
    )
    return Image.fromarray(composite, mode="L").convert("RGB")


def prep_photo(input_path: Path = INPUT_PATH, output_path: Path = OUTPUT_PATH) -> None:
    """Prepare the profile photo and save it as a PNG asset."""
    source = load_photo(input_path)
    cutout = remove_background(source)
    enhanced = enhance_grayscale(cutout)
    alpha = np.array(cutout.getchannel("A"))

    output_path.parent.mkdir(parents=True, exist_ok=True)
    composite_on_white(enhanced, alpha).save(output_path)


if __name__ == "__main__":
    prep_photo()
