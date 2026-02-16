# simple-modern-pnpm

A minimal, modern TypeScript project template using pnpm workspaces.

This template provides a production-ready monorepo structure with best practices for TypeScript
development. Use [Copier](https://copier.readthedocs.io/) to create new projects from this
template and pull upstream improvements over time.

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

## Quick Start

### Create a new project with Copier

```bash
# Install Copier (requires Python 3.9+)
pip install copier   # or: pipx install copier

# Create a new project (interactive prompts)
copier copy gh:jlevy/simple-modern-pnpm my-project
cd my-project

# Install dependencies and verify
pnpm install
pnpm build && pnpm test

# Initialize git and push
git init && git add . && git commit -m "Initial commit from simple-modern-pnpm"
gh repo create placeholder-org/my-project --source=. --push
```

### Pull upstream template updates

```bash
copier update
pnpm install && pnpm build && pnpm test
git add . && git commit -m "Update from simple-modern-pnpm template"
```

## Development

### Scripts

| Command              | Description              |
| -------------------- | ------------------------ |
| `pnpm build`         | Build all packages       |
| `pnpm test`          | Run tests                |
| `pnpm test:coverage` | Run tests with coverage  |
| `pnpm lint`          | Lint and auto-fix        |
| `pnpm lint:check`    | Lint without fixing (CI) |
| `pnpm format`        | Format code              |
| `pnpm format:check`  | Check formatting (CI)    |
| `pnpm typecheck`     | Type check all packages  |
| `pnpm ci`            | Run full CI pipeline     |

### Dependency Management

| Command              | Description                        |
| -------------------- | ---------------------------------- |
| `pnpm upgrade:check` | Check for available updates        |
| `pnpm upgrade`       | Safe upgrade (minor + patch)       |
| `pnpm upgrade:major` | Interactive major version upgrades |

### Versioning & Release

| Command                 | Description                         |
| ----------------------- | ----------------------------------- |
| `pnpm changeset`        | Create a changeset for your changes |
| `pnpm version-packages` | Apply changesets and bump versions  |
| `pnpm release`          | Build, validate, and publish to npm |

## Project Structure

```
.
├── .changeset/              # Changesets configuration
├── .github/workflows/       # CI/CD workflows
├── packages/
│   └── placeholder-package/          # Your package
│       ├── src/             # Source code
│       ├── tests/           # Tests
│       ├── package.json
│       ├── tsconfig.json
│       ├── tsdown.config.ts
│       └── vitest.config.ts
├── eslint.config.js         # ESLint flat config
├── .prettierrc              # Prettier config
├── lefthook.yml             # Git hooks
├── package.json             # Root workspace config
├── pnpm-workspace.yaml      # Workspace definition
└── tsconfig.base.json       # Shared TypeScript config
```

## Adding More Packages

1. Create a new directory under `packages/`:

   ```bash
   mkdir -p packages/new-package/src packages/new-package/tests
   ```

2. Copy and adapt configuration files from the existing package.

3. Add the package reference to root `tsconfig.json`:

   ```json
   {
     "references": [
       { "path": "./packages/placeholder-package" },
       { "path": "./packages/new-package" }
     ]
   }
   ```

## Configuration Details

### TypeScript

- `target: ES2024` - Modern JavaScript features
- `moduleResolution: "Bundler"` - Optimized for tsdown
- `noUncheckedIndexedAccess: true` - Safer array/object access
- `verbatimModuleSyntax: true` - Enforces explicit type imports

### ESLint

- Type-aware rules via `typescript-eslint`
- Promise safety rules (no floating promises, no misused promises)
- Consistent type imports (`import type`)
- Relaxed rules for test files

### Git Hooks (Lefthook)

- **Pre-commit**: Format, lint, and typecheck staged files
- **Pre-push**: Run full test suite

## Publishing

1. Create an npm account and generate an access token
2. Add `NPM_TOKEN` secret to your GitHub repository
3. Create a git tag: `git tag v0.1.0 && git push --tags`
4. The release workflow will automatically publish to npm

## License

MIT
