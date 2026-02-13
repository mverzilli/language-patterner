"""CLI entry point for language-patterner."""

import http.server
import shutil
import socketserver
import sys
import threading
import time
from pathlib import Path

import click

from .builder import build
from .config import load_config
from .graph import resolve_graph, validate_patterns
from .pattern import load_patterns

INIT_BOOK_YAML = """\
title: "My Pattern Language"
subtitle: ""
authors:
  - Author Name

scales:
  - id: large
    name: "Large Scale"
    description: "Patterns at the largest scale"
    range: [1, 50]
  - id: medium
    name: "Medium Scale"
    description: "Patterns at a medium scale"
    range: [51, 100]
  - id: small
    name: "Small Scale"
    description: "Patterns at the smallest scale"
    range: [101, 150]

confidence_labels:
  0: "Hypothesis"
  1: "Progressing"
  2: "Invariant"

# style: "clean and modern"
"""

INIT_PATTERN = """\
---
number: 1
name: First Pattern
confidence: 0
contains: []
contained_by: []
tags: [example]
---

State the problem this pattern solves here.

## Discussion

Explain the context, forces, and reasoning behind the pattern.

## Solution

Describe the solution clearly and concisely.
"""


@click.group()
def cli():
    """language-patterner: Static site generator for Pattern Language books."""
    pass


@cli.command()
@click.argument("directory")
def init(directory):
    """Initialize a new pattern language project with scaffolding."""
    target = Path(directory)
    if target.exists() and any(target.iterdir()):
        click.echo(f"Error: {directory} already exists and is not empty.", err=True)
        sys.exit(1)

    patterns_dir = target / "patterns"
    patterns_dir.mkdir(parents=True, exist_ok=True)

    (target / "book.yaml").write_text(INIT_BOOK_YAML)
    (patterns_dir / "001-first-pattern.md").write_text(INIT_PATTERN)

    click.echo(f"Initialized new pattern language in {directory}/")
    click.echo(f"  {directory}/book.yaml")
    click.echo(f"  {directory}/patterns/001-first-pattern.md")
    click.echo()
    click.echo("Next steps:")
    click.echo(f"  1. Edit {directory}/book.yaml with your book details")
    click.echo(f"  2. Add patterns in {directory}/patterns/")
    click.echo(f"  3. Run: patterner build --source {directory}")


@cli.command()
@click.option("--source", default=".", help="Source directory containing book.yaml and patterns/")
@click.option("--output", default="_site", help="Output directory for the built site")
def build_cmd(source, output):
    """Build the static site from pattern files."""
    source_dir = Path(source)
    output_dir = Path(output)

    try:
        warnings = build(source_dir, output_dir)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    for w in warnings:
        click.echo(f"Warning: {w}", err=True)

    click.echo(f"Site built successfully in {output_dir}/")


# Register with the name "build" for the CLI
build_cmd.name = "build"


@cli.command()
@click.option("--source", default=".", help="Source directory containing book.yaml and patterns/")
def validate(source):
    """Validate patterns: check references, numbering, missing fields."""
    source_dir = Path(source)

    try:
        config = load_config(source_dir)
        patterns = load_patterns(source_dir)
    except (FileNotFoundError, ValueError) as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)

    warnings = resolve_graph(patterns, config)
    errors = validate_patterns(patterns, config)

    for w in warnings:
        click.echo(f"Warning: {w}")

    for e in errors:
        click.echo(f"Error: {e}")

    if not warnings and not errors:
        click.echo(f"All {len(patterns)} patterns valid.")
    else:
        summary_parts = []
        if errors:
            summary_parts.append(f"{len(errors)} error(s)")
        if warnings:
            summary_parts.append(f"{len(warnings)} warning(s)")
        click.echo(f"Validation complete: {', '.join(summary_parts)}.")
        if errors:
            sys.exit(1)


@cli.command()
@click.option("--source", default=".", help="Source directory containing book.yaml and patterns/")
@click.option("--port", default=8000, help="Port to serve on")
@click.option("--output", default="_site", help="Output directory for the built site")
def serve(source, port, output):
    """Build and serve the site locally with auto-rebuild on changes."""
    source_dir = Path(source)
    output_dir = Path(output)

    def do_build():
        try:
            warnings = build(source_dir, output_dir)
            for w in warnings:
                click.echo(f"Warning: {w}", err=True)
            click.echo(f"Built site in {output_dir}/")
        except Exception as e:
            click.echo(f"Build error: {e}", err=True)

    do_build()

    # Simple file watcher: poll for changes
    def watch():
        last_mtime = {}
        watch_dirs = [source_dir / "patterns", source_dir]
        while True:
            changed = False
            for watch_dir in watch_dirs:
                if not watch_dir.exists():
                    continue
                for f in watch_dir.iterdir():
                    if not f.is_file():
                        continue
                    mtime = f.stat().st_mtime
                    if f not in last_mtime or last_mtime[f] != mtime:
                        last_mtime[f] = mtime
                        changed = True
            if changed:
                click.echo("Change detected, rebuilding...")
                do_build()
            time.sleep(1)

    watcher = threading.Thread(target=watch, daemon=True)
    watcher.start()

    # Serve
    class Handler(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(output_dir), **kwargs)

        def log_message(self, format, *args):
            click.echo(f"  {args[0]}")

    click.echo(f"Serving at http://localhost:{port}/ (Ctrl+C to stop)")
    with socketserver.TCPServer(("", port), Handler) as httpd:
        httpd.allow_reuse_address = True
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            click.echo("\nStopped.")
