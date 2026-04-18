#!/usr/bin/env python3
"""Poll the current working directory for file changes.

The script snapshots the directory tree under the current working directory and
prints added, removed, and modified files on each polling interval.

It is intentionally lightweight and uses only the standard library.
"""

from __future__ import annotations

import argparse
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, Iterator, Tuple


@dataclass(frozen=True)
class FileState:
    size: int
    mtime_ns: int


def iter_files(root: Path) -> Iterator[Path]:
    """Yield all files under root, recursively."""
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames.sort()
        filenames.sort()
        current_dir = Path(dirpath)
        for name in filenames:
            yield current_dir / name


def snapshot(root: Path) -> Dict[Path, FileState]:
    """Collect a snapshot of all files under root."""
    state: Dict[Path, FileState] = {}
    for path in iter_files(root):
        try:
            stat_result = path.stat()
        except FileNotFoundError:
            # The file may disappear between os.walk and stat during active writes.
            continue
        state[path.relative_to(root)] = FileState(
            size=stat_result.st_size,
            mtime_ns=stat_result.st_mtime_ns,
        )
    return state


def diff(
    previous: Dict[Path, FileState],
    current: Dict[Path, FileState],
) -> Tuple[list[Path], list[Path], list[Path]]:
    """Return added, removed, and modified paths."""
    prev_paths = set(previous)
    curr_paths = set(current)

    added = sorted(curr_paths - prev_paths)
    removed = sorted(prev_paths - curr_paths)

    modified = []
    for path in sorted(prev_paths & curr_paths):
        if previous[path] != current[path]:
            modified.append(path)

    return added, removed, modified


def format_paths(paths: Iterable[Path]) -> str:
    items = [str(path) for path in paths]
    return "\n".join(f"  {item}" for item in items)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Poll the current working directory for file changes."
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=10.0,
        help="Seconds between polls. Default: 10",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Take one snapshot and exit.",
    )
    args = parser.parse_args()

    root = Path.cwd()
    print(f"Watching: {root}")
    print(f"Polling every {args.interval} seconds")
    print("Press Ctrl+C to stop")
    sys.stdout.flush()

    previous = snapshot(root)
    if args.once:
        print(f"Initial file count: {len(previous)}")
        return 0

    while True:
        time.sleep(args.interval)
        current = snapshot(root)
        added, removed, modified = diff(previous, current)

        if added or removed or modified:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[{timestamp}] changes detected")
            if added:
                print("Added:")
                print(format_paths(added))
            if removed:
                print("Removed:")
                print(format_paths(removed))
            if modified:
                print("Modified:")
                print(format_paths(modified))
            sys.stdout.flush()

        previous = current


if __name__ == "__main__":
    raise SystemExit(main())
