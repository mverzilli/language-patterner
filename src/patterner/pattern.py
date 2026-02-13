"""Pattern dataclass and markdown parsing."""

import re
from dataclasses import dataclass, field
from pathlib import Path

import frontmatter
import markdown


@dataclass
class Pattern:
    number: int
    name: str
    confidence: int
    contains: list[int] = field(default_factory=list)
    contained_by: list[int] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    problem: str = ""
    body_html: str = ""
    body_markdown: str = ""
    # Resolved at graph-building time
    scale_id: str | None = None
    contains_patterns: list["Pattern"] = field(default_factory=list, repr=False)
    contained_by_patterns: list["Pattern"] = field(default_factory=list, repr=False)

    @property
    def confidence_stars(self) -> str:
        if self.confidence >= 2:
            return "\u2605\u2605"
        elif self.confidence == 1:
            return "\u2605"
        return "\u25CB"

    @property
    def slug(self) -> str:
        return re.sub(r"[^a-z0-9]+", "-", self.name.lower()).strip("-")


def _extract_problem(md_body: str) -> str:
    """Extract the first paragraph before any heading as the problem statement."""
    lines = []
    for line in md_body.strip().splitlines():
        if line.startswith("#"):
            break
        lines.append(line)
    text = "\n".join(lines).strip()
    # Collapse to first paragraph (separated by blank line)
    paragraphs = re.split(r"\n\s*\n", text)
    return paragraphs[0].strip() if paragraphs else ""


def parse_pattern(path: Path) -> Pattern:
    """Parse a pattern markdown file into a Pattern object."""
    post = frontmatter.load(str(path))
    meta = post.metadata
    body = post.content

    if "number" not in meta or "name" not in meta:
        raise ValueError(f"{path.name}: frontmatter must include 'number' and 'name'")

    md = markdown.Markdown(extensions=["extra", "codehilite", "toc"])
    body_html = md.convert(body)

    problem_md = _extract_problem(body)
    problem_html = markdown.markdown(problem_md) if problem_md else ""

    return Pattern(
        number=int(meta["number"]),
        name=meta["name"],
        confidence=int(meta.get("confidence", 0)),
        contains=meta.get("contains", []),
        contained_by=meta.get("contained_by", []),
        tags=meta.get("tags", []),
        problem=problem_md,
        body_html=body_html,
        body_markdown=body,
    )


def load_patterns(source_dir: Path) -> list[Pattern]:
    """Load all pattern files from source_dir/patterns/."""
    patterns_dir = source_dir / "patterns"
    if not patterns_dir.exists():
        raise FileNotFoundError(f"No patterns/ directory in {source_dir}")

    files = sorted(patterns_dir.glob("*.md"))
    if not files:
        raise FileNotFoundError(f"No .md files found in {patterns_dir}")

    patterns = []
    for f in files:
        patterns.append(parse_pattern(f))

    patterns.sort(key=lambda p: p.number)
    return patterns
