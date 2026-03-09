# Template Release Guide

This guide is for releasing the template itself.
It is separate from the generated-project release workflow in
`.github/workflows/release.yml`, which exists for repos created from this template.

## Copier Version Selection

Copier chooses template versions from Git tags, not from GitHub Release metadata.

- `copier copy gh:jlevy/simple-modern-pnpm` uses the latest Git tag by default.
- `copier update` also moves to the latest available tag by default.
- If maintainers want to test unreleased template changes, use `--vcs-ref=HEAD` or a
  specific branch, commit, or tag.
- If we ever publish prereleases, use PEP 440-compatible version tags and remember that
  Copier ignores prereleases unless users opt in with `--prereleases` or an explicit
  `--vcs-ref`.

The practical rule is simple: the newest stable Git tag is the default version that
Copier users will get.
Creating a GitHub Release without creating or moving a tag does not change what Copier
pulls.

## Release Policy

- Use SemVer tags: `v0.1.0`, `v0.1.1`, `v0.2.0`.
- Only tag commits that have passed:
  - `pnpm compile-template`
  - `pnpm check`
  - `python admin/smoke_test_template.py`
- Write template release notes under `admin/releases/`.
- Keep the tag and the GitHub Release in sync.
- Treat the Git tag as the source of truth for Copier consumers.

## Why The Root Release Workflow Is Guarded

The root `.github/workflows/release.yml` is intentionally kept for generated repos.
In this template-maintainer repo, an admin-only guard skips that workflow when the
repository is `jlevy/simple-modern-pnpm`, so tagging the template does not try to
publish the placeholder package to npm.

That guard is stripped from generated repos during `pnpm compile-template`, so generated
projects still receive the normal npm/OIDC release workflow.

## Release Checklist

1. Start from `main` with a clean working tree.

2. Finish and commit any template changes.

3. Regenerate and validate the template:

   ```bash
   pnpm compile-template
   pnpm check
   python admin/smoke_test_template.py
   ```

4. Write release notes at `admin/releases/vX.Y.Z.md`.

5. Push `main`:

   ```bash
   git push origin main
   ```

6. Create and push the tag:

   ```bash
   git tag vX.Y.Z
   git push origin vX.Y.Z
   ```

7. Create the GitHub Release from the same notes file:

   ```bash
   gh release create vX.Y.Z \
     --title "vX.Y.Z" \
     --notes-file admin/releases/vX.Y.Z.md
   ```

8. Verify the release page and tag.

## Updating An Existing Draft Before Tagging

If you need to test template changes before cutting a tag:

```bash
uvx copier copy --vcs-ref=HEAD gh:jlevy/simple-modern-pnpm my-project
```

or use a local checkout:

```bash
uvx copier copy /path/to/simple-modern-pnpm my-project
```

Do not create a tag until the smoke test and maintainer checks are green.

## File Conventions

- Template release process: `admin/releasing.md`
- Template release notes: `admin/releases/vX.Y.Z.md`
- Generated-project release notes template: `release-notes.md`

Do not overwrite the root `release-notes.md` when releasing the template itself.
