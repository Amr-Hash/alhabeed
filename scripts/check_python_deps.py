#!/usr/bin/env python3
"""Ensure Vercel pyproject.toml deps stay in sync with requirements.txt."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQUIREMENTS = ROOT / "backend" / "requirements.txt"
PYPROJECT = ROOT / "backend" / "pyproject.toml"

# Installed in Docker/CI tests only; Vercel uses pyproject.toml instead.
OPTIONAL_IN_PYPROJECT = {"gunicorn", "coverage"}


def package_name(spec: str) -> str:
    return re.split(r"[<>=!~;\[]", spec.strip(), maxsplit=1)[0].strip().lower()


def read_requirements() -> set[str]:
    names: set[str] = set()
    for line in REQUIREMENTS.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        names.add(package_name(line))
    return names


def read_pyproject() -> set[str]:
    text = PYPROJECT.read_text(encoding="utf-8")
    block = re.search(r"dependencies\s*=\s*\[(.*?)\]", text, re.S)
    if not block:
        raise SystemExit(f"Could not parse dependencies from {PYPROJECT}")
    names: set[str] = set()
    for match in re.finditer(r'"([^"]+)"', block.group(1)):
        names.add(package_name(match.group(1)))
    return names


def main() -> int:
    req = read_requirements()
    proj = read_pyproject()

    missing_in_pyproject = sorted(
        name for name in req - OPTIONAL_IN_PYPROJECT if name not in proj
    )
    missing_in_requirements = sorted(name for name in proj if name not in req)

    if missing_in_pyproject:
        print(
            "Runtime packages in requirements.txt but missing from pyproject.toml "
            "(Vercel will not install them):"
        )
        for name in missing_in_pyproject:
            print(f"  - {name}")
    if missing_in_requirements:
        print("Packages in pyproject.toml but missing from requirements.txt:")
        for name in missing_in_requirements:
            print(f"  - {name}")

    if missing_in_pyproject or missing_in_requirements:
        return 1

    print("Python dependencies are in sync between requirements.txt and pyproject.toml.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
