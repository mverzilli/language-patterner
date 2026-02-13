"""Load and validate book.yaml configuration."""

from dataclasses import dataclass, field
from pathlib import Path

import yaml


@dataclass
class Scale:
    id: str
    name: str
    description: str
    range: tuple[int, int]


@dataclass
class Config:
    title: str
    subtitle: str
    authors: list[str]
    scales: list[Scale]
    confidence_labels: dict[int, str]
    style: str | None = None
    source_dir: Path = field(default_factory=lambda: Path("."))

    def scale_for_number(self, number: int) -> Scale | None:
        """Return the scale a pattern number belongs to."""
        for scale in self.scales:
            if scale.range[0] <= number <= scale.range[1]:
                return scale
        return None


def load_config(source_dir: Path) -> Config:
    """Load and validate book.yaml from the given directory."""
    config_path = source_dir / "book.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"No book.yaml found in {source_dir}")

    with open(config_path) as f:
        raw = yaml.safe_load(f)

    if not isinstance(raw, dict):
        raise ValueError("book.yaml must be a YAML mapping")

    for key in ("title", "scales"):
        if key not in raw:
            raise ValueError(f"book.yaml missing required key: {key}")

    scales = []
    for s in raw["scales"]:
        for k in ("id", "name", "range"):
            if k not in s:
                raise ValueError(f"Scale entry missing required key: {k}")
        r = s["range"]
        if not (isinstance(r, list) and len(r) == 2):
            raise ValueError(f"Scale '{s['id']}' range must be a two-element list")
        scales.append(Scale(
            id=s["id"],
            name=s["name"],
            description=s.get("description", ""),
            range=(r[0], r[1]),
        ))

    confidence_labels = {
        int(k): v for k, v in raw.get("confidence_labels", {
            0: "Hypothesis", 1: "Progressing", 2: "Invariant"
        }).items()
    }

    return Config(
        title=raw["title"],
        subtitle=raw.get("subtitle", ""),
        authors=raw.get("authors", []),
        scales=scales,
        confidence_labels=confidence_labels,
        style=raw.get("style"),
        source_dir=source_dir,
    )
