import json
import tempfile
import unittest
from pathlib import Path

from demo_library.manifest import ManifestError, load_manifest

CREATIVE_COMMONS_PREFIX = "https://creativecommons.org/licenses/"


def valid_raw(**overrides) -> dict:
    raw = {
        "id": "sample",
        "kind": "movie",
        "title": "Sample",
        "year": 2020,
        "filename": "sample.mkv",
        "difficulty": "none",
        "url": "https://example.org/sample.mkv",
        "size": 10,
        "license": "CC BY 3.0",
        "license_url": CREATIVE_COMMONS_PREFIX + "by/3.0/",
        "attribution": "Someone",
        "source_page": "https://example.org",
    }
    raw.update(overrides)
    return raw


class RealManifestTest(unittest.TestCase):
    def setUp(self):
        self.entries = load_manifest()

    def test_it_lists_media(self):
        self.assertGreater(len(self.entries), 0)

    def test_every_media_has_a_creative_commons_license(self):
        for entry in self.entries:
            with self.subTest(entry=entry.id):
                self.assertTrue(entry.license_url.startswith(CREATIVE_COMMONS_PREFIX))

    def test_every_media_has_a_credit_and_a_source(self):
        for entry in self.entries:
            with self.subTest(entry=entry.id):
                self.assertTrue(entry.attribution)
                self.assertTrue(entry.source_page.startswith("https://"))

    def test_the_installed_names_are_not_the_clean_titles(self):
        for entry in self.entries:
            with self.subTest(entry=entry.id):
                self.assertNotEqual(entry.filename, f"{entry.title} ({entry.year}).mkv")


class ValidationTest(unittest.TestCase):
    def load(self, *media: dict):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "manifest.json"
            path.write_text(json.dumps({"media": list(media)}), encoding="utf-8")
            return load_manifest(path)

    def test_a_valid_entry_is_loaded(self):
        entries = self.load(valid_raw())

        self.assertEqual(entries[0].id, "sample")
        self.assertFalse(entries[0].needs_manual_correction)
        self.assertIsNone(entries[0].archive_member)

    def test_a_missing_field_is_reported(self):
        raw = valid_raw()
        del raw["license"]

        with self.assertRaisesRegex(ManifestError, "license"):
            self.load(raw)

    def test_a_filename_with_a_path_is_refused(self):
        for name in ("../escape.mkv", "folder/file.mkv", "..\\escape.mkv", ".."):
            with self.subTest(name=name):
                with self.assertRaisesRegex(ManifestError, "path"):
                    self.load(valid_raw(filename=name))

    def test_a_plain_http_url_is_refused(self):
        with self.assertRaisesRegex(ManifestError, "https"):
            self.load(valid_raw(url="http://example.org/sample.mkv"))

    def test_an_unsupported_kind_is_refused(self):
        with self.assertRaisesRegex(ManifestError, "kind"):
            self.load(valid_raw(kind="game"))

    def test_a_size_must_be_positive(self):
        with self.assertRaisesRegex(ManifestError, "size"):
            self.load(valid_raw(size=0))

    def test_duplicate_ids_are_refused(self):
        with self.assertRaisesRegex(ManifestError, "duplicate id"):
            self.load(valid_raw(), valid_raw(filename="other.mkv"))

    def test_duplicate_filenames_are_refused(self):
        with self.assertRaisesRegex(ManifestError, "duplicate filename"):
            self.load(valid_raw(), valid_raw(id="other"))

    def test_an_unreadable_manifest_is_reported(self):
        with self.assertRaises(ManifestError):
            load_manifest(Path("does-not-exist.json"))


if __name__ == "__main__":
    unittest.main()
