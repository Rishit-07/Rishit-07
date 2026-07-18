import json
import re
from datetime import UTC, datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_PATH = ROOT / "data" / "contributions.json"
USERNAME = "Rishit-07"
SOURCE_URL = f"https://github.com/users/{USERNAME}/contributions"


def fetch_contributions_html(url: str = SOURCE_URL) -> str:
    """Fetch GitHub's public contributions fragment without using the GitHub API."""
    response = requests.get(
        url,
        headers={
            "Accept": "text/html",
            "User-Agent": "animated-github-profile-generator/1.0",
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.text


def parse_count(label: str | None, data_count: str | None) -> int:
    """Extract a contribution count from GitHub's attributes or aria label."""
    if data_count and data_count.isdigit():
        return int(data_count)

    if not label or label.lower().startswith("no contributions"):
        return 0

    match = re.search(r"(\d+)\s+contribution", label)
    return int(match.group(1)) if match else 0


def parse_total_contributions(soup: BeautifulSoup) -> int | None:
    """Find the visible summary total when it is present in the HTML."""
    text = soup.get_text(" ", strip=True)
    match = re.search(r"([\d,]+)\s+contributions?\s+in\s+the\s+last\s+year", text, re.I)
    return int(match.group(1).replace(",", "")) if match else None


def parse_contribution_days(html: str) -> dict:
    """Parse daily contribution cells from GitHub's public contribution graph."""
    soup = BeautifulSoup(html, "html.parser")
    days = []

    for cell in soup.select("[data-date]"):
        date = cell.get("data-date")
        label = cell.get("aria-label") or cell.get("data-tooltip")

        days.append(
            {
                "date": date,
                "count": parse_count(label, cell.get("data-count")),
                "level": int(cell.get("data-level", "0")),
                "description": label,
            }
        )

    return {
        "username": USERNAME,
        "source_url": SOURCE_URL,
        "fetched_at": datetime.now(UTC).isoformat(),
        "total_contributions": parse_total_contributions(soup),
        "days": days,
    }


def save_contributions(data: dict, output_path: Path = OUTPUT_PATH) -> None:
    """Write parsed contribution data as stable, readable JSON."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, sort_keys=True), encoding="utf-8")


def main() -> None:
    html = fetch_contributions_html()
    save_contributions(parse_contribution_days(html))


if __name__ == "__main__":
    main()
