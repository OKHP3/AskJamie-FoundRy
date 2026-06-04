#!/usr/bin/env python3
"""Normalize filenames in a directory tree to lowercase-kebab-case ASCII.

Safety defaults:
- Dry-run by default (no renames unless --apply)
- Non-recursive by default
- Hidden paths (starting with '.') excluded by default (use --include-hidden)
- Build/convention dirs excluded by default (use --include-default-dirs)
- Collision-safe: if target exists, appends "-2", "-3", ...
"""

from __future__ import annotations

import argparse
import os
import re
import sys
import unicodedata
from dataclasses import dataclass
from pathlib import Path

INVALID_WINDOWS_BASENAMES = {
    "con", "prn", "aux", "nul",
    *(f"com{i}" for i in range(1, 10)),
    *(f"lpt{i}" for i in range(1, 10)),
}

CHAR_SUBSTITUTIONS: dict[str, str] = {
    "\u2011": "-",   # NON-BREAKING HYPHEN
    "\u2010": "-",   # HYPHEN
    "\u2012": "-",   # FIGURE DASH
    "\u2013": "-",   # EN DASH
    "\u2014": "-",   # EM DASH
    "\u2015": "-",   # HORIZONTAL BAR
    "\u2212": "-",   # MINUS SIGN
    "\u1D67": "y",   # MODIFIER LETTER SMALL GAMMA (ᵧ)
    "\u00B3": "3",   # SUPERSCRIPT THREE (³)
    "\u00B2": "2",   # SUPERSCRIPT TWO
    "\u00B9": "1",   # SUPERSCRIPT ONE
    "\u00B0": "deg", # DEGREE SIGN
    "\u2019": "",    # RIGHT SINGLE QUOTATION MARK
    "\u2018": "",    # LEFT SINGLE QUOTATION MARK
    "\u201C": "",    # LEFT DOUBLE QUOTATION MARK
    "\u201D": "",    # RIGHT DOUBLE QUOTATION MARK
    "&": "and",      # AMPERSAND
}

# Well-known filenames that must stay in their conventional form (case-sensitive).
# GitHub renders README, CHANGELOG, CONTRIBUTING, AGENTS, etc. specially when ALLCAPS.
PRESERVE_NAMES: frozenset[str] = frozenset({
    "README.md",
    "README.rst",
    "README.txt",
    "README",
    "CHANGELOG.md",
    "CHANGELOG.rst",
    "CHANGELOG.txt",
    "CHANGELOG",
    "CONTRIBUTING.md",
    "CONTRIBUTING.rst",
    "CONTRIBUTING",
    "LICENSE",
    "LICENSE.md",
    "LICENSE.txt",
    "AUTHORS",
    "AUTHORS.md",
    "OWNERS",
    "CODEOWNERS",
    "CODE_OF_CONDUCT.md",
    "SECURITY.md",
    "SUPPORT.md",
    "AGENTS.md",
    "NOTICE",
    "NOTICE.md",
    "PATENT",
    "PATENTS",
    "COPYING",
    "COPYING.md",
})

# Multi-component compound extensions — checked longest-first.
COMPOUND_EXTENSIONS: tuple[str, ...] = (
    ".d.ts.map",
    ".d.mts.map",
    ".d.cts.map",
    ".d.ts",
    ".d.mts",
    ".d.cts",
    ".mjs.map",
    ".cjs.map",
    ".js.map",
    ".ts.map",
)

# Default dirs to skip (build output, template scaffolds, etc.)
DEFAULT_EXCLUDE_DIRS: frozenset[str] = frozenset({
    "_template",
    "lib",
    "artifacts",
})

# Temp-file marker; uses a leading dot so hidden-exclusion covers it automatically.
_TMP_SUFFIX = ".__norm_tmp__"


def _is_emoji_or_symbol(char: str) -> bool:
    cp = ord(char)
    cat = unicodedata.category(char)
    if cat in ("So", "Sm", "Sc", "Sk"):
        return True
    if (
        0x1F300 <= cp <= 0x1FAFF
        or 0x2600 <= cp <= 0x27BF
        or 0xFE00 <= cp <= 0xFE0F
        or 0x1F1E0 <= cp <= 0x1F1FF
        or cp == 0x200D
        or cp == 0xFE0F
        or cp == 0x20E3
    ):
        return True
    return False


def preprocess_name(name: str) -> str:
    """Apply explicit character substitutions and strip emoji/symbols."""
    result = []
    for ch in name:
        if ch in CHAR_SUBSTITUTIONS:
            result.append(CHAR_SUBSTITUTIONS[ch])
        elif _is_emoji_or_symbol(ch):
            pass
        else:
            result.append(ch)
    return "".join(result)


def split_stem_ext(name: str, *, is_dir: bool = False) -> tuple[str, str]:
    """Split *name* into (stem, extension).

    - Directories have no extension; the whole name is the stem.
    - For files, multi-component compound extensions (.d.ts, .mjs.map …) are
      matched first; otherwise the final Path.suffix is used.
    """
    if is_dir:
        return name, ""

    lower = name.lower()
    for compound in COMPOUND_EXTENSIONS:
        if lower.endswith(compound):
            ext = name[len(name) - len(compound):]
            stem = name[: len(name) - len(compound)]
            return stem, ext

    p = Path(name)
    if p.suffix:
        return name[: -len(p.suffix)], p.suffix
    return name, ""


