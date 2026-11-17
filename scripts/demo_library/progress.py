"""Human-readable output of transfers: sizes and a progress line."""

import sys
import time

MIN_SECONDS_BETWEEN_UPDATES = 0.5
UNITS = ("B", "KB", "MB", "GB")


def format_size(byte_count: int) -> str:
    """Formats a number of bytes, for example `103.6 MB`."""
    size = float(byte_count)
    for unit in UNITS[:-1]:
        if size < 1000:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1000
    return f"{size:.1f} {UNITS[-1]}"


class ProgressReporter:
    """Prints how far a download went. Call it with `(received, total)` as bytes arrive.

    On a terminal the line is updated in place. Otherwise (logs, CI) only the final line
    is printed, so the output stays readable.
    """

    def __init__(self, label: str, stream=None):
        self._label = label
        self._stream = stream if stream is not None else sys.stderr
        self._last_update = 0.0
        self._received = 0
        self._total = 0

    def __call__(self, received: int, total: int) -> None:
        self._received, self._total = received, total
        if self._stream.isatty() and self._is_due():
            self._print_line(end="\r")

    def finish(self) -> None:
        self._print_line(end="\n")

    def _is_due(self) -> bool:
        now = time.monotonic()
        if now - self._last_update < MIN_SECONDS_BETWEEN_UPDATES:
            return False
        self._last_update = now
        return True

    def _print_line(self, end: str) -> None:
        percent = 100 * self._received // self._total if self._total else 0
        line = (
            f"  {self._label}: {percent:3d}% "
            f"({format_size(self._received)} of {format_size(self._total)})"
        )
        print(line, end=end, file=self._stream, flush=True)
