"""Command-line interface: list, check or install the demo library."""

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Optional

from . import licenses
from .archive import ArchiveError
from .download import DownloadError, probe
from .install import Outcome, install, relative_path, target_path
from .manifest import ManifestError, MediaEntry, load_manifest
from .progress import ProgressReporter, format_size

DEFAULT_DESTINATION = Path("demo-library")


class UsageError(ValueError):
    """The command line asks for something impossible."""


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        entries = select_entries(load_manifest(), args.only)
        if args.list:
            return list_entries(entries)
        if args.check:
            return check_entries(entries)
        return install_entries(entries, args.dest, args.yes)
    except (ManifestError, UsageError, DownloadError, ArchiveError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted: run the command again to continue", file=sys.stderr)
        return 130


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Download the legal media of the CopyCast demo library."
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=DEFAULT_DESTINATION,
        help=f"folder to install into (default: {DEFAULT_DESTINATION})",
    )
    parser.add_argument("--only", nargs="+", metavar="ID", help="install only these media")
    parser.add_argument("--yes", action="store_true", help="do not ask for confirmation")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--list", action="store_true", help="show the media and exit")
    mode.add_argument(
        "--check", action="store_true", help="check that every download link still works"
    )
    return parser


def select_entries(entries: list, ids: Optional[Sequence[str]]) -> list:
    """Keeps the entries named in `ids`, or all of them when `ids` is empty."""
    if not ids:
        return entries
    known = {entry.id for entry in entries}
    unknown = [name for name in ids if name not in known]
    if unknown:
        raise UsageError(
            f"unknown media: {', '.join(unknown)} (available: {', '.join(sorted(known))})"
        )
    return [entry for entry in entries if entry.id in ids]


def list_entries(entries: Sequence[MediaEntry]) -> int:
    for entry in entries:
        print(f"{entry.id}  {entry.title} ({entry.year})  {format_size(entry.size)}")
        print(f"    installed as: {entry.filename}")
        print(f"    tests:        {entry.difficulty}")
        print(f"    license:      {entry.license}")
    return 0


def check_entries(entries: Sequence[MediaEntry]) -> int:
    problems = {entry.id: _link_problem(entry) for entry in entries}
    for name, problem in problems.items():
        print(f"ok      {name}" if problem is None else f"FAILED  {name}: {problem}")
    return 1 if any(problems.values()) else 0


def install_entries(entries: Sequence[MediaEntry], destination: Path, assume_yes: bool) -> int:
    pending = [entry for entry in entries if not target_path(entry, destination).exists()]
    if pending and not _confirmed(pending, assume_yes):
        print("nothing downloaded")
        return 1
    for entry in pending:
        _install_one(entry, destination)
    present = [entry for entry in entries if target_path(entry, destination).exists()]
    licenses.write(destination, present)
    print(f"{len(present)} media in {destination}")
    return 0


def _link_problem(entry: MediaEntry) -> Optional[str]:
    answer = probe(entry.url)
    if answer.status != 200:
        return f"the server answered {answer.status}"
    if answer.size != entry.size:
        return f"the file is {answer.size} bytes, the manifest says {entry.size}"
    return None


def _confirmed(pending: Sequence[MediaEntry], assume_yes: bool) -> bool:
    total = sum(entry.size for entry in pending)
    print(f"{len(pending)} files to download, {format_size(total)} in total.")
    if assume_yes:
        return True
    return _ask("Continue? [y/N] ").strip().lower() in ("y", "yes")


def _ask(question: str) -> str:
    """Asks on the terminal. `isatty` is not reliable on every system (Windows reports
    the NUL device as a terminal), so a closed input is handled too."""
    no_terminal = UsageError("not an interactive terminal: pass --yes to confirm the download")
    if not sys.stdin.isatty():
        raise no_terminal
    try:
        return input(question)
    except EOFError:
        raise no_terminal from None


def _install_one(entry: MediaEntry, destination: Path) -> None:
    reporter = ProgressReporter(entry.id)
    outcome = install(entry, destination, reporter)
    if outcome is Outcome.INSTALLED:
        reporter.finish()
    print(f"{entry.id}: {outcome.value} as {relative_path(entry)}")
