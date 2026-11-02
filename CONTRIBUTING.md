# Contributing

Thanks for helping with CopyCast. This document describes how we work.

## Workflow

1. Pick an issue from the GitHub Projects board, or open one. Every task is an issue with an assignee, a label and a status.
2. Create a branch from an up-to-date `main`.
3. Commit with small, focused commits.
4. Open a pull request linked to the issue (`Closes #123`).
5. Wait for CI to pass and for one approving review. Resolve all review conversations.
6. The pull request is squash-merged. The branch is deleted automatically.

`main` is protected: no direct push, no force push, no merge without review and a passing pipeline.

## Branches

| Prefix | Use |
| --- | --- |
| `feat/` | New feature |
| `fix/` | Bug fix |
| `docs/` | Documentation only |
| `ci/` | Pipeline and tooling |
| `refactor/` | Change without behavior change |
| `test/` | Tests only |

Example: `feat/smb-source`.

## Commit messages

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>(<optional scope>): <short summary>
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`.

Examples:

```
feat(library): add incremental scan
fix(remote): reject unpaired devices
docs(extensions): add manifest reference
```

## Pull requests

- Keep them small and focused on one issue.
- Fill in the pull request template.
- Add or update tests for any behavior change.
- Update the documentation and the changelog when behavior changes.
- Check accessibility for any UI change: keyboard-only navigation, visible focus, accessible names, contrast.
- Never commit secrets, API keys, media files or build output.

## Code quality

Linters and formatters run through pre-commit and in CI. Install the hooks once after cloning:

```bash
pre-commit install
```

## Use of AI

AI tools are allowed. Declare what you used in the README section "Use of AI". Generated code follows the same rules as any other code: tests, review, clean repository. You are responsible for what you submit and must be able to explain it.

## Legal content only

Only use media that is royalty-free or under an open license. Never add an extension or a source that gives access to illegally distributed content.
