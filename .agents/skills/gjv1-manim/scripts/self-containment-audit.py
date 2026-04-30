#!/usr/bin/env python
# /// script
# requires-python = ">=3.11"
# ///
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {"__pycache__", ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache"}
BINARY_SUFFIXES = {
    ".avi",
    ".gif",
    ".ico",
    ".jpeg",
    ".jpg",
    ".mov",
    ".mp4",
    ".pdf",
    ".png",
    ".pyc",
    ".webm",
}

DISALLOWED_PATTERNS = [
    ("external URL", re.compile("http" + r"s?://", re.IGNORECASE)),
    ("absolute local path", re.compile(r"\b[A-Za-z]:[\\/][^\s)\]`'\"]+")),
    (
        "project-management reference",
        re.compile(r"(^|[\\/`'\"])\." + "specs" + r"([\\/`'\"]|$)|\." + "specs" + r"/", re.IGNORECASE),
    ),
    ("external skill repository reference", re.compile("manim" + r"_skill|" + "github" + r"\.com", re.IGNORECASE)),
    ("external decision-record reference", re.compile(r"\b" + "ADR" + r"-\d{4}\b", re.IGNORECASE)),
]

MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
RELATIVE_PARENT_PATH = re.compile(r"(?<![\w.-])\.\.[\\/][^\s)`'\"]+")


@dataclass(frozen=True)
class Finding:
    path: Path
    line_number: int
    kind: str
    detail: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Verify that gjv1-manim contains no required references outside its own directory."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=SKILL_ROOT,
        help="Skill directory to scan. Defaults to the parent directory of this script.",
    )
    return parser.parse_args()


def iter_text_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if any(part in SKIP_DIRS for part in path.parts):
            continue
        if not path.is_file():
            continue
        if path.suffix.lower() in BINARY_SUFFIXES:
            continue
        files.append(path)
    return files


def read_text(path: Path) -> str | None:
    try:
        data = path.read_bytes()
    except OSError:
        return None
    if b"\x00" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("utf-8", errors="replace")


def normalize_markdown_target(raw_target: str) -> str:
    target = raw_target.strip()
    if target.startswith("<") and target.endswith(">"):
        target = target[1:-1].strip()
    if " " in target:
        target = target.split(" ", 1)[0].strip()
    if "#" in target:
        target = target.split("#", 1)[0].strip()
    return target


def is_inside(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=False))
    except ValueError:
        return False
    return True


def scan_file(path: Path, root: Path) -> list[Finding]:
    text = read_text(path)
    if text is None:
        return []

    findings: list[Finding] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for kind, pattern in DISALLOWED_PATTERNS:
            match = pattern.search(line)
            if match:
                findings.append(
                    Finding(path=path, line_number=line_number, kind=kind, detail=match.group(0))
                )

        for match in MARKDOWN_LINK.finditer(line):
            target = normalize_markdown_target(match.group(1))
            if not target or target.startswith("#"):
                continue
            if re.match("http" + r"s?://", target, re.IGNORECASE):
                findings.append(
                    Finding(path=path, line_number=line_number, kind="external markdown link", detail=target)
                )
                continue
            if Path(target).is_absolute():
                findings.append(
                    Finding(path=path, line_number=line_number, kind="absolute markdown link", detail=target)
                )
                continue
            resolved = (path.parent / target).resolve(strict=False)
            if not is_inside(resolved, root):
                findings.append(
                    Finding(path=path, line_number=line_number, kind="markdown link outside skill", detail=target)
                )

        for match in RELATIVE_PARENT_PATH.finditer(line):
            target = match.group(0).rstrip(".,;:")
            resolved = (path.parent / target).resolve(strict=False)
            if not is_inside(resolved, root):
                findings.append(
                    Finding(path=path, line_number=line_number, kind="relative path outside skill", detail=target)
                )

    return findings


def main() -> int:
    args = parse_args()
    root = args.root.resolve(strict=False)
    findings: list[Finding] = []
    for path in iter_text_files(root):
        findings.extend(scan_file(path.resolve(strict=False), root))

    if findings:
        print("Self-containment audit failed:")
        for finding in findings:
            rel = finding.path.relative_to(root).as_posix()
            print(f"- {rel}:{finding.line_number}: {finding.kind}: {finding.detail}")
        return 1

    print(f"Self-containment audit passed: no outside references found under {root}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
