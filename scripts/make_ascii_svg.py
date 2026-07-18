from html import escape
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "assets" / "source-prepped.png"
OUTPUT_PATH = ROOT / "ascii.svg"

ASCII_CHARS = " .`:-=+*cs#%@"
COLUMNS = 100
FONT_SIZE = 8
CHAR_WIDTH = FONT_SIZE * 0.62
LINE_HEIGHT = FONT_SIZE * 1.15
TEXT_COLOR = "#d1d5db"


def load_grayscale_image(path: Path) -> Image.Image:
    """Load the prepared image as grayscale for brightness sampling."""
    if not path.exists():
        raise FileNotFoundError(f"Missing input image: {path}")

    return Image.open(path).convert("L")


def resize_for_ascii(image: Image.Image, columns: int = COLUMNS) -> Image.Image:
    """Resize the image to about 100 columns while compensating for text shape."""
    width, height = image.size
    rows = max(1, round((height / width) * columns * (CHAR_WIDTH / LINE_HEIGHT)))
    return image.resize((columns, rows))


def pixel_to_ascii(pixel: int) -> str:
    """Map darker pixels to denser ASCII characters."""
    index = round((255 - pixel) / 255 * (len(ASCII_CHARS) - 1))
    return ASCII_CHARS[index]


def image_to_ascii_rows(image: Image.Image) -> list[str]:
    """Convert every resized image row into a string of ASCII characters."""
    pixel_source = getattr(image, "get_flattened_data", image.getdata)
    pixels = list(pixel_source())
    width, height = image.size

    return [
        "".join(pixel_to_ascii(pixels[row * width + column]) for column in range(width))
        for row in range(height)
    ]


def build_svg(rows: list[str]) -> str:
    """Build an animated SVG with each row typing left-to-right once."""
    width = COLUMNS * CHAR_WIDTH
    height = len(rows) * LINE_HEIGHT
    row_duration = 1.2
    row_stagger = 0.035

    clip_paths = []
    text_rows = []

    for row_index, row in enumerate(rows):
        clip_id = f"row-clip-{row_index}"
        y = row_index * LINE_HEIGHT
        baseline_y = y + FONT_SIZE
        begin = row_index * row_stagger

        clip_paths.append(
            f'    <clipPath id="{clip_id}">\n'
            f'      <rect x="0" y="{y:.2f}" width="0" height="{LINE_HEIGHT:.2f}">\n'
            f'        <animate attributeName="width" from="0" to="{width:.2f}" '
            f'dur="{row_duration:.2f}s" begin="{begin:.3f}s" fill="freeze" />\n'
            "      </rect>\n"
            "    </clipPath>"
        )
        text_rows.append(
            f'    <text x="0" y="{baseline_y:.2f}" clip-path="url(#{clip_id})">'
            f"{escape(row)}</text>"
        )

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width:.2f}" '
        f'height="{height:.2f}" viewBox="0 0 {width:.2f} {height:.2f}" '
        'role="img" aria-label="Animated ASCII portrait">\n'
        "  <defs>\n"
        + "\n".join(clip_paths)
        + "\n  </defs>\n"
        f'  <g fill="{TEXT_COLOR}" font-family="monospace" font-size="{FONT_SIZE}" '
        'xml:space="preserve">\n'
        + "\n".join(text_rows)
        + "\n  </g>\n"
        "</svg>\n"
    )


def make_ascii_svg(
    input_path: Path = INPUT_PATH, output_path: Path = OUTPUT_PATH
) -> None:
    """Generate the animated ASCII SVG from the prepared source image."""
    source = load_grayscale_image(input_path)
    ascii_image = resize_for_ascii(source)
    rows = image_to_ascii_rows(ascii_image)

    output_path.write_text(build_svg(rows), encoding="utf-8")


if __name__ == "__main__":
    make_ascii_svg()
