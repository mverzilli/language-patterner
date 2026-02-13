"""Jinja2 HTML rendering and JSON export."""

import json
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

from .config import Config
from .pattern import Pattern


def _get_template_dir() -> Path:
    """Locate the templates directory relative to the package."""
    # Templates live at project root / templates
    return Path(__file__).resolve().parent.parent.parent / "templates"


def _build_env(config: Config) -> Environment:
    env = Environment(
        loader=FileSystemLoader(str(_get_template_dir())),
        autoescape=True,
    )
    env.globals["config"] = config
    env.globals["confidence_labels"] = config.confidence_labels
    return env


def render_site(
    patterns: list[Pattern],
    config: Config,
    output_dir: Path,
) -> None:
    """Render the full static site."""
    env = _build_env(config)
    output_dir.mkdir(parents=True, exist_ok=True)

    by_number = {p.number: p for p in patterns}
    sorted_patterns = sorted(patterns, key=lambda p: p.number)

    # Group patterns by scale
    patterns_by_scale: dict[str, list[Pattern]] = {}
    for scale in config.scales:
        patterns_by_scale[scale.id] = [
            p for p in sorted_patterns if p.scale_id == scale.id
        ]

    # Build scale index lookup for templates
    scale_index = {s.id: i for i, s in enumerate(config.scales)}
    env.globals["scale_index"] = scale_index

    # Compute hierarchy data for index page tree
    has_contains = {p.number for p in sorted_patterns if p.contains}
    has_contained_by = {p.number for p in sorted_patterns if p.contained_by}
    hierarchy_roots = [
        p for p in sorted_patterns
        if p.contains_patterns and not p.contained_by
    ]
    orphan_patterns = [
        p for p in sorted_patterns
        if not p.contains and not p.contained_by
    ]

    # Render index
    tmpl = env.get_template("index.html")
    (output_dir / "index.html").write_text(tmpl.render(
        patterns=sorted_patterns,
        patterns_by_scale=patterns_by_scale,
        hierarchy_roots=hierarchy_roots,
        orphan_patterns=orphan_patterns,
    ))

    # Render individual pattern pages
    pattern_dir = output_dir / "pattern"
    pattern_dir.mkdir(exist_ok=True)
    tmpl = env.get_template("pattern.html")
    for i, pattern in enumerate(sorted_patterns):
        prev_pattern = sorted_patterns[i - 1] if i > 0 else None
        next_pattern = sorted_patterns[i + 1] if i < len(sorted_patterns) - 1 else None
        (pattern_dir / f"{pattern.number}.html").write_text(tmpl.render(
            pattern=pattern,
            prev_pattern=prev_pattern,
            next_pattern=next_pattern,
            scale=config.scale_for_number(pattern.number),
        ))

    # Render scale pages
    scale_dir = output_dir / "scale"
    scale_dir.mkdir(exist_ok=True)
    tmpl = env.get_template("scale.html")
    for scale in config.scales:
        (scale_dir / f"{scale.id}.html").write_text(tmpl.render(
            scale=scale,
            patterns=patterns_by_scale.get(scale.id, []),
        ))

    # Render graph page
    tmpl = env.get_template("graph.html")
    (output_dir / "graph.html").write_text(tmpl.render())


def generate_patterns_json(patterns: list[Pattern], config: Config, output_dir: Path) -> None:
    """Generate patterns.json with full pattern graph metadata."""
    data = {
        "title": config.title,
        "subtitle": config.subtitle,
        "authors": config.authors,
        "scales": [
            {
                "id": s.id,
                "name": s.name,
                "description": s.description,
                "range": list(s.range),
            }
            for s in config.scales
        ],
        "patterns": [
            {
                "number": p.number,
                "name": p.name,
                "confidence": p.confidence,
                "confidence_label": config.confidence_labels.get(p.confidence, "Unknown"),
                "scale": p.scale_id,
                "tags": p.tags,
                "problem": p.problem,
                "contains": p.contains,
                "contained_by": p.contained_by,
            }
            for p in sorted(patterns, key=lambda p: p.number)
        ],
    }
    (output_dir / "patterns.json").write_text(json.dumps(data, indent=2))


def generate_search_index(patterns: list[Pattern], config: Config, output_dir: Path) -> None:
    """Generate search-index.json for client-side search."""
    index = [
        {
            "number": p.number,
            "name": p.name,
            "problem": p.problem[:200],
            "tags": p.tags,
            "scale": p.scale_id,
            "confidence": p.confidence,
        }
        for p in sorted(patterns, key=lambda p: p.number)
    ]
    (output_dir / "search-index.json").write_text(json.dumps(index, indent=2))
