"""Installs one media entry of the manifest into the demo library folder."""

from enum import Enum
from pathlib import Path, PurePosixPath
from typing import Optional
from urllib.parse import urlparse

from .archive import extract_member
from .download import ProgressCallback, fetch
from .manifest import MediaEntry

KIND_FOLDERS = {"movie": "movies"}
WORK_FOLDER = ".downloads"


class Outcome(Enum):
    INSTALLED = "installed"
    ALREADY_PRESENT = "already installed"


def relative_path(entry: MediaEntry) -> PurePosixPath:
    """Where the file lives inside the library, for example `movies/Sintel.mkv`."""
    return PurePosixPath(KIND_FOLDERS[entry.kind]) / entry.filename


def target_path(entry: MediaEntry, library_root: Path) -> Path:
    return library_root / relative_path(entry)


def install(
    entry: MediaEntry, library_root: Path, progress: Optional[ProgressCallback] = None
) -> Outcome:
    """Downloads the entry and puts it in the library. Does nothing if it is already there."""
    target = target_path(entry, library_root)
    if target.exists():
        return Outcome.ALREADY_PRESENT
    download = library_root / WORK_FOLDER / _download_name(entry)
    fetch(entry.url, download, entry.size, progress)
    try:
        _place(entry, download, target)
    finally:
        download.unlink(missing_ok=True)
        _remove_if_empty(download.parent)
    return Outcome.INSTALLED


def _download_name(entry: MediaEntry) -> str:
    remote_name = PurePosixPath(urlparse(entry.url).path).name
    return f"{entry.id}-{remote_name}"


def _place(entry: MediaEntry, download: Path, target: Path) -> None:
    if entry.archive_member:
        extract_member(download, entry.archive_member, target)
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    download.replace(target)


def _remove_if_empty(folder: Path) -> None:
    try:
        folder.rmdir()
    except OSError:
        pass