def clean_filename(name: str, *, keep_unicode: bool, is_dir: bool = False) -> str:
    name = preprocess_name(name)
    stem, ext = split_stem_ext(name, is_dir=is_dir)

    stem = stem.replace(" ", "-")
    stem = stem.replace(".", "-")

    if keep_unicode:
        stem = re.sub(r"[^\w-]+", "", stem)
    else:
        stem = stem.encode("ascii", "ignore").decode("ascii")
        stem = re.sub(r"[^a-zA-Z0-9_-]+", "", stem)

    stem = re.sub(r"-+", "-", stem)
    stem = re.sub(r"_+", "_", stem)
    stem = stem.strip("-_. ")
    stem = stem.lower()

    if not stem:
        stem = "untitled"

    if stem in INVALID_WINDOWS_BASENAMES:
        stem = f"{stem}-file"

    return f"{stem}{ext}"


def unique_destination(dst: Path, *, is_dir: bool = False) -> Path:
    if not dst.exists():
        return dst

    stem, ext = split_stem_ext(dst.name, is_dir=is_dir)
    parent = dst.parent
    for i in range(2, 10_000):
        candidate = parent / f"{stem}-{i}{ext}"
        if not candidate.exists():
            return candidate

    raise RuntimeError(f"Could not find a free filename for: {dst}")


@dataclass(frozen=True)
class RenamePlan:
    src: Path
    dst: Path
    is_dir: bool = False


def _should_exclude(
    path: Path,
    root: Path,
    exclude_paths: set[Path] | None,
    exclude_hidden: bool,
    include_default_dirs: bool,
) -> bool:
    try:
        rel_parts = path.relative_to(root).parts
    except ValueError:
        rel_parts = (path.name,)

    for part in rel_parts:
        if exclude_hidden and part.startswith("."):
            return True
        if not include_default_dirs and part in DEFAULT_EXCLUDE_DIRS:
            return True

    if exclude_paths:
        if any(path == ep or ep in path.parents for ep in exclude_paths):
            return True
    return False


def build_dir_plan(
    directory: Path,
    *,
    recursive: bool,
    keep_unicode: bool,
    exclude_paths: set[Path] | None = None,
    exclude_hidden: bool = True,
    include_default_dirs: bool = False,
) -> list[RenamePlan]:
    all_paths = list(directory.rglob("*")) if recursive else list(directory.iterdir())

    all_paths = [
        p for p in all_paths
        if not _should_exclude(p, directory, exclude_paths, exclude_hidden, include_default_dirs)
    ]

    dir_paths = sorted(
        [p for p in all_paths if p.is_dir()],
        key=lambda p: len(p.parts),
        reverse=True,
    )

    plans: list[RenamePlan] = []
    for src in dir_paths:
        new_name = clean_filename(src.name, keep_unicode=keep_unicode, is_dir=True)
        dst = src.with_name(new_name)
        if src.name == dst.name:
            continue
        dst = unique_destination(dst, is_dir=True)
        plans.append(RenamePlan(src=src, dst=dst, is_dir=True))

    return plans


def build_file_plan(
    directory: Path,
    *,
    recursive: bool,
    keep_unicode: bool,
    include_extensions: set[str] | None = None,
    exclude_extensions: set[str] | None = None,
    exclude_paths: set[Path] | None = None,
    exclude_hidden: bool = True,
    include_default_dirs: bool = False,
) -> list[RenamePlan]:
    all_paths = list(directory.rglob("*")) if recursive else list(directory.iterdir())

    all_paths = [
        p for p in all_paths
        if not _should_exclude(p, directory, exclude_paths, exclude_hidden, include_default_dirs)
    ]

    plans: list[RenamePlan] = []
    for src in sorted([p for p in all_paths if p.is_file()]):
        _, ext = split_stem_ext(src.name)
        if include_extensions is not None and ext.lower() not in include_extensions:
            continue
        if exclude_extensions is not None and ext.lower() in exclude_extensions:
            continue

        if src.name in PRESERVE_NAMES:
            continue
        new_name = clean_filename(src.name, keep_unicode=keep_unicode, is_dir=False)
        dst = src.with_name(new_name)
        if src.name == dst.name:
            continue
        dst = unique_destination(dst)
        plans.append(RenamePlan(src=src, dst=dst))

    return plans


