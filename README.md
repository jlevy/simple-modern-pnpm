# simple-modern-pnpm

An agent-friendly template for a modern model repo in TypeScript using pnpm.

Use [Copier](https://copier.readthedocs.io/) to start a brand-new project, retrofit an
existing TypeScript repo onto this setup, and keep pulling upstream template
improvements over time.

## Why This Template

- **Modern TypeScript repo defaults**: pnpm workspaces, TypeScript 5.9+, tsdown, Vitest,
  ESLint 9, Prettier, Lefthook, and GitHub Actions.
- **Agent-friendly workflows**: deterministic root commands, non-interactive Copier
  inputs, and repo guidance mirrored into `AGENTS.md` and `CLAUDE.md`.
- **Copier lifecycle support**: create, adopt, and update workflows are all first-class.

## Choose a Workflow

### 1. Start a brand-new GitHub repo

Create the repo first, then render the template into the empty clone.

```bash
gh repo create my-org/my-project --public --gitignore Node --license MIT --description "My project description"
git clone https://github.com/my-org/my-project
cd my-project
uvx copier copy gh:jlevy/simple-modern-pnpm . --overwrite
pnpm install
pnpm check
git add .
git commit -m "feat: initialize from simple-modern-pnpm"
git push
```

For non-interactive agent runs:

```bash
uvx copier copy gh:jlevy/simple-modern-pnpm . --overwrite \
  --data workspace_name=my-project \
  --data package_name=my-package \
  --data package_description="My project description" \
  --data author_name="Your Name" \
  --data author_email="you@example.com" \
  --data github_org=my-org \
  --data repo_name=my-project
```

### 2. Render into a local scratch directory

Use this when you want to inspect the generated repo before creating Git history or a
remote repository.

```bash
uvx copier copy gh:jlevy/simple-modern-pnpm my-project
cd my-project
pnpm install
pnpm check
git init -b main
pnpm prepare
git add .
git commit -m "feat: initialize from simple-modern-pnpm"
```

The initial `pnpm install` works before `git init`. Once Git exists, run `pnpm prepare`
to install hooks.

### 3. Adopt the template into an existing TypeScript repo

This is the retrofit path for an existing project that wants this repo structure,
tooling, and Copier update path.

```bash
git checkout -b chore/adopt-simple-modern-pnpm
git status --short
uvx copier copy gh:jlevy/simple-modern-pnpm . --overwrite
git diff
```

Then review and merge carefully:

- If your current repo keeps `src/` or `tests/` at the root, move that code under the
  generated `packages/<package_name>/` directory before the first `pnpm check`.
- Replace the starter files in `packages/<package_name>/src/` and
  `packages/<package_name>/tests/` with your real application code and tests.
- Merge dependencies, exports, bins, and package metadata from your old root
  `package.json` into `packages/<package_name>/package.json`. The new root
  `package.json` is workspace orchestration, not your app package.
- Reconcile `tsconfig`, ESLint, Lefthook, and GitHub workflow changes with any
  repo-specific behavior you already have.
- If you keep a non-`packages/` layout, update `pnpm-workspace.yaml`, root
  `tsconfig.json`, and any package-level config together before running checks.
- Commit `.copier-answers.yml` so future `copier update` runs know which template
  version your repo came from.

When the merge is complete:

```bash
pnpm install
pnpm check
git add .
git commit -m "chore: adopt simple-modern-pnpm"
```

### 4. Pull future upstream template changes

Keep `.copier-answers.yml` committed.
That file is what makes `copier update` work.

```bash
uvx copier update
pnpm install
pnpm check
git add .
git commit -m "chore: update from simple-modern-pnpm"
```

Copier performs a three-way merge and will surface conflicts for manual resolution.

## Template Variables

- `workspace_name`: root workspace package name
- `package_name`: starter package name
- `package_description`: one-line repo/package description
- `author_name`: package author name
- `author_email`: package author email
- `github_org`: GitHub org or username
- `repo_name`: GitHub repo name

## Documentation

| Document | Description |
| --- | --- |
| [docs/development.md](docs/development.md) | Day-to-day development workflow and Copier guidance |
| [docs/publishing.md](docs/publishing.md) | Versioning, release notes, and npm publishing |
| [admin/updating.md](admin/updating.md) | Template-maintainer workflow, compile step, and smoke test |

This repo keeps `AGENTS.md` and `CLAUDE.md` as symlinks to `docs/development.md`.
Generated repos receive the same guidance content so coding agents have the same working
context.

## License

MIT
