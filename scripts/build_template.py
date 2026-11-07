#!/usr/bin/env python3
"""
Build festcommand.template.yaml from template/festcommand.template.src.yaml.

Every value written as  "@include <path>"  (path relative to the project root)
is replaced by the contents of that file as a literal YAML block scalar (|).
Markdown front matter (a leading --- ... --- block) is stripped from included
SKILL.md files, because Switch agents take plain instructions.

Usage:
    python scripts/build_template.py           # write festcommand.template.yaml
    python scripts/build_template.py --check   # exit 1 if it is out of date
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

# Emoji in the output: don't let a cp1252 console or pipe on Windows crash us.
for _stream in (sys.stdout, sys.stderr):
    if hasattr(_stream, "reconfigure"):
        _stream.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "template" / "festcommand.template.src.yaml"
OUT = ROOT / "festcommand.template.yaml"

INCLUDE = re.compile(r'^(?P<indent>\s*)(?P<key>[A-Za-z_][\w-]*): "@include (?P<path>[^"]+)"\s*$')
FRONT_MATTER = re.compile(r"\A---\n.*?\n---\n+", re.S)

HEADER = (
    "# GENERATED FILE: do not edit by hand.\n"
    "# Source: template/festcommand.template.src.yaml\n"
    "# Rebuild: python scripts/build_template.py\n"
)


def read_include(rel: str) -> str:
    path = (ROOT / rel).resolve()
    if ROOT not in path.parents:
        raise SystemExit(f"@include outside the project: {rel}")
    if not path.is_file():
        raise SystemExit(f"@include target not found: {rel}")
    text = path.read_text(encoding="utf-8").replace("\r\n", "\n")
    if path.suffix == ".md":
        text = FRONT_MATTER.sub("", text, count=1)
    return text.rstrip("\n") + "\n"


def build() -> str:
    out: list[str] = [HEADER]
    for line in SRC.read_text(encoding="utf-8").replace("\r\n", "\n").splitlines(keepends=True):
        m = INCLUDE.match(line.rstrip("\n"))
        if not m:
            out.append(line)
            continue
        indent = m["indent"]
        body_indent = indent + "  "
        out.append(f"{indent}{m['key']}: |\n")
        for body_line in read_include(m["path"]).splitlines():
            out.append(f"{body_indent}{body_line}\n" if body_line.strip() else "\n")
    return "".join(out)


def main() -> int:
    built = build()
    if "--check" in sys.argv:
        current = OUT.read_text(encoding="utf-8") if OUT.exists() else ""
        if current != built:
            print(f"✗ {OUT.name} is out of date. Run: python scripts/build_template.py")
            return 1
        print(f"✓ {OUT.name} is up to date with its sources")
        return 0
    OUT.write_text(built, encoding="utf-8", newline="\n")
    print(f"✓ wrote {OUT.relative_to(ROOT)} ({len(built.encode('utf-8')) // 1024} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
