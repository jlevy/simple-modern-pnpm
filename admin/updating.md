# Template Maintenance Guide

## Updating Dependencies

1. Run `pnpm upgrade:check` to see available updates.
2. Apply updates with `pnpm upgrade` (minor/patch) or `pnpm upgrade:major` (major).
3. Run `pnpm build && pnpm test` to verify.
4. Run `pnpm compile-template` to regenerate the template.
5. Commit both the working project changes and the regenerated `admin/template/`.

## Adding New Configuration Files

If you add a new config file at the repo root (e.g., `.nvmrc`, `.editorconfig`):

- It is **automatically included** in the template output.
- If it contains any placeholder values (see `CLAUDE.md` for the mapping table),
  the compile script will replace them and add a `.jinja` suffix.
- No changes to the compile script are needed unless the file should be excluded.

## Excluding Files from Template

To exclude a new file or directory from the template output:

1. Add the path to the `EXCLUDED_PATHS` set in `admin/compile_template.py`.
2. Run `pnpm compile-template` to verify.

## Adding New Placeholder Variables

1. Add the working value and Jinja variable to the `REPLACEMENTS` list in
   `admin/compile_template.py` (keep longest-first ordering).
2. Add the variable definition to `copier.yml`.
3. Update the placeholder mapping table in `CLAUDE.md`.
4. Run `pnpm compile-template` and verify the output.

## Verifying Template Output

```bash
# Compile and check
pnpm compile-template
git diff admin/template/

# Test with Copier (requires copier installed)
copier copy --defaults --trust . /tmp/test-output
cd /tmp/test-output
pnpm install && pnpm build && pnpm test
```

## CI Validation

CI runs a `template-sync` check that:

1. Runs the compile script
2. Verifies `admin/template/` matches what's committed (`git diff --exit-code`)

If this check fails, run `pnpm compile-template` and commit the changes.
