import tempfile
import unittest
from pathlib import Path

from demo_library.download import DownloadError
from demo_library.install import WORK_FOLDER, Outcome, install, relative_path, target_path

from .support import LocalServer, make_entry, make_zip


class InstallTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "library"

    def test_a_plain_file_is_installed_under_its_messy_name(self):
        entry_path = "/movie"
        with LocalServer({entry_path: b"0123456789"}) as server:
            entry = make_entry(url=server.url(entry_path), filename="Sample (2020) [720p].mkv")

            outcome = install(entry, self.root)

        self.assertIs(outcome, Outcome.INSTALLED)
        self.assertEqual((self.root / "movies" / "Sample (2020) [720p].mkv").read_bytes(), b"0123456789")

    def test_a_file_inside_a_zip_is_extracted_and_renamed(self):
        archive = Path(self.directory.name) / "source.zip"
        content = make_zip(archive, {"Original.Name.mkv": b"video"})
        with LocalServer({"/archive.zip": content}) as server:
            entry = make_entry(
                url=server.url("/archive.zip"),
                size=len(content),
                archive_member="Original.Name.mkv",
                filename="messy name.mkv",
            )

            install(entry, self.root)

        self.assertEqual((self.root / "movies" / "messy name.mkv").read_bytes(), b"video")

    def test_the_download_folder_is_removed_afterwards(self):
        with LocalServer({"/movie": b"0123456789"}) as server:
            install(make_entry(url=server.url("/movie")), self.root)

        self.assertFalse((self.root / WORK_FOLDER).exists())

    def test_an_installed_file_is_not_downloaded_again(self):
        with LocalServer({"/movie": b"0123456789"}) as server:
            entry = make_entry(url=server.url("/movie"))
            install(entry, self.root)

            outcome = install(entry, self.root)

        self.assertIs(outcome, Outcome.ALREADY_PRESENT)

    def test_a_failed_download_installs_nothing(self):
        with LocalServer({}) as server:
            entry = make_entry(url=server.url("/missing"))

            with self.assertRaises(DownloadError):
                install(entry, self.root)

        self.assertFalse(target_path(entry, self.root).exists())

    def test_the_relative_path_uses_the_folder_of_the_kind(self):
        entry = make_entry(filename="a.mkv")

        self.assertEqual(str(relative_path(entry)), "movies/a.mkv")


if __name__ == "__main__":
    unittest.main()
