import tempfile
import unittest
from pathlib import Path

from demo_library.archive import ArchiveError, extract_member

from .support import make_zip


class ExtractMemberTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name)
        self.destination = self.root / "out" / "movie.mkv"

    def make_archive(self, members: dict) -> Path:
        path = self.root / "archive.zip"
        make_zip(path, members)
        return path

    def test_the_requested_file_is_written_to_the_destination(self):
        archive = self.make_archive({"inside.mkv": b"video", "other.txt": b"text"})

        extract_member(archive, "inside.mkv", self.destination)

        self.assertEqual(self.destination.read_bytes(), b"video")

    def test_a_missing_member_lists_what_the_archive_holds(self):
        archive = self.make_archive({"inside.mkv": b"video"})

        with self.assertRaisesRegex(ArchiveError, "inside.mkv"):
            extract_member(archive, "absent.mkv", self.destination)

        self.assertFalse(self.destination.exists())

    def test_a_member_name_cannot_choose_where_the_file_goes(self):
        archive = self.make_archive({"../escaped.mkv": b"video"})

        extract_member(archive, "../escaped.mkv", self.destination)

        self.assertEqual(self.destination.read_bytes(), b"video")
        self.assertFalse((self.root / "escaped.mkv").exists())
        self.assertFalse((self.root.parent / "escaped.mkv").exists())

    def test_a_file_that_is_not_a_zip_is_reported(self):
        broken = self.root / "broken.zip"
        broken.write_bytes(b"not a zip")

        with self.assertRaisesRegex(ArchiveError, "corrupted"):
            extract_member(broken, "inside.mkv", self.destination)

    def test_no_partial_file_is_left_behind(self):
        archive = self.make_archive({"inside.mkv": b"video"})

        extract_member(archive, "inside.mkv", self.destination)

        self.assertEqual([path.name for path in self.destination.parent.iterdir()], ["movie.mkv"])


if __name__ == "__main__":
    unittest.main()
