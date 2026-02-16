# admin/

This directory contains all template administration files. Nothing in `admin/` is
included in the generated template output.

## Contents

- `compile_template.py` — Generates `admin/template/` from the working project
  by replacing fixed placeholder values with Jinja `{{ variable }}` syntax.
- `template/` — The compiled Copier template (generated, committed to git).
- `admin-readme.md` — This file.
- `updating.md` — Guide for maintaining the template.
- `docs/` — Project specs and planning documents.

## How It Works

The repo root is a fully functional project that CI tests directly. The compile
script mechanically transforms it into a Copier template:

1. Walks all files at the repo root (excluding `admin/`, `.claude/`, `.tbd/`, etc.)
2. Replaces working placeholder values (e.g., `placeholder-package`) with Jinja variables
   (e.g., `{{ package_name }}`)
3. Adds `.jinja` suffix to any file whose content was modified
4. Renames `packages/placeholder-package/` to `packages/{{ package_name }}/`
5. Creates special files: starter README, placeholder LICENSE, Copier answers file

## Workflow

```bash
# After making changes to the working project:
pnpm compile-template    # Regenerate admin/template/
pnpm build && pnpm test  # Verify the working project still passes

# CI validates that admin/template/ is in sync with the compile script output
```
