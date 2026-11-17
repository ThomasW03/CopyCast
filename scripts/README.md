# Scripts

## Demo library

`fetch-demo-library.py` downloads a legal media library to develop and test CopyCast against. It needs Python 3.9 or later and nothing else (no package to install).

```bash
python scripts/fetch-demo-library.py
```

The media are installed in `demo-library/` at the root of the repository (ignored by git). The script shows how much it is going to download and asks for confirmation. Pass `--yes` to skip the question, for example in a script.

| Option | Effect |
| --- | --- |
| `--dest FOLDER` | Install somewhere else than `demo-library/` |
| `--only ID [ID ...]` | Install only these media (see `--list` for the ids) |
| `--list` | Show the media, their size, installed name and license, then exit |
| `--check` | Check that every download link still works, without downloading |
| `--yes` | Do not ask for confirmation |

Running it again only downloads what is missing. A download that is cut or has the wrong size is refused and leaves nothing behind. Media delivered in a zip are extracted: the files inside the archive are checked by their CRC.

The first run downloads about 1.4 GB, mostly Sintel (681 MB). To start small, install one film:

```bash
python scripts/fetch-demo-library.py --only elephants-dream
```

### What is in it

Every media comes from the Blender Foundation open movies, released under a Creative Commons Attribution license. `LICENSES.md` is written next to the media with the license, the credit and the source of each file. The same information is in `scripts/demo_library/manifest.json`.

The files are installed under **deliberately badly formatted names**, to exercise the recognition of file names and the manual correction:

| Installed as | What it tests |
| --- | --- |
| `Elephants.Dream.2006.480p.WEB-DL.H264-DEMO.mov` | Dots as separators, release tags around the year |
| `big_buck_bunny_360p_final(2).m4v` | Underscores, no year, a copy suffix |
| `SINTEL - 2010 - 720p [BluRay] x264.mkv` | Upper case, dashes, brackets |
| `ToS_2012_720p.mov` | Abbreviated title: cannot be matched, needs manual correction |
| `caminandes_2_gran_dillama.mp4` | A number in the title that looks like a sequel number, no year |

The manifest also holds the title and year a recognition should find for each file (`title`, `year`), and `needs_manual_correction` when the name alone is not enough. Recognition tests should read these values instead of repeating them.

### Not complete yet

The brief asks for at least 10 films, a series of several episodes, 50 music tracks and 3 podcasts. This first version has 5 films. Series, music and podcasts need new entries in the manifest (and support for their kinds in `manifest.py` and `install.py`).

The download size of each file is checked against the manifest. There is no checksum of the downloads themselves, because the Blender servers do not publish one for these files.

### Add a media

1. Find a media under a Creative Commons license that allows sharing, and read its license on the official page. Never add a media of unclear origin.
2. Add an entry to `scripts/demo_library/manifest.json`: download link, exact size in bytes, license, license link, credit and source page. For a zip, give the name of the file inside in `archive_member`.
3. Check the link and the size:

```bash
python scripts/fetch-demo-library.py --check
```

### Tests

The tests use a local web server and need no network:

```bash
cd scripts
python -m unittest discover -s demo_library/tests -t .
```
