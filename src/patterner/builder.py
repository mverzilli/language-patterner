"""Orchestrate the build pipeline: parse, resolve, render, write."""

import shutil
from pathlib import Path

from .config import Config, load_config
from .graph import resolve_graph
from .pattern import load_patterns
from .renderer import generate_patterns_json, generate_search_index, render_site


def _static_dir() -> Path:
    return Path(__file__).resolve().parent.parent.parent / "static"


def build(source_dir: Path, output_dir: Path) -> list[str]:
    """Run the full build pipeline. Returns warnings."""
    # 1. Load config
    config = load_config(source_dir)

    # 2. Parse patterns
    patterns = load_patterns(source_dir)

    # 3-5. Resolve graph (assigns scales + cross-references)
    warnings = resolve_graph(patterns, config)

    # 6. Render HTML
    render_site(patterns, config, output_dir)

    # 7. Generate patterns.json
    generate_patterns_json(patterns, config, output_dir)

    # 8. Generate search-index.json
    generate_search_index(patterns, config, output_dir)

    # 9. Copy static assets
    static = _static_dir()
    if static.exists():
        for f in static.iterdir():
            if f.is_file():
                shutil.copy2(f, output_dir / f.name)

    # Copy theme.css if present in source
    theme_css = source_dir / "theme.css"
    if theme_css.exists():
        shutil.copy2(theme_css, output_dir / "theme.css")

    return warnings
