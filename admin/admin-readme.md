# admin/

This directory contains all template administration files.
Nothing in `admin/` is included in the generated template output.

## Contents

- `compile_template.py` — Generates `template/` from the working project by replacing
  fixed placeholder values with Copier `[[ variable ]]` syntax.
- `smoke_test_template.py` — Renders the compiled template into a temp directory and
  verifies install/build/test/check/bootstrap behavior.
- `admin-readme.md` — This file.
- `updating.md` — Guide for maintaining the template.
- `docs/` — Project specs and planning documents.

## How It Works

The repo root is a fully functional project that CI tests directly.
The compile script mechanically transforms it into a Copier template:

1. Walks all files at the repo root (excluding `admin/`, `.claude/`, `.tbd/`, etc.)
2. Replaces working placeholder values (e.g., `placeholder-package`) with Copier
   template variables (e.g., `[[ package_name ]]`)
3. Adds `.jinja` suffix to any file whose content was modified
4. Renames `packages/placeholder-package/` to `packages/[[ package_name ]]/`
5. Strips template-admin-only content from generated files
6. Creates special files: starter README, MIT LICENSE template, Copier answers file

## Workflow

```bash
# After making changes to the working project:
pnpm compile-template    # Regenerate template/
python admin/smoke_test_template.py
pnpm check               # Verify the working project still passes

# CI validates that template/ is in sync and that a rendered repo works
```
