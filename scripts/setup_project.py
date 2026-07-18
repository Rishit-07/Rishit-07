from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

DIRECTORIES = [
    ROOT / "assets",
    ROOT / "scripts",
    ROOT / "data",
    ROOT / ".github" / "workflows",
]


def main() -> None:
    for directory in DIRECTORIES:
        directory.mkdir(parents=True, exist_ok=True)


if __name__ == "__main__":
    main()

