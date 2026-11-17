import contextlib
import io
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from demo_library.cli import UsageError, check_entries, install_entries, list_entries, select_entries

from .support import LocalServer, make_entry


def run_silently(function, *args):
    """Calls `function`, hiding what it prints, and returns its result and its output."""
    output = io.StringIO()
    with contextlib.redirect_stdout(output), contextlib.redirect_stderr(io.StringIO()):
        result = function(*args)
    return result, output.getvalue()


class SelectEntriesTest(unittest.TestCase):
    def setUp(self):
        self.entries = [make_entry(id="a", filename="a.mkv"), make_entry(id="b", filename="b.mkv")]

    def test_everything_is_kept_without_a_selection(self):
        self.assertEqual(select_entries(self.entries, None), self.entries)

    def test_only_the_named_media_are_kept(self):
        self.assertEqual([entry.id for entry in select_entries(self.entries, ["b"])], ["b"])

    def test_an_unknown_name_lists_the_available_ones(self):
        with self.assertRaisesRegex(UsageError, "unknown media: c.*a, b"):
            select_entries(self.entries, ["c"])


class ListTest(unittest.TestCase):
    def test_each_media_is_shown_with_its_installed_name_and_difficulty(self):
        entry = make_entry(id="sintel", filename="SINTEL.mkv", difficulty="Upper case")

        status, output = run_silently(list_entries, [entry])

        self.assertEqual(status, 0)
        self.assertIn("sintel", output)
        self.assertIn("SINTEL.mkv", output)
        self.assertIn("Upper case", output)


class CheckTest(unittest.TestCase):
    def test_a_link_with_the_expected_size_passes(self):
        with LocalServer({"/file": b"0123456789"}) as server:
            entry = make_entry(url=server.url("/file"), size=10)

            status, output = run_silently(check_entries, [entry])

        self.assertEqual(status, 0)
        self.assertIn("ok", output)

    def test_a_missing_file_or_a_changed_size_fails(self):
        with LocalServer({"/file": b"0123456789"}) as server:
            missing = make_entry(id="missing", filename="m.mkv", url=server.url("/nope"))
            changed = make_entry(id="changed", filename="c.mkv", url=server.url("/file"), size=99)

            status, output = run_silently(check_entries, [missing, changed])

        self.assertEqual(status, 1)
        self.assertIn("404", output)
        self.assertIn("manifest says 99", output)


class InstallEntriesTest(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.root = Path(self.directory.name) / "library"

    def test_media_and_the_license_file_are_installed(self):
        with LocalServer({"/file": b"0123456789"}) as server:
            entry = make_entry(url=server.url("/file"))

            status, _ = run_silently(install_entries, [entry], self.root, True)

        self.assertEqual(status, 0)
        self.assertTrue((self.root / "movies" / entry.filename).exists())
        self.assertIn(entry.title, (self.root / "LICENSES.md").read_text(encoding="utf-8"))

    def test_running_it_twice_changes_nothing(self):
        with LocalServer({"/file": b"0123456789"}) as server:
            entry = make_entry(url=server.url("/file"))
            run_silently(install_entries, [entry], self.root, True)

            status, output = run_silently(install_entries, [entry], self.root, True)

        self.assertEqual(status, 0)
        self.assertNotIn("files to download", output)

    def test_a_download_needs_confirmation_when_there_is_no_terminal(self):
        entry = make_entry()

        with mock.patch("sys.stdin", io.StringIO()):
            with self.assertRaisesRegex(UsageError, "--yes"):
                run_silently(install_entries, [entry], self.root, False)

    def test_a_closed_input_is_treated_as_no_terminal(self):
        entry = make_entry()

        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", side_effect=EOFError):
            with self.assertRaisesRegex(UsageError, "--yes"):
                run_silently(install_entries, [entry], self.root, False)

    def test_declining_the_confirmation_downloads_nothing(self):
        entry = make_entry()

        with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="n"):
            status, output = run_silently(install_entries, [entry], self.root, False)

        self.assertEqual(status, 1)
        self.assertIn("nothing downloaded", output)
        self.assertFalse(self.root.exists())

    def test_accepting_the_confirmation_downloads(self):
        with LocalServer({"/file": b"0123456789"}) as server:
            entry = make_entry(url=server.url("/file"))

            with mock.patch("sys.stdin.isatty", return_value=True), mock.patch("builtins.input", return_value="y"):
                status, _ = run_silently(install_entries, [entry], self.root, False)

        self.assertEqual(status, 0)
        self.assertTrue((self.root / "movies" / entry.filename).exists())


if __name__ == "__main__":
    unittest.main()
