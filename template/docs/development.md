# Development Guide

## Prerequisites

- [Node.js](https://nodejs.org/) >= 24 (see `.nvmrc`)
- [pnpm](https://pnpm.io/) (enabled via `corepack enable`)
- [uv](https://docs.astral.sh/uv/) (recommended — used for `copier update` and flowmark
  markdown formatting)

## First Run

```bash
pnpm install
pnpm check
```

## Scripts

| Command | Description |
| --- | --- |
| `pnpm build` | Build all packages |
| `pnpm check` | Run the full local validation pipeline |
| `pnpm dev` | Run package build/watch scripts in parallel |
| `pnpm test` | Run tests |
| `pnpm test:watch` | Run package test watchers in parallel |
| `pnpm test:coverage` | Run tests with coverage |
| `pnpm lint` | Lint and auto-fix |
| `pnpm lint:check` | Lint without fixing (CI) |
| `pnpm format` | Format all files (Prettier + flowmark) |
| `pnpm format:md` | Format markdown only (flowmark) |
| `pnpm format:check` | Check code formatting (Prettier only, for CI) |
| `pnpm typecheck` | Type check all packages |
| `pnpm publint` | Validate package.json for publishing |
| `pnpm prepare` | Install git hooks when Git is available |

## Dependency Management

| Command | Description |
| --- | --- |
| `pnpm upgrade:check` | Check for available updates |
| `pnpm upgrade` | Safe upgrade (minor + patch) |
| `pnpm upgrade:major` | Interactive major version upgrades |

## Copier Lineage

This repo is designed to keep working with Copier after the initial render.

- Keep `.copier-answers.yml` committed.

- Use `uvx copier update` to pull upstream template changes.

- After any update, rerun:

  ```bash
  pnpm install
  pnpm check
  ```

If you created the repo before running `git init`, install hooks after Git exists:

```bash
git init -b main
pnpm prepare
```

If this repo was adopted from an older project, expect future `copier update` runs to
touch config files more often than app code.
Review merges carefully around `package.json`, `tsconfig`, ESLint, Lefthook, and GitHub
workflow files.

## Retrofit Notes

If you adopted this template into an existing repo:

- Replace the starter `packages/<package>/src/` and `packages/<package>/tests/` with
  your real code and tests.
- If your old repo kept `src/` or `tests/` at the root, move that code under
  `packages/<package>/` before running `pnpm check`, or update `pnpm-workspace.yaml` and
  root `tsconfig.json` references to match your custom layout.
- Merge runtime dependencies, exports, bin entries, and package metadata from the old
  root `package.json` into `packages/<package>/package.json`. The generated root
  `package.json` is for workspace tooling.

## Project Structure

```
.
├── .copier-answers.yml      # Copier state used by `copier update`
├── docs/                    # Project documentation
│   ├── development.md       # This file
│   └── publishing.md        # Publishing and release guide
├── packages/
│   └── <package>/           # Your package(s)
│       ├── src/             # Source code
│       ├── tests/           # Tests
│       ├── package.json
│       ├── tsconfig.json
│       ├── tsdown.config.ts # Build config
│       └── vitest.config.ts # Test config
├── .github/workflows/       # CI/CD workflows
├── eslint.config.js         # ESLint flat config
├── .prettierrc              # Prettier config (code files)
├── .flowmarkignore          # Flowmark ignore patterns (markdown)
├── lefthook.yml             # Git hooks
├── package.json             # Root workspace config
├── pnpm-workspace.yaml      # Workspace packages
├── scripts/
│   └── prepare-hooks.mjs    # Installs hooks only when Git is available
├── tsconfig.json            # Root TypeScript config (project references)
└── tsconfig.base.json       # Shared TypeScript settings
```

## Adding Packages

1. Create a new directory under `packages/`:

   ```bash
   mkdir -p packages/new-package/src packages/new-package/tests
   ```

2. Copy and adapt configuration files from the existing package (`package.json`,
   `tsconfig.json`, `tsdown.config.ts`, `vitest.config.ts`).

3. Add the package reference to root `tsconfig.json`:

   ```json
   {
     "references": [{ "path": "./packages/existing-package" }, { "path": "./packages/new-package" }]
   }
   ```

## Configuration

### TypeScript

- **Target**: ES2024 (modern JavaScript features for Node 24+)
- **Module resolution**: `Bundler` (optimized for tsdown)
- **Strict settings**: `noUncheckedIndexedAccess`, `verbatimModuleSyntax`,
  `exactOptionalPropertyTypes`

### ESLint

- Flat config (`eslint.config.js`) with type-aware rules via `typescript-eslint`
- Promise safety: no floating promises, no misused promises, await-thenable
- Consistent type imports (`import type`)
- Curly braces required for all control statements
- Relaxed rules for test files

### Formatting (Prettier + flowmark)

Code and markdown use separate formatters:

- **Prettier** handles code files (JS/TS, JSON, YAML) — configured in `.prettierrc`
- **[flowmark](https://github.com/jlevy/flowmark)** handles markdown (`.md` files) —
  does semantic line-breaking for cleaner diffs

Prettier is enforced in CI (`pnpm format:check` fails the build on code formatting
issues). Flowmark is best-effort: it runs in pre-commit hooks and via `pnpm format`, but
is not enforced in CI since markdown formatting rarely causes functional issues and
flowmark can be brittle on edge cases.

To disable flowmark locally, comment out the `format-md` command in `lefthook.yml`.

flowmark runs via `uvx` (no npm dependency — requires [uv](https://docs.astral.sh/uv/)
installed).

### Git Hooks (Lefthook)

- **Pre-commit** (parallel):
  - Format staged code files with Prettier
  - Format staged markdown with flowmark (via uvx)
  - Lint staged files with ESLint (with cache and auto-fix)
  - Type check with `pnpm typecheck`
- **Pre-push**:
  - Run full test suite with `pnpm test`

`pnpm install` skips hook installation if the directory is not a Git repo yet.
Run `pnpm prepare` after `git init` when you are ready to install hooks.

### Build (tsdown)

- ESM-only output (`.mjs` + `.d.mts`)
- Target: Node 24
- Source maps enabled
- TypeScript declarations generated

### Testing (Vitest)

- Coverage via `@vitest/coverage-v8`
- Reporters: text, json, json-summary

## Agent Context

Generated repos include `AGENTS.md` and `CLAUDE.md` copies of this guide so coding
agents can load the same repo instructions humans use.
