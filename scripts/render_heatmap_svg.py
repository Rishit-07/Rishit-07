import json
from datetime import date, timedelta
from html import escape
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT_PATH = ROOT / "data" / "contributions.json"
OUTPUT_PATH = ROOT / "contrib-heatmap.svg"

CELL_SIZE = 12
CELL_GAP = 4
GRID_LEFT = 44
GRID_TOP = 54
TEXT_COLOR = "#c9d1d9"
MUTED_TEXT = "#8b949e"
BACKGROUND = "#0d1117"
BORDER = "#30363d"
LEVEL_COLORS = {
    0: "#161b22",
    1: "#0e4429",
    2: "#006d32",
    3: "#26a641",
    4: "#39d353",
}
WEEKDAY_LABELS = {1: "Mon", 3: "Wed", 5: "Fri"}
MONTH_LABELS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def load_contributions(path: Path = INPUT_PATH) -> dict:
    """Load contribution data produced by fetch_contributions.py."""
    if not path.exists():
        raise FileNotFoundError(f"Missing contribution data: {path}")

    return json.loads(path.read_text(encoding="utf-8"))


def parse_days(data: dict) -> dict[date, dict]:
    """Index contribution entries by date for calendar-based rendering."""
    return {
        date.fromisoformat(day["date"]): day
        for day in data.get("days", [])
        if day.get("date")
    }


def date_range(days_by_date: dict[date, dict]) -> tuple[date, date]:
    """Expand the data range to full GitHub-style Sunday-through-Saturday weeks."""
    if not days_by_date:
        today = date.today()
        return today - timedelta(days=today.weekday() + 1), today

    first = min(days_by_date)
    last = max(days_by_date)
    start = first - timedelta(days=(first.weekday() + 1) % 7)
    end = last + timedelta(days=(5 - last.weekday()) % 7)
    return start, end


def contribution_level(day: dict | None) -> int:
    """Normalize contribution levels into GitHub's 0-4 color buckets."""
    if not day:
        return 0

    return max(0, min(4, int(day.get("level", 0))))


def month_labels(start: date, week_count: int) -> list[str]:
    """Create month labels at the first week where each month appears."""
    labels = []
    seen_months = set()

    for week in range(week_count):
        current = start + timedelta(days=week * 7)
        if current.month in seen_months:
            continue

        seen_months.add(current.month)
        labels.append(
            f'    <text x="{GRID_LEFT + week * (CELL_SIZE + CELL_GAP)}" y="36">'
            f"{MONTH_LABELS[current.month - 1]}</text>"
        )

    return labels


def weekday_labels() -> list[str]:
    """Create the sparse weekday labels used by GitHub contribution graphs."""
    return [
        f'    <text x="0" y="{GRID_TOP + weekday * (CELL_SIZE + CELL_GAP) + 10}">{label}</text>'
        for weekday, label in WEEKDAY_LABELS.items()
    ]


def render_cells(days_by_date: dict[date, dict], start: date, end: date) -> list[str]:
    """Render rounded contribution squares with a diagonal reveal animation."""
    cells = []
    current = start

    while current <= end:
        week = (current - start).days // 7
        weekday = (current.weekday() + 1) % 7
        day = days_by_date.get(current)
        level = contribution_level(day)
        count = int(day.get("count", 0)) if day else 0
        label = day.get("description") if day else None
        title = label or f"{count} contributions on {current.isoformat()}"
        x = GRID_LEFT + week * (CELL_SIZE + CELL_GAP)
        y = GRID_TOP + weekday * (CELL_SIZE + CELL_GAP)
        begin = (week + weekday) * 0.018

        cells.append(
            f'    <rect x="{x}" y="{y}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="3" fill="{LEVEL_COLORS[level]}" opacity="0">\n'
            f"      <title>{escape(title)}</title>\n"
            f'      <animate attributeName="opacity" from="0" to="1" dur="0.28s" '
            f'begin="{begin:.3f}s" fill="freeze" />\n'
            "    </rect>"
        )
        current += timedelta(days=1)

    return cells


def legend(width: int, y: int) -> str:
    """Build the Less-to-More contribution intensity legend."""
    legend_x = width - 190
    squares = []

    for level, color in LEVEL_COLORS.items():
        x = legend_x + 36 + level * (CELL_SIZE + 4)
        squares.append(
            f'    <rect x="{x}" y="{y - 10}" width="{CELL_SIZE}" height="{CELL_SIZE}" '
            f'rx="3" fill="{color}" />'
        )

    return (
        f'    <text x="{legend_x}" y="{y}" fill="{MUTED_TEXT}">Less</text>\n'
        + "\n".join(squares)
        + f'\n    <text x="{legend_x + 130}" y="{y}" fill="{MUTED_TEXT}">More</text>'
    )


def build_svg(data: dict) -> str:
    """Build the final animated contribution heatmap SVG."""
    days_by_date = parse_days(data)
    start, end = date_range(days_by_date)
    week_count = ((end - start).days // 7) + 1
    width = GRID_LEFT + week_count * (CELL_SIZE + CELL_GAP) + 24
    height = 190
    total = data.get("total_contributions")
    total_text = f"{total:,} contributions in the last year" if total is not None else "GitHub contributions"

    return (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}" role="img" '
        f'aria-label="{escape(total_text)}">\n'
        f'  <rect width="100%" height="100%" rx="10" fill="{BACKGROUND}" '
        f'stroke="{BORDER}" stroke-width="1" />\n'
        '  <g font-family="ui-monospace, SFMono-Regular, Consolas, '
        "'Liberation Mono', monospace\" font-size=\"11\" fill=\""
        f'{MUTED_TEXT}">\n'
        + "\n".join(month_labels(start, week_count))
        + "\n"
        + "\n".join(weekday_labels())
        + "\n  </g>\n"
        f'  <text x="20" y="24" fill="{TEXT_COLOR}" '
        'font-family="ui-monospace, SFMono-Regular, Consolas, '
        '\'Liberation Mono\', monospace" font-size="14" font-weight="600">'
        f"{escape(total_text)}</text>\n"
        "  <g>\n"
        + "\n".join(render_cells(days_by_date, start, end))
        + "\n  </g>\n"
        '  <g font-family="ui-monospace, SFMono-Regular, Consolas, '
        f'\'Liberation Mono\', monospace" font-size="11">\n{legend(width, 164)}\n'
        "  </g>\n"
        "</svg>\n"
    )


def render_heatmap_svg(input_path: Path = INPUT_PATH, output_path: Path = OUTPUT_PATH) -> None:
    """Render contrib-heatmap.svg from the fetched contribution JSON."""
    output_path.write_text(build_svg(load_contributions(input_path)), encoding="utf-8")


if __name__ == "__main__":
    render_heatmap_svg()
