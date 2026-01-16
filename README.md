# simple-modern-pnpm

A minimal, modern TypeScript project template using pnpm workspaces.

This template provides a production-ready monorepo structure with best practices for TypeScript
development, following patterns documented in modern TypeScript ecosystem research.

## Features

- **pnpm workspaces** - Efficient monorepo dependency management
- **TypeScript 5.7+** - Modern TypeScript with strict configuration
- **tsdown** - Fast ESM builds with TypeScript declarations
- **Vitest** - Fast unit testing with coverage
- **ESLint 9** - Flat config with type-aware rules
- **Prettier** - Consistent code formatting
- **Lefthook** - Fast git hooks (format, lint, typecheck on commit; test on push)
- **Changesets** - Automated versioning and changelog generation
- **GitHub Actions** - CI/CD for testing and npm publishing

## Quick Start

### Using This Template

1. Click "Use this template" on GitHub, or clone and remove git history:

   ```bash
   git clone https://github.com/TODO-github-org/simple-modern-pnpm.git my-project
   cd my-project
   rm -rf .git
   git init
   ```

2. Find and replace all `TODO-*` placeholders:

   | Placeholder           | Replace with        | Example                |
   | --------------------- | ------------------- | ---------------------- |
   | `TODO-workspace-name` | Your workspace name | `my-project-workspace` |
   | `TODO-package-name`   | Your package name   | `my-package`           |
   | `TODO-description`    | Package description | `A useful library`     |
   | `TODO-author-name`    | Your name           | `Jane Doe`             |
   | `TODO-author-email`   | Your email          | `jane@example.com`     |
   | `TODO-github-org`     | GitHub org/username | `janedoe`              |
   | `TODO-repo-name`      | Repository name     | `my-project`           |

3. Rename the package directory:

   ```bash
   mv packages/TODO-package-name packages/your-package-name
   ```

4. Update `tsconfig.json` to reference your package:

   ```json
   {
     "files": [],
     "references": [{ "path": "./packages/your-package-name" }]
   }
   ```

5. Install dependencies and verify everything works:

   ```bash
   pnpm install
   pnpm build
   pnpm test
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
│   └── TODO-package-name/   # Your package
│       ├── src/             # Source code
│       ├── tests/           # Tests
│       ├── package.json
│       ├── tsconfig.json
│       ├── tsdown.config.ts
│       └── vitest.config.ts
├── .eslintconfig.js         # ESLint flat config
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
     "references": [{ "path": "./packages/existing-package" }, { "path": "./packages/new-package" }]
   }
   ```

## Configuration Details

### TypeScript

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
