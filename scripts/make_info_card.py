from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "info-card.svg"

CARD_WIDTH = 760
CARD_HEIGHT = 340
PADDING = 28
ROW_HEIGHT = 34

PROFILE_ROWS = [
    ("Name", "Rishit"),
    ("Role", "Full-stack Developer"),
    ("Languages", "Python, Java, JavaScript"),
    ("Stack", "MERN, OpenCV, GitHub Actions"),
    ("Editor", "VS Code"),
    ("Current Focus", "Animated GitHub profile systems"),
]


def build_row(label: str, value: str, index: int) -> str:
    """Create one terminal row with a staggered fade and slide animation."""
    y = 112 + index * ROW_HEIGHT
    begin = 0.2 + index * 0.14
    prompt_color = "#7ee787"
    label_color = "#79c0ff"
    value_color = "#c9d1d9"

    return (
        f'    <g opacity="0" transform="translate(0 8)">\n'
        f'      <animate attributeName="opacity" from="0" to="1" '
        f'dur="0.45s" begin="{begin:.2f}s" fill="freeze" />\n'
        f'      <animateTransform attributeName="transform" type="translate" '
        f'from="0 8" to="0 0" dur="0.45s" begin="{begin:.2f}s" '
        'fill="freeze" />\n'
        f'      <text x="{PADDING + 2}" y="{y}" fill="{prompt_color}">$</text>\n'
        f'      <text x="{PADDING + 26}" y="{y}" fill="{label_color}">'
        f'{escape(label.lower().replace(" ", "_"))}</text>\n'
        f'      <text x="{PADDING + 188}" y="{y}" fill="{value_color}">'
        f'{escape(value)}</text>\n'
        "    </g>"
    )


def build_svg(rows: list[tuple[str, str]]) -> str:
    """Build a Linux-terminal styled SVG card for a GitHub dark theme."""
    row_markup = "\n".join(build_row(label, value, index) for index, (label, value) in enumerate(rows))

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{CARD_WIDTH}" '
        f'height="{CARD_HEIGHT}" viewBox="0 0 {CARD_WIDTH} {CARD_HEIGHT}" '
        'role="img" aria-label="Profile info terminal card">\n'
        "  <rect width=\"100%\" height=\"100%\" rx=\"18\" fill=\"#0d1117\" "
        "stroke=\"#30363d\" stroke-width=\"2\" />\n"
        "  <rect x=\"1\" y=\"1\" width=\"758\" height=\"52\" rx=\"17\" "
        "fill=\"#161b22\" />\n"
        "  <circle cx=\"32\" cy=\"27\" r=\"7\" fill=\"#ff7b72\" />\n"
        "  <circle cx=\"56\" cy=\"27\" r=\"7\" fill=\"#f2cc60\" />\n"
        "  <circle cx=\"80\" cy=\"27\" r=\"7\" fill=\"#3fb950\" />\n"
        "  <text x=\"112\" y=\"32\" fill=\"#8b949e\" "
        "font-family=\"ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', monospace\" "
        "font-size=\"14\">rishit@github-profile: ~/animated-profile</text>\n"
        "  <g font-family=\"ui-monospace, SFMono-Regular, Consolas, 'Liberation Mono', monospace\" "
        "font-size=\"18\">\n"
        "    <text x=\"28\" y=\"82\" fill=\"#8b949e\">cat profile.info</text>\n"
        f"{row_markup}\n"
        "  </g>\n"
        "</svg>\n"
    )


def make_info_card(output_path: Path = OUTPUT_PATH) -> None:
    """Generate the animated terminal info card SVG."""
    output_path.write_text(build_svg(PROFILE_ROWS), encoding="utf-8")


if __name__ == "__main__":
    make_info_card()
