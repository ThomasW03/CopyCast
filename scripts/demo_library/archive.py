"""Extracts the one file we want out of a downloaded zip archive."""

import shutil
import zipfile
from pathlib import Path

MAX_EXTRACTED_BYTES = 8 * 1024**3


class ArchiveError(RuntimeError):
    """The archive does not hold what the manifest says."""


def extract_member(archive_path: Path, member: str, destination: Path) -> None:
    """Writes the file named `member` of the archive to `destination`.

    The name inside the archive is only used to find the file. The location comes from
    the caller, so a hostile archive cannot write anywhere else.
    """
    try:
        with zipfile.ZipFile(archive_path) as archive:
            info = _find_member(archive, member)
            _require_reasonable_size(info)
            _write_member(archive, info, destination)
    except zipfile.BadZipFile as error:
        raise ArchiveError(f"{archive_path.name} is corrupted: {error}") from error


def _find_member(archive: zipfile.ZipFile, member: str) -> zipfile.ZipInfo:
    try:
        return archive.getinfo(member)
    except KeyError:
        available = ", ".join(archive.namelist())
        raise ArchiveError(f"{member!r} is not in the archive (it holds: {available})") from None


def _require_reasonable_size(info: zipfile.ZipInfo) -> None:
    if info.file_size > MAX_EXTRACTED_BYTES:
        raise ArchiveError(f"{info.filename!r} would extract to {info.file_size} bytes")


def _write_member(archive: zipfile.ZipFile, info: zipfile.ZipInfo, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    try:
        with archive.open(info) as source, open(partial, "wb") as target:
            shutil.copyfileobj(source, target)
        partial.replace(destination)
    except BaseException:
        partial.unlink(missing_ok=True)
        raise