def build_plan(
    directory: Path,
    *,
    recursive: bool,
    keep_unicode: bool,
    include_extensions: set[str] | None = None,
    exclude_extensions: set[str] | None = None,
    include_dirs: bool = False,
    exclude_paths: set[Path] | None = None,
    exclude_hidden: bool = True,
    include_default_dirs: bool = False,
) -> list[RenamePlan]:
    """Build combined rename plan for dry-run display."""
    plans: list[RenamePlan] = []
    if include_dirs:
        plans.extend(build_dir_plan(
            directory,
            recursive=recursive,
            keep_unicode=keep_unicode,
            exclude_paths=exclude_paths,
            exclude_hidden=exclude_hidden,
            include_default_dirs=include_default_dirs,
        ))
    plans.extend(build_file_plan(
        directory,
        recursive=recursive,
        keep_unicode=keep_unicode,
        include_extensions=include_extensions,
        exclude_extensions=exclude_extensions,
        exclude_paths=exclude_paths,
        exclude_hidden=exclude_hidden,
        include_default_dirs=include_default_dirs,
    ))
    return plans


def apply_plan(plans: list[RenamePlan]) -> None:
    """Two-phase rename: all → hidden temp names, then temps → final names."""
    temp_pairs: list[tuple[Path, Path]] = []

    for plan in plans:
        # Leading dot makes temp hidden (excluded by default on re-run).
        tmp = plan.src.with_name("." + plan.src.name + _TMP_SUFFIX)
        tmp = unique_destination(tmp, is_dir=plan.is_dir)
        os.replace(plan.src, tmp)
        temp_pairs.append((tmp, plan.dst))

    for tmp, dst in temp_pairs:
        os.replace(tmp, dst)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description="Normalize filenames to lowercase-kebab-case ASCII.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "directory",
        nargs="?",
        default=str(Path.cwd()),
        help="Directory to process (default: current directory)",
    )
    parser.add_argument("--apply", action="store_true", help="Actually rename files")
    parser.add_argument(
        "--recursive", action="store_true",
        help="Process subfolders too",
    )
    parser.add_argument(
        "--ascii-only", action="store_true",
        help="Strip non-ASCII characters",
    )
    parser.add_argument(
        "--include-dirs", action="store_true",
        help="Also normalize directory names (deepest first, before files)",
    )
    parser.add_argument(
        "--include-hidden", action="store_true",
        help="Include hidden paths (names starting with '.') — excluded by default",
    )
    parser.add_argument(
        "--include-default-dirs", action="store_true",
        help=f"Include default-excluded dirs: {sorted(DEFAULT_EXCLUDE_DIRS)}",
    )
    parser.add_argument(
        "--exclude-path",
        action="append",
        default=None,
        dest="exclude_paths",
        metavar="PATH",
        help="Exclude a path (repeatable), e.g. --exclude-path mydir",
    )
    parser.add_argument(
        "--include-ext",
        action="append",
        default=None,
        metavar="EXT",
        help="Only rename files with this extension (repeatable)",
    )
    parser.add_argument(
        "--exclude-ext",
        action="append",
        default=None,
        metavar="EXT",
        help="Skip files with this extension (repeatable)",
    )

    args = parser.parse_args(argv)

    directory = Path(args.directory).expanduser().resolve()
    keep_unicode = not args.ascii_only
    exclude_hidden = not args.include_hidden
    include_default_dirs = args.include_default_dirs

    include_extensions = None
    if args.include_ext:
        include_extensions = {
            e.lower() if e.startswith(".") else f".{e.lower()}"
            for e in args.include_ext
        }

    exclude_extensions = None
    if args.exclude_ext:
        exclude_extensions = {
            e.lower() if e.startswith(".") else f".{e.lower()}"
            for e in args.exclude_ext
        }

    exclude_paths: set[Path] | None = None
    if args.exclude_paths:
        exclude_paths = {(directory / ep).resolve() for ep in args.exclude_paths}

    plans = build_plan(
        directory,
        recursive=args.recursive,
        keep_unicode=keep_unicode,
        include_extensions=include_extensions,
        exclude_extensions=exclude_extensions,
        include_dirs=args.include_dirs,
        exclude_paths=exclude_paths,
        exclude_hidden=exclude_hidden,
        include_default_dirs=include_default_dirs,
    )

    if not plans:
        print("No changes needed.")
        return 0

    for plan in plans:
        print(f"{plan.src.name} -> {plan.dst.name}")

    if not args.apply:
        print(f"\nDry-run: {len(plans)} rename(s) planned. Re-run with --apply to execute.")
        return 0

    if args.include_dirs:
        dir_plans = build_dir_plan(
            directory,
            recursive=args.recursive,
            keep_unicode=keep_unicode,
            exclude_paths=exclude_paths,
            exclude_hidden=exclude_hidden,
            include_default_dirs=include_default_dirs,
        )
        if dir_plans:
            apply_plan(dir_plans)
            print(f"Directories renamed: {len(dir_plans)}.")

        file_plans = build_file_plan(
            directory,
            recursive=args.recursive,
            keep_unicode=keep_unicode,
            include_extensions=include_extensions,
            exclude_extensions=exclude_extensions,
            exclude_paths=exclude_paths,
            exclude_hidden=exclude_hidden,
            include_default_dirs=include_default_dirs,
        )
        if file_plans:
            apply_plan(file_plans)
            print(f"Files renamed: {len(file_plans)}.")

        total = len(dir_plans) + len(file_plans)
        print(f"\nApplied: {total} rename(s).")
    else:
        apply_plan(plans)
        print(f"\nApplied: {len(plans)} rename(s).")

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
