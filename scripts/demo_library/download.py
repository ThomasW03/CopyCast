"""Downloads one file over HTTP(S) and checks that it arrives complete."""

import urllib.error
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Optional

USER_AGENT = "CopyCast-demo-library/0.1 (+https://github.com/ThomasW03/CopyCast)"
CHUNK_SIZE = 1024 * 1024
TIMEOUT_SECONDS = 30

ProgressCallback = Callable[[int, int], None]


class DownloadError(RuntimeError):
    """A file could not be downloaded."""


@dataclass(frozen=True)
class Probe:
    """What a server answers about a file, without sending it."""

    status: int
    size: Optional[int]


def fetch(
    url: str,
    destination: Path,
    expected_size: int,
    progress: Optional[ProgressCallback] = None,
) -> None:
    """Downloads `url` to `destination`.

    The data goes to a `.part` file first, so `destination` only ever holds a complete
    download of `expected_size` bytes.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial = destination.with_name(destination.name + ".part")
    try:
        _write_response(url, partial, expected_size, progress)
        _require_size(partial, expected_size, url)
        partial.replace(destination)
    except OSError as error:
        _discard(partial)
        raise DownloadError(f"cannot download {url}: {error}") from error
    except BaseException:
        _discard(partial)
        raise


def probe(url: str) -> Probe:
    """Asks the server for the status and size of `url`, without downloading it."""
    request = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            return Probe(response.status, _content_length(response))
    except urllib.error.HTTPError as error:
        return Probe(error.code, None)
    except OSError as error:
        raise DownloadError(f"cannot reach {url}: {error}") from error


def _write_response(
    url: str, partial: Path, expected_size: int, progress: Optional[ProgressCallback]
) -> None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    received = 0
    with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
        with open(partial, "wb") as target:
            while chunk := response.read(CHUNK_SIZE):
                target.write(chunk)
                received += len(chunk)
                if progress:
                    progress(received, expected_size)


def _require_size(path: Path, expected_size: int, url: str) -> None:
    actual = path.stat().st_size
    if actual != expected_size:
        raise DownloadError(
            f"{url} is {actual} bytes, expected {expected_size}: "
            "the file changed or the download was cut"
        )


def _content_length(response) -> Optional[int]:
    value = response.headers.get("Content-Length")
    return int(value) if value is not None and value.isdigit() else None


def _discard(path: Path) -> None:
    path.unlink(missing_ok=True)
