"""Loads and validates the manifest: the list of legal media the demo library is made of."""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

MANIFEST_PATH = Path(__file__).with_name("manifest.json")
SUPPORTED_KINDS = ("movie",)
REQUIRED_FIELDS = (
    "id",
    "kind",
    "title",
    "year",
    "filename",
    "difficulty",
    "url",
    "size",
    "license",
    "license_url",
    "attribution",
    "source_page",
)


class ManifestError(ValueError):
    """The manifest is malformed."""


@dataclass(frozen=True)
class MediaEntry:
    """One media file, with the name it is installed under and the license it comes with.

    `title` and `year` are what a recognition of `filename` should find. `filename` is
    deliberately badly formatted. When the name cannot be matched on its own,
    `needs_manual_correction` is set.
    """

    id: str
    kind: str
    title: str
    year: int
    filename: str
    difficulty: str
    url: str
    size: int
    license: str
    license_url: str
    attribution: str
    source_page: str
    archive_member: Optional[str] = None
    needs_manual_correction: bool = False


def load_manifest(path: Path = MANIFEST_PATH) -> list:
    """Returns the entries of the manifest, or raises ManifestError."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ManifestError(f"cannot read {path}: {error}") from error
    entries = [_build_entry(raw) for raw in _media_list(document)]
    _require_unique(entries, "id")
    _require_unique(entries, "filename")
    return entries


def _media_list(document: object) -> list:
    if not isinstance(document, dict) or not isinstance(document.get("media"), list):
        raise ManifestError('the manifest must be an object with a "media" list')
    return document["media"]


def _build_entry(raw: object) -> MediaEntry:
    if not isinstance(raw, dict):
        raise ManifestError("every media entry must be an object")
    _require_fields(raw)
    entry = MediaEntry(
        **{field: raw[field] for field in REQUIRED_FIELDS},
        archive_member=raw.get("archive_member"),
        needs_manual_correction=raw.get("needs_manual_correction", False),
    )
    _validate_entry(entry)
    return entry


def _require_fields(raw: dict) -> None:
    missing = [field for field in REQUIRED_FIELDS if field not in raw]
    if missing:
        name = raw.get("id", "<no id>")
        raise ManifestError(f"entry {name} is missing: {', '.join(missing)}")


def _validate_entry(entry: MediaEntry) -> None:
    if entry.kind not in SUPPORTED_KINDS:
        raise ManifestError(f"{entry.id}: unsupported kind {entry.kind!r}")
    if not entry.url.startswith("https://"):
        raise ManifestError(f"{entry.id}: the url must use https")
    if not _is_plain_filename(entry.filename):
        raise ManifestError(f"{entry.id}: filename must not contain a path")
    if not isinstance(entry.size, int) or entry.size <= 0:
        raise ManifestError(f"{entry.id}: size must be a positive number of bytes")
    if not isinstance(entry.year, int):
        raise ManifestError(f"{entry.id}: year must be a number")


def _is_plain_filename(name: str) -> bool:
    return bool(name) and name not in (".", "..") and "/" not in name and "\\" not in name


def _require_unique(entries: list, field: str) -> None:
    seen = set()
    for entry in entries:
        value = getattr(entry, field)
        if value in seen:
            raise ManifestError(f"duplicate {field}: {value}")
        seen.add(value)
