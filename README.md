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
- **GitHub Actions** - CI/CD with tag-triggered npm publishing via OIDC

## Quick Start

### Prerequisites

- Node.js 24+ ([nvm](https://github.com/nvm-sh/nvm) recommended)
- [pnpm](https://pnpm.io/) (via `corepack enable`)
- [uv](https://docs.astral.sh/uv/) (for running Copier)

### Create a New Project

1. **Create your GitHub repository** (recommended):

   ```bash
   gh repo create my-org/my-project --public --gitignore Node --license MIT --description "My project description"
   git clone https://github.com/my-org/my-project
   cd my-project
   ```

2. **Initialize from template**:

   ```bash
   uvx copier copy gh:jlevy/simple-modern-pnpm . --overwrite
   ```

   Copier will prompt for:

   - `workspace_name` - Root package name (e.g., `my-workspace`)
   - `package_name` - Starter package name (e.g., `my-utils`)
   - `package_description` - One-line description
   - `author_name` & `author_email` - Your information
   - `github_org` & `repo_name` - Match your GitHub repo

3. **Install and verify**:

   ```bash
   pnpm install
   pnpm format
   pnpm build && pnpm test
   ```

4. **Commit and push**:

   ```bash
   git add .
   git commit -m "feat: initialize from simple-modern-pnpm"
   git push
   ```

### Alternative: Standalone Project

If you don’t want to create the GitHub repo first:

```bash
uvx copier copy gh:jlevy/simple-modern-pnpm my-project
cd my-project
pnpm install && pnpm format && pnpm build && pnpm test
git init && git add . && git commit -m "Initial commit"
```

### Update from Template

Pull in future template improvements:

```bash
uvx copier update
pnpm install && pnpm format && pnpm build && pnpm test
git add . && git commit -m "chore: update from simple-modern-pnpm template"
```

Copier performs a smart three-way merge and marks conflicts for you to resolve.

## Documentation

| Document | Description |
| --- | --- |
| [docs/development.md](docs/development.md) | Development setup, scripts, and config |
| [docs/publishing.md](docs/publishing.md) | Versioning and npm publishing |

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
