# simple-modern-pnpm

A minimal, modern TypeScript project template using pnpm workspaces.

This template provides a production-ready monorepo structure with best practices for
TypeScript development.
Use [Copier](https://copier.readthedocs.io/) to create new projects from this template
and pull upstream improvements over time.

## Features

- **pnpm workspaces** - Efficient monorepo dependency management
- **TypeScript 5.9+** - Modern TypeScript with strict configuration
- **tsdown** - Fast ESM builds with TypeScript declarations
- **Vitest 4** - Fast unit testing with coverage
- **ESLint 9** - Flat config with type-aware rules
- **Prettier** - Consistent code formatting
- **Lefthook 2** - Fast git hooks (format, lint, typecheck on commit; test on push)
- **Changesets** - Automated versioning and changelog generation
- **GitHub Actions** - CI/CD for testing and npm publishing

## Using This Template

This template uses [Copier](https://copier.readthedocs.io/) for project generation and
ongoing upstream updates.
We recommend installing Copier via [uv](https://docs.astral.sh/uv/) (shown below), but
any installation method works.

### Create a new project

```bash
uvx copier copy gh:jlevy/simple-modern-pnpm my-project
cd my-project
pnpm install
pnpm build && pnpm test
git init && git add . && git commit -m "Initial commit from simple-modern-pnpm"
```

Copier will prompt for these values:

| Variable              | Description              | Example            |
| --------------------- | ------------------------ | ------------------ |
| `workspace_name`      | Root package.json `name` | `my-workspace`     |
| `package_name`        | Starter package name     | `my-utils`         |
| `package_description` | One-line description     | `Shared utilities` |
| `author_name`         | Package author           | `Jane Doe`         |
| `author_email`        | Author email             | `jane@example.com` |
| `github_org`          | GitHub org or username   | `my-org`           |
| `repo_name`           | GitHub repository name   | `my-project`       |

### Copy into an existing repo

```bash
cd existing-repo
uvx copier copy gh:jlevy/simple-modern-pnpm .

# Review what changed
git diff

# Merge your existing code: restore your source files, merge configs
pnpm install
pnpm build && pnpm test
git add . && git commit -m "Add simple-modern-pnpm template structure"
```

### Pull upstream template updates

After creating a project from this template, you can pull in future improvements:

```bash
uvx copier update
pnpm install && pnpm build && pnpm test
git add . && git commit -m "Update from simple-modern-pnpm template"
```

Copier does a three-way merge: it regenerates the old template version, diffs your local
changes, and applies the new template on top.
Conflicts are marked inline or as `.rej` files for you to resolve.

## Documentation

| Document                                   | Description                                |
| ------------------------------------------ | ------------------------------------------ |
| [docs/development.md](docs/development.md) | Development setup, scripts, and config     |
| [docs/publishing.md](docs/publishing.md)   | Versioning, changesets, and npm publishing |

`CLAUDE.md` and `AGENTS.md` symlink to `docs/development.md` so that AI coding agents
automatically have development context.

## Project Structure

```
.
├── docs/
│   ├── development.md       # Development guide (= CLAUDE.md, AGENTS.md)
│   └── publishing.md        # Publishing and release guide
├── packages/
│   └── <package>/           # Your package(s)
│       ├── src/             # Source code
│       ├── tests/           # Tests
│       ├── package.json
│       ├── tsconfig.json
│       ├── tsdown.config.ts
│       └── vitest.config.ts
├── .changeset/              # Changesets configuration
├── .github/workflows/       # CI/CD (test + release)
├── CLAUDE.md -> docs/development.md
├── AGENTS.md -> docs/development.md
├── eslint.config.js         # ESLint flat config
├── .prettierrc              # Prettier config
├── lefthook.yml             # Git hooks
├── package.json             # Root workspace config
├── pnpm-workspace.yaml      # Workspace packages
├── tsconfig.json            # Root TypeScript config
└── tsconfig.base.json       # Shared TypeScript settings
```

## License

MIT
