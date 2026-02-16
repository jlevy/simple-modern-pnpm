# Claude Code Context

This is a pnpm monorepo template project (simple-modern-pnpm).

## Project Documentation

- [Template architecture spec](admin/docs/project/specs/active/plan-2026-02-15-copier-template-architecture.md)
- [Admin directory guide](admin/admin-readme.md)
- [Template maintenance guide](admin/updating.md)

## Key Concepts

- The repo root is a fully functional project (CI passes, builds work, tests pass)
- A compile script (`admin/compile_template.py`) generates a Copier template from
  the working project by replacing fixed values with Jinja variables
- The compiled template lives in `template/` and is committed to git
- `copier.yml` at root configures Copier with `_subdirectory: template`

## Placeholder Values (Working Project)

These fixed values are used in the working project and get replaced with Jinja
variables in the compiled template:

| Value                         | Becomes                     |
| ----------------------------- | --------------------------- |
| `placeholder-workspace`       | `{{ workspace_name }}`      |
| `placeholder-package`         | `{{ package_name }}`        |
| `A modern TypeScript package` | `{{ package_description }}` |
| `Package Author`              | `{{ author_name }}`         |
| `author@example.com`          | `{{ author_email }}`        |
| `placeholder-org`             | `{{ github_org }}`          |
| `placeholder-repo`            | `{{ repo_name }}`           |

## Stack

- pnpm 10 + Node 22+
- TypeScript 5.9, ES2024 target
- tsdown for builds, Vitest 4 for tests
- ESLint 9 (flat config), Prettier
- Lefthook 2 for git hooks
- Changesets for versioning
