import tempfile
import unittest
from pathlib import Path

from demo_library import licenses

from .support import make_entry


class LicensesTest(unittest.TestCase):
    def test_every_entry_shows_its_license_credit_and_source(self):
        entry = make_entry(
            title="Sintel",
            year=2010,
            filename="SINTEL 2010.mkv",
            license="CC BY 3.0",
            attribution="Blender Foundation",
            source_page="https://example.org/sintel",
        )

        text = licenses.render([entry])

        self.assertIn("## Sintel (2010)", text)
        self.assertIn("`movies/SINTEL 2010.mkv`", text)
        self.assertIn("[CC BY 3.0](https://creativecommons.org/licenses/by/3.0/)", text)
        self.assertIn("Credit: Blender Foundation", text)
        self.assertIn("<https://example.org/sintel>", text)

    def test_the_file_is_written_in_the_library_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "library"

            path = licenses.write(root, [make_entry()])

            self.assertEqual(path, root / "LICENSES.md")
            self.assertIn("Sample (2020)", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
