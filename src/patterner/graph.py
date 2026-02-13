"""Resolve cross-references and build the relationship graph."""

from .config import Config
from .pattern import Pattern


def resolve_graph(patterns: list[Pattern], config: Config) -> list[str]:
    """Resolve cross-references between patterns and assign scales.

    Returns a list of warning messages for any issues found.
    """
    warnings = []
    by_number: dict[int, Pattern] = {p.number: p for p in patterns}

    # Assign scales
    for pattern in patterns:
        scale = config.scale_for_number(pattern.number)
        if scale:
            pattern.scale_id = scale.id
        else:
            warnings.append(
                f"Pattern {pattern.number} ({pattern.name}): "
                f"number not covered by any scale range"
            )

    # Resolve contains
    for pattern in patterns:
        for ref_num in pattern.contains:
            if ref_num in by_number:
                pattern.contains_patterns.append(by_number[ref_num])
            else:
                warnings.append(
                    f"Pattern {pattern.number} ({pattern.name}): "
                    f"contains reference to non-existent pattern {ref_num}"
                )

    # Resolve contained_by
    for pattern in patterns:
        for ref_num in pattern.contained_by:
            if ref_num in by_number:
                pattern.contained_by_patterns.append(by_number[ref_num])
            else:
                warnings.append(
                    f"Pattern {pattern.number} ({pattern.name}): "
                    f"contained_by reference to non-existent pattern {ref_num}"
                )

    return warnings


def validate_patterns(patterns: list[Pattern], config: Config) -> list[str]:
    """Validate pattern data beyond basic parsing. Returns error messages."""
    errors = []
    seen_numbers: dict[int, str] = {}

    for pattern in patterns:
        # Duplicate numbers
        if pattern.number in seen_numbers:
            errors.append(
                f"Duplicate pattern number {pattern.number}: "
                f"'{seen_numbers[pattern.number]}' and '{pattern.name}'"
            )
        seen_numbers[pattern.number] = pattern.name

        # Missing problem statement
        if not pattern.problem:
            errors.append(
                f"Pattern {pattern.number} ({pattern.name}): "
                f"no problem statement (text before first heading)"
            )

        # Confidence range
        if pattern.confidence not in (0, 1, 2):
            errors.append(
                f"Pattern {pattern.number} ({pattern.name}): "
                f"confidence must be 0, 1, or 2 (got {pattern.confidence})"
            )

    # Check for numbering gaps within scale ranges
    for scale in config.scales:
        nums_in_scale = sorted(
            p.number for p in patterns
            if scale.range[0] <= p.number <= scale.range[1]
        )
        if nums_in_scale:
            for i in range(len(nums_in_scale) - 1):
                gap = nums_in_scale[i + 1] - nums_in_scale[i]
                if gap > 1:
                    errors.append(
                        f"Numbering gap in scale '{scale.name}': "
                        f"no patterns between {nums_in_scale[i]} and {nums_in_scale[i + 1]}"
                    )

    return errors
