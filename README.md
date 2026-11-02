# CopyCast

A media center for the living room: it manages a media library, enriches it with metadata (posters, summaries, cast), plays it, and can be controlled from a smartphone used as a remote.

> Status: early development. Nothing is released yet.

## Features (planned)

- Fullscreen "10-foot" desktop app, fully navigable with arrow keys, Enter and Back.
- Library of movies, TV shows, music and podcasts, from local folders and network shares.
- Automatic file recognition and metadata enrichment, with manual correction and an offline cache.
- Multiple profiles with parental control.
- Extension system with permissions and isolation, plus switchable themes.
- Local network control API with secure pairing and automatic discovery.
- Mobile remote app.

## Requirements

To be completed once the stack is final. See [docs/adr/0001-stack.md](docs/adr/0001-stack.md).

## Getting started

To be completed. The goal is to run the app, the demo library and the tests in under 15 minutes from a fresh clone.

```bash
git clone https://github.com/ThomasW03/CopyCast.git
cd CopyCast
cp .env.example .env
```

## Tests

To be completed. Tests will run with a single command.

## Documentation

- [Documentation index](docs/README.md)
- [Architecture decisions](docs/adr/)
- [Contributing](CONTRIBUTING.md)
- [Changelog](CHANGELOG.md)

## Use of AI

AI tools are allowed on this project and are declared here. Every generated change goes through the same tests, pull request review and repository rules as any other change, and every team member must be able to explain any part of the code.

| Tool | Used for |
| --- | --- |
| _to be filled_ | _code, tests, documentation, visuals_ |

## Third-party services and attribution

Metadata is provided by public APIs, used under their terms. The required attributions will be listed here (for example TheMovieDB and MusicBrainz).

## License

[MIT](LICENSE)
