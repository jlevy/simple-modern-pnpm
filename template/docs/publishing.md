# Publishing Guide

This project uses [Changesets](https://github.com/changesets/changesets) for versioning
and a tag-triggered GitHub Actions workflow for publishing to npm.

## Workflow Overview

1. **During development**: Create changesets to describe your changes.
2. **Before release**: Apply changesets to bump versions and generate changelogs.
3. **To release**: Create a git tag and push it.
   CI publishes to npm automatically.

## Creating Changesets

After making changes, create a changeset:

```bash
pnpm changeset
```

This prompts you to:

- Select which packages changed
- Choose a semver bump level (patch, minor, major)
- Write a summary of the change

The changeset is saved as a markdown file in `.changeset/`. Commit it with your code.

## Versioning

When ready to release, apply all pending changesets:

```bash
pnpm version-packages
```

This:

- Bumps package versions according to the changesets
- Generates/updates `CHANGELOG.md` in each affected package
- Removes the consumed changeset files

Review the version bumps and changelog entries, then commit.

## Publishing

### One-Time Setup

1. Create an [npm](https://www.npmjs.com/) account if you don’t have one.
2. Generate an access token (granular token with publish permission).
3. Add the token as `NPM_TOKEN` in your GitHub repository secrets (Settings > Secrets
   and variables > Actions).

### Releasing

```bash
# Commit the version bump from `pnpm version-packages`
git add . && git commit -m "Version packages"

# Create and push a tag
git tag v0.1.0
git push && git push --tags
```

The release workflow (`.github/workflows/release.yml`) will:

1. Build all packages
2. Run `publint` to validate package.json
3. Publish to npm with provenance
4. Create a GitHub Release with changelog notes

### Manual Publishing

If you need to publish without CI:

```bash
pnpm release
```

This runs `pnpm build && pnpm publint && changeset publish`.

## Quick Reference

| Command                 | Description                             |
| ----------------------- | --------------------------------------- |
| `pnpm changeset`        | Create a changeset for your changes     |
| `pnpm version-packages` | Apply changesets, bump versions         |
| `pnpm release`          | Build, validate, and publish (manually) |
