# Feature: Migrate to Maintainable Copier Template Architecture

**Date:** 2026-02-15

**Author:** Joshua Levy

**Status:** Draft

## Overview

Migrate simple-modern-pnpm from manual `TODO-*` placeholder replacement to a
[Copier](https://copier.readthedocs.io/)-based template architecture.
The key innovation is a “reverse compile” approach: the repo root remains a fully
functional, testable project using fixed placeholder names, and a compile script
generates the Copier `template/` subdirectory from it.
This eliminates the duplication problem where you must maintain both a working project
and a template directory.

This follows the pattern established by
[simple-modern-uv](https://github.com/jlevy/simple-modern-uv) but improves on it: in
simple-modern-uv, the template directory is maintained manually and has no CI of its
own. Here, the working project IS the test for the template.

## Goals

- The repo root is a fully functional project: CI passes, tests pass, builds work.
- A deterministic compile step generates `template/` from the working project.
- Users can instantiate new projects via `copier copy`.
- Users can pull upstream template changes via `copier update`.
- CI validates that `template/` is in sync with the working project.
- Clear, strict separation between “project files” (go into template) and “template-meta
  files” (stay out of template).

## Non-Goals

- Multi-package template generation (only one starter package for now).
- Template variable validators or conditional questions (keep it simple).
- Automated `pnpm install` post-generation tasks (document in after-copy message
  instead).
- Templating the LICENSE file (users can modify post-generation).
- Including dev tooling setup (Claude Code, tbd, etc.) in the template output.
  For v1, users set up their own `.claude/`, `.tbd/`, and similar tooling after
  instantiation. A future version could optionally scaffold these.

## Background

### The Problem

Template repos have a fundamental tension: you want the template to be a testable,
working project, but you also want it to serve as a Copier/Cookiecutter source with
Jinja variables. Maintaining both means duplication and drift.

### Why Copier

Copier is the leading tool for template instantiation + upstream merging.
Its `copier update` command does a three-way diff: regenerates the old template version,
computes what you changed locally, and applies the new template on top.
This means users can pull improvements from this template into their projects months or
years later.

### The “Reverse Compile” Insight

Instead of maintaining a `template/` directory with Jinja syntax and a separate working
project, we maintain only the working project.
A compile script mechanically transforms it into the template by replacing fixed
placeholder values with `{{ variable }}` syntax.
The compiled output is committed to git so Copier clients can access it.

### Reference Implementation

simple-modern-uv uses `_subdirectory: template` in its `copier.yml` and maintains the
template directory manually.
Its variables: `package_name`, `package_module`, `package_description`,
`package_author_name`, `package_author_email`, `package_github_org`.

## Design

### Placeholder Mapping

The working project uses fixed placeholder names.
The compile script replaces them with Jinja variables:

| Working Value                 | Copier Variable             | Used In                                      |
| ----------------------------- | --------------------------- | -------------------------------------------- |
| `my-workspace`                | `{{ workspace_name }}`      | root package.json `name`                     |
| `my-package`                  | `{{ package_name }}`        | package dir, package.json, tsconfig refs, CI |
| `A modern TypeScript package` | `{{ package_description }}` | package.json description, src/index.ts       |
| `Package Author`              | `{{ author_name }}`         | package.json author                          |
| `author@example.com`          | `{{ author_email }}`        | package.json author                          |
| `my-org`                      | `{{ github_org }}`          | package.json repository URLs                 |
| `my-repo`                     | `{{ repo_name }}`           | package.json repository URLs                 |

### File Boundary: Template vs Template-Meta

All template administration lives in a single directory: `admin/`.
The boundary rule is simple:

> **Everything at root IS the project and goes into the template, except `admin/`
> and a small number of root-level files that must be there.**

**Root-level dot-directories — project vs admin:**

The compile script must distinguish between project dot-directories (included in
template) and admin dot-directories (excluded). This classification is configured
explicitly in the compile script:

| Directory     | Classification | Reason                                                    |
| ------------- | -------------- | --------------------------------------------------------- |
| `.github/`    | **project**    | CI/CD workflows — every generated project needs these     |
| `.changeset/` | **project**    | Versioning config — part of the release workflow          |
| `.claude/`    | **admin**      | Claude Code settings for administering this template repo |
| `.tbd/`       | **admin**      | Issue tracking for this template repo                     |
| `attic/`      | **admin**      | Third-party repos cloned for reference during development |

**Excluded from template (configured in compile script):**

- `admin/` — all template admin (compile script, compiled output, docs, specs)
- `copier.yml` — Copier configuration (must be at repo root per Copier requirement)
- `README.md` — template documentation for GitHub visitors (generated projects get a
  different starter README created by the compile script)
- Admin dot-directories: `.claude/`, `.tbd/`, `attic/`
- Standard build artifacts: `node_modules/`, `dist/`, `pnpm-lock.yaml`, `.git/`

**Everything else at root** goes into the template — no explicit include list needed.
If you add a new config file or directory at root, it's automatically part of the
template. The exclusion list is the single source of truth, configured in the compile
script.

### Compile Script (`admin/compile_template.py`)

Python script (stdlib only, no dependencies) that:

1. Deletes and recreates `admin/template/` (idempotent).
2. Walks the repo root, copying all files except excluded paths.
3. Replaces placeholder strings with Jinja `{{ variable }}` syntax in file contents.
4. Adds `.jinja` suffix to any file whose content was modified.
5. Renames `packages/my-package/` to `packages/{{ package_name }}/` in the output.
6. Creates special Copier files:
   - `{{ _copier_conf.answers_file }}.jinja` (for `copier update` support)
   - `README.md.jinja` (starter README for generated projects)

Replacement ordering: longer/more-specific strings first to prevent partial matches.
None of the placeholder values is a substring of another, so ordering is safe but
longest-first is defensive.

Why Python: Copier requires Python, so it's available.
Jinja `{{ }}` syntax is painful to escape in shell/sed.
Python's pathlib and string operations are clean.

### Repository Layout After Migration

```
simple-modern-pnpm/
  # --- Root-level exceptions (not part of template) ---
  copier.yml                     # Copier config (_subdirectory: admin/template)
  README.md                      # Template documentation for GitHub visitors

  # --- Template admin (all in one place, excluded from template) ---
  admin/
    admin-readme.md              # Documents admin/ structure and workflows
    compile_template.py          # Generates admin/template/ from working project
    updating.md                  # Template maintenance guide
    docs/                        # Specs, planning docs
      specs/active/...
    template/                    # GENERATED by compile script, committed to git
      packages/{{ package_name }}/
        src/index.ts.jinja
        tests/index.test.ts      # no placeholders, plain copy
        package.json.jinja
        ...
      package.json.jinja
      tsconfig.json.jinja
      README.md.jinja            # Starter README (different from root)
      {{ _copier_conf.answers_file }}.jinja
      ... (config files, some with .jinja suffix)

  # --- Everything below IS the project (all included in template) ---
  .changeset/
  .github/workflows/
    ci.yml                       # Working CI + template-sync validation
    release.yml                  # Working release workflow
  packages/
    my-package/                  # Fully functional package
      src/index.ts
      tests/index.test.ts
      package.json               # name: "my-package"
      tsconfig.json
      tsdown.config.ts
      vitest.config.ts
  package.json                   # name: "my-workspace"
  tsconfig.json                  # refs: "./packages/my-package"
  tsconfig.base.json
  eslint.config.js
  .prettierrc
  lefthook.yml
  pnpm-workspace.yaml
  .gitignore
  LICENSE
  ... (other config files)
```

### User Workflows

#### Workflow 1: Create a new repo end-to-end

```bash
# Install copier
pip install copier   # or pipx install copier

# Create project (interactive prompts)
copier copy gh:jlevy/simple-modern-pnpm my-project
cd my-project

# Initialize and push
pnpm install
pnpm build && pnpm test
git init && git add . && git commit -m "Initial commit from simple-modern-pnpm"
gh repo create my-org/my-project --source=. --push
```

#### Workflow 2: Copy into an existing repo

```bash
# From inside an existing repo
copier copy gh:jlevy/simple-modern-pnpm .
# Copier writes files; you review diffs and resolve any conflicts
pnpm install
pnpm build && pnpm test
git add . && git commit -m "Add simple-modern-pnpm template structure"
```

#### Workflow 3: Migrate an existing repo to this template

This is the hardest case: an existing project with its own scaffolding that roughly fits
the pnpm monorepo pattern but doesn’t match exactly.

```bash
# 1. Create a clean branch
git checkout -b migrate-to-template

# 2. Copy the template on top of existing code
copier copy --overwrite gh:jlevy/simple-modern-pnpm .

# 3. Review ALL diffs carefully
git diff

# 4. The template will have overwritten config files (package.json, tsconfig, eslint, etc.)
#    You need to:
#    - Merge your dependencies into the new package.json(s)
#    - Preserve your source code (src/ files are generic stubs from template)
#    - Keep your existing tests
#    - Adapt CI workflows if you have custom steps
git checkout HEAD -- src/ tests/  # restore your actual code
# Manually merge package.json, tsconfig, etc.

# 5. Verify everything works
pnpm install
pnpm build && pnpm test

# 6. Commit
git add . && git commit -m "Migrate to simple-modern-pnpm template"
```

After migration, `.copier-answers.yml` tracks the template version, and future
`copier update` calls work normally.

#### Ongoing: Pull upstream template changes

```bash
# Ensure clean working tree
git stash --include-untracked  # if needed

# Pull template updates
copier update

# Resolve any conflicts (inline markers or .rej files)
# Review changes
pnpm install && pnpm build && pnpm test

# Commit
git add . && git commit -m "Update from simple-modern-pnpm template"
```

## Implementation Plan

### Phase 1: Convert Working Project and Create Compile Infrastructure

- [ ] Replace all `TODO-*` placeholders with fixed working values (see mapping table)
- [ ] Rename `packages/TODO-package-name/` to `packages/my-package/`
- [ ] Run `pnpm install` to regenerate lockfile, verify `pnpm build && pnpm test` pass
- [ ] Create `copier.yml` with variable definitions and `_subdirectory: admin/template`
- [ ] Create `admin/compile_template.py` (the reverse-compile script)
- [ ] Run compile script to generate `admin/template/`
- [ ] Manually verify compiled output: check `.jinja` suffixes, directory naming,
      variable substitutions
- [ ] Add `"compile-template": "python admin/compile_template.py"` script to root
      package.json
- [ ] Rewrite `README.md` as template documentation (Copier usage, workflows)
- [ ] Create `admin/admin-readme.md` documenting the admin/ directory structure,
      the reverse-compile workflow, and how the template boundary works
- [ ] Create `admin/updating.md` with template maintenance guide
- [ ] Move `docs/` into `admin/docs/`

### Phase 2: CI Validation and End-to-End Testing

- [ ] Add `template-sync` job to CI that runs compile script and verifies
      `admin/template/` matches committed version (`git diff --exit-code`)
- [ ] Add template rendering test to CI: `copier copy --defaults --trust . /tmp/test`
      then verify key files exist with correct substituted values
- [ ] Test Workflow 1 manually: `copier copy` into a temp dir,
      `pnpm install && build && test`
- [ ] Test `copier update` manually: make a change to template, tag, update downstream
- [ ] Commit everything

## Testing Strategy

- **Working project CI**: Existing CI continues to build/test the working project
  itself.
- **Template sync check**: CI verifies `admin/template/` matches compile script output.
- **Template render test**: CI renders template with `--defaults` and validates output.
- **Manual end-to-end**: Test all three user workflows before merging.

## Open Questions

- Should we include `pnpm-lock.yaml` in the template?
  (Current recommendation: no, regenerated per project.
  But including it gives reproducible first install.)
- Should the starter README for generated projects include all the dev workflow tables
  from the current README, or be minimal?
- Should we add Copier `_tasks` to auto-run `pnpm install` after copy?
  (Risk: requires Node.js installed at copy time, which may not be the case.)

## References

- [Copier documentation](https://copier.readthedocs.io/)
- [simple-modern-uv](https://github.com/jlevy/simple-modern-uv) (sibling template,
  reference implementation)
- [Copier updating workflow](https://copier.readthedocs.io/en/stable/updating/)
