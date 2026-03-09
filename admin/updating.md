# Template Maintenance Guide

## Updating Dependencies

1. Run `pnpm upgrade:check` to see available updates.
2. Apply updates with `pnpm upgrade` (minor/patch) or `pnpm upgrade:major` (major).
3. Run `pnpm build && pnpm test` to verify.
4. Run `pnpm compile-template` to regenerate the template.
5. Run `python admin/smoke_test_template.py`.
6. Commit both the working project changes and the regenerated `template/`.

## Releasing The Template

Template releases are tag-driven for Copier consumers.
See `admin/releasing.md` for the maintainer process, tag policy, and GitHub release
steps.

## Adding New Configuration Files

If you add a new config file at the repo root (e.g., `.nvmrc`, `.editorconfig`):

- It is **automatically included** in the template output.
- If it contains any placeholder values from `admin/compile_template.py`, the compile
  script will replace them and add a `.jinja` suffix.
- No changes to the compile script are needed unless the file should be excluded.

## Excluding Files from Template

To exclude a new file or directory from the template output:

1. Add the path to the `EXCLUDED_ROOT_PATHS` set in `admin/compile_template.py`.
2. Run `pnpm compile-template` to verify.

## Adding New Placeholder Variables

1. Add the working value and Jinja variable to the `REPLACEMENTS` list in
   `admin/compile_template.py` (keep longest-first ordering).
2. Add the variable definition to `copier.yml`.
3. Run `pnpm compile-template` and verify the output.

## Verifying Template Output

```bash
# Compile and check
pnpm compile-template
git diff template/

# Render and verify end-to-end
python admin/smoke_test_template.py
```

## CI Validation

CI runs admin-only checks that:

1. Runs the compile script
2. Verifies `template/` matches what’s committed (`git diff --exit-code`)
3. Renders the template with Copier and verifies the generated repo installs, builds,
   tests, passes `pnpm check`, survives `copier update`, and can adopt a flat legacy
   repo layout into the generated workspace package structure

If these checks fail, run `pnpm compile-template`, rerun
`python admin/smoke_test_template.py`, and commit the resulting changes.
