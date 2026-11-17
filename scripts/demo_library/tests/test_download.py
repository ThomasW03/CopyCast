import tempfile
import unittest
from pathlib import Path

from demo_library.download import DownloadError, fetch, probe

from .support import LocalServer

CONTENT = b"x" * 5000


class FetchTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.destination = Path(self.directory.name) / "nested" / "file.bin"

    def test_a_complete_download_is_saved(self):
        with LocalServer({"/file": CONTENT}) as server:
            fetch(server.url("/file"), self.destination, len(CONTENT))

        self.assertEqual(self.destination.read_bytes(), CONTENT)

    def test_no_partial_file_is_left_behind(self):
        with LocalServer({"/file": CONTENT}) as server:
            fetch(server.url("/file"), self.destination, len(CONTENT))

        self.assertEqual([path.name for path in self.destination.parent.iterdir()], ["file.bin"])

    def test_progress_reaches_the_total(self):
        calls = []
        with LocalServer({"/file": CONTENT}) as server:
            fetch(server.url("/file"), self.destination, len(CONTENT), lambda *a: calls.append(a))

        self.assertEqual(calls[-1], (len(CONTENT), len(CONTENT)))

    def test_a_file_of_the_wrong_size_is_refused_and_removed(self):
        with LocalServer({"/file": CONTENT}) as server:
            with self.assertRaisesRegex(DownloadError, "expected"):
                fetch(server.url("/file"), self.destination, len(CONTENT) + 1)

        self.assertFalse(self.destination.exists())
        self.assertEqual(list(self.destination.parent.iterdir()), [])

    def test_a_missing_file_is_reported(self):
        with LocalServer({}) as server:
            with self.assertRaisesRegex(DownloadError, "404"):
                fetch(server.url("/missing"), self.destination, 1)

        self.assertFalse(self.destination.exists())


class ProbeTest(unittest.TestCase):
    def test_it_reports_the_status_and_size_without_downloading(self):
        with LocalServer({"/file": CONTENT}) as server:
            answer = probe(server.url("/file"))

        self.assertEqual((answer.status, answer.size), (200, len(CONTENT)))

    def test_it_reports_a_missing_file(self):
        with LocalServer({}) as server:
            answer = probe(server.url("/missing"))

        self.assertEqual((answer.status, answer.size), (404, None))


if __name__ == "__main__":
    unittest.main()
