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
- Including dev tooling setup (Claude Code, tbd, etc.)
  in the template output.
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

| Working Value | Copier Variable | Used In |
| --- | --- | --- |
| `placeholder-workspace` | `{{ workspace_name }}` | root package.json `name` |
| `placeholder-package` | `{{ package_name }}` | package dir, package.json, tsconfig refs, CI |
| `A modern TypeScript package` | `{{ package_description }}` | package.json description, src/index.ts |
| `Package Author` | `{{ author_name }}` | package.json author |
| `author@example.com` | `{{ author_email }}` | package.json author |
| `placeholder-org` | `{{ github_org }}` | package.json repository URLs |
| `placeholder-repo` | `{{ repo_name }}` | package.json repository URLs |

### File Boundary: Template vs Template-Meta

All template administration lives in a single directory: `admin/`. The boundary rule is
simple:

> **Everything at root IS the project and goes into the template, except `admin/` and a
> small number of root-level files that must be there.**

**Root-level dot-directories — project vs admin:**

The compile script must distinguish between project dot-directories (included in
template) and admin dot-directories (excluded).
This classification is configured explicitly in the compile script:

| Directory | Classification | Reason |
| --- | --- | --- |
| `.github/` | **project** | CI/CD workflows — every generated project needs these |
| `.claude/` | **admin** | Claude Code settings for administering this template repo |
| `.tbd/` | **admin** | Issue tracking for this template repo |
| `attic/` | **admin** | Third-party repos cloned for reference during development |

**Excluded from template (configured in compile script):**

- `admin/` — all template admin (compile script, compiled output, docs, specs)
- `copier.yml` — Copier configuration (must be at repo root per Copier requirement)
- `README.md` — template documentation for GitHub visitors (generated projects get a
  different starter README created by the compile script)
- `LICENSE` — the template repo’s own license (generated projects get a placeholder
  LICENSE created by the compile script, prompting the user to fill in their own)
- Admin dot-directories: `.claude/`, `.tbd/`, `attic/`
- Standard build artifacts: `node_modules/`, `dist/`, `pnpm-lock.yaml`, `.git/`

**Everything else at root** goes into the template — no explicit include list needed.
If you add a new config file or directory at root, it’s automatically part of the
template. The exclusion list is the single source of truth, configured in the compile
script.

### Compile Script (`admin/compile_template.py`)

Python script (stdlib only, no dependencies) that:

1. Deletes and recreates `template/` (idempotent).
2. Walks the repo root, copying all files except excluded paths.
3. Replaces placeholder strings with Jinja `{{ variable }}` syntax in file contents.
4. Adds `.jinja` suffix to any file whose content was modified.
5. Renames `packages/placeholder-package/` to `packages/{{ package_name }}/` in the
   output.
6. Creates special Copier files:
   - `{{ _copier_conf.answers_file }}.jinja` (for `copier update` support)
   - `README.md.jinja` (starter README for generated projects)
   - `LICENSE` (placeholder text prompting the user to choose and add their own license)

Replacement ordering: longer/more-specific strings first to prevent partial matches.
None of the placeholder values is a substring of another, so ordering is safe but
longest-first is defensive.

Why Python: Copier requires Python, so it’s available.
Jinja `{{ }}` syntax is painful to escape in shell/sed.
Python’s pathlib and string operations are clean.

### Repository Layout After Migration

```
simple-modern-pnpm/
  # --- Root-level exceptions (not part of template) ---
  copier.yml                     # Copier config (_subdirectory: template)
  README.md                      # Template documentation for GitHub visitors

  # --- Compiled template output (at repo root, excluded from itself) ---
  template/                      # GENERATED by compile script, committed to git
    packages/{{ package_name }}/
      src/index.ts.jinja
      tests/index.test.ts        # no placeholders, plain copy
      package.json.jinja
      ...
    package.json.jinja
    tsconfig.json.jinja
    README.md.jinja              # Starter README (different from root)
    LICENSE                      # Placeholder (different from root)
    {{ _copier_conf.answers_file }}.jinja
    ... (config files, some with .jinja suffix)

  # --- Template admin (excluded from template) ---
  admin/
    admin-readme.md              # Documents admin/ structure and workflows
    compile_template.py          # Generates template/ from working project
    updating.md                  # Template maintenance guide
    docs/                        # Specs, planning docs
      specs/active/...

  # --- Everything below IS the project (all included in template) ---
  .github/workflows/
    ci.yml                       # Working CI + template-sync validation
    release.yml                  # Working release workflow
  packages/
    placeholder-package/                  # Fully functional package
      src/index.ts
      tests/index.test.ts
      package.json               # name: "placeholder-package"
      tsconfig.json
      tsdown.config.ts
      vitest.config.ts
  package.json                   # name: "placeholder-workspace"
  tsconfig.json                  # refs: "./packages/placeholder-package"
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
gh repo create placeholder-org/my-project --source=. --push
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

### Phase 0: Configuration Audit and Modernization

Before the Copier migration, audit every configuration area to ensure it reflects
current best practices.
For each area, compare four sources and take the best option:

1. **Current** — what’s in this repo today
2. **Guidelines** — `tbd guidelines pnpm-monorepo-patterns` (researched best practices)
3. **Reference repo** — `attic/tbd/` (more recently maintained, uses same stack)
4. **Latest versions** — check release pages for any newer versions

Parent bead: **`smp-7qqy`** — Backfill project setup improvements from tbd repo

#### 0.1 Root package.json (workspace config)

- [ ] `packageManager` version — Current: `pnpm@10.28.0`, tbd: `10.28.2`. Check latest
  at pnpm/pnpm releases.
  **`smp-71bs`**
- [ ] `engines.node` — Current: `>=22`, tbd: `>=20`, Guidelines: Node 24 LTS. Decide
  minimum version for generated projects vs template itself.
  **`smp-jq0u`**
- [ ] `pnpm.onlyBuiltDependencies` — Both have `[esbuild, lefthook]`. Confirm still
  correct. **`smp-a597`**
- [ ] Scripts: compare `format`, `lint`, `lint:check`, `build`, `test`, `release`,
  `upgrade` scripts. tbd adds `precommit`, `ci`, `format:md` (flowmark).
  Decide which belong in a starter template.
  **`smp-a9pg`** — Add `precommit` and `ci` convenience scripts.
  Note: `format:md` (flowmark) is tbd-specific — do not include in template.
- [ ] DevDependencies: bump all versions to latest.
  **`smp-71bs`** — pnpm 10.28.0→latest, prettier 3.8.0→latest, typescript-eslint
  8.53→latest, npm-check-updates 17→latest (guidelines: `^19.0.0`), lefthook (see 0.6
  for v1→v2 decision).

#### 0.2 TypeScript configs

- [ ] `tsconfig.base.json` — Current and tbd are identical (`ES2023`). Guidelines
  recommend `ES2024`. Decide whether to bump (aligns with Node 22+). **`smp-bo1i`**
- [ ] Root `tsconfig.json` — Will be updated when placeholders are converted.
  **`smp-bw6h`** (Phase 1)
- [ ] Package `tsconfig.json` — Current includes `["src", "tests", "*.config.ts"]`, tbd
  same. Guidelines only include `["src"]`. Keep current (type checking tests is useful).
  *(no change needed)*

#### 0.3 ESLint config

- [ ] Compare rules against tbd.
  Core rules (curly, brace-style, unused vars, promise safety, type imports,
  no-restricted-syntax for TSImportType) are identical — keep.
  tbd-specific rules to exclude from template: atomic file write restrictions,
  CLI/script overrides.
  **`smp-oj2f`** — Note: this bead proposes adding `attic/` to ignores and `scripts/`
  overrides. For the template, `attic/` is excluded and `scripts/` doesn’t exist, so
  these are admin-repo-only changes.
  For the template output: keep ESLint config as-is, plus add
  `no-restricted-imports: off` for test files (useful).
- [ ] Test file overrides — both identical.
  Keep.

#### 0.4 Prettier configs and markdown formatting (flowmark)

**Decision:** Use [flowmark](https://github.com/jlevy/flowmark) for markdown formatting
instead of Prettier.
Prettier handles code files (JS/TS/JSON/YAML); flowmark handles `.md` files.
This applies to both the admin repo and the template output.

Rationale: Prettier’s markdown formatting rewraps prose in ways that create noisy diffs.
Flowmark does semantic line-breaking (one sentence/clause per line), producing cleaner
diffs and more readable version-controlled prose.

flowmark runs via `uvx flowmark@latest --auto` — no npm dependency needed.
uv is already recommended for Copier, so this adds no new prerequisites.

- [x] `.prettierrc` — No changes needed (code-only settings).
- [x] `.prettierignore` — Add `*.md` so Prettier never touches markdown.
  Also add comment explaining flowmark handles markdown.
  Admin-only entries (`.tbd`, `attic/`, `template`) stay in root .prettierignore but are
  stripped from template output by the compile script.
- [x] `.flowmarkignore` — New file.
  Excludes `.claude/`, `.tbd/`, `node_modules/`, `template/` (admin-only).
  Template output gets a simpler version.
- [x] `package.json` scripts: - `format` →
  `prettier --write --log-level warn . && uvx flowmark@latest --auto .` - `format:check`
  → `prettier --check --log-level warn .` (Prettier only — flowmark excluded from CI
  checks since markdown formatting issues are rarely serious; noted in docs) - Add
  `format:md` → `uvx flowmark@latest --auto .` (standalone convenience)
- [x] `lefthook.yml` pre-commit: - `format` glob: remove `.md` →
  `*.{js,ts,tsx,json,yaml,yml}` - Add `format-md` command: glob `*.md`, run
  `uvx flowmark@latest --auto {staged_files}`
- [x] `docs/development.md` — Update prerequisites to recommend uv, update script
  descriptions, note flowmark for markdown
- [x] CI workflow — `format:check` stays Prettier-only (no flowmark in CI)

#### 0.5 npm/pnpm configs

- [ ] `.npmrc` — Identical.
  No changes. *(no bead)*
- [ ] `pnpm-workspace.yaml` — Keep `packages/*` only.
  *(no bead)*

#### 0.6 Git hooks (lefthook.yml)

- [ ] Lefthook version — Guidelines: `^2.0.15`. Current and tbd: `^1.13.6`. Decide:
  upgrade to v2 now? Check migration guide.
  **`smp-d5yn`** (research) + **`smp-71bs`** (version bump) + **`smp-6h0j`** (config
  changes)
- [x] Pre-commit format glob — Remove `.md` from Prettier glob.
  Add separate `format-md` command using flowmark via uvx.
  Applies to both admin repo and template output (see 0.4 for details).
- [ ] Pre-push — **`smp-6h0j`** proposes adding `build:check` before test and
  priorities. For template: keep simple (`pnpm test`). Guidelines recommend commit-hash
  caching — consider for a future improvement.

#### 0.7 Node version (.nvmrc)

- [ ] Reconcile all four locations: `.nvmrc` says `24`, root `engines` says `>=22`,
  package `engines` says `>=20`, CI uses `node-version: 20`. **`smp-jq0u`** (P0 bug) —
  Fix CI/CD Node version mismatch.
  Recommendation: `.nvmrc: 24`, `engines.node: ">=22"` (minimum supported), CI
  `node-version: 24`, package `engines.node: ">=22"`.

#### 0.8 Sub-package configs

- [ ] `package.json` exports format — Current: ESM-only (`./dist/index.mjs`).
  Guidelines: dual ESM+CJS. Decide for template.
  **`smp-4uik`**
- [ ] `engines.node` in package — align with 0.7 decision.
  **`smp-jq0u`**
- [ ] `devDependencies` versions — **`smp-71bs`**: - `@types/node`: `^22.10.7` → should
  match Node major (`^22.19.7` min, or `^24.0.0` if Node 24 is the target) - `vitest` +
  `@vitest/coverage-v8`: `^2.1.8` → decide v2 or v4 (guidelines: v4). **`smp-0brk`**
  (research) - `publint`: `^0.3.2` → latest (`^0.3.17`+) - `tsdown`: `0.20.0-beta.3`
  (pinned beta!) → `^0.20.1` (caret, stable)
- [ ] `tsdown.config.ts` target — `node20` → align with Node version decision.
  **`smp-71bs`**
- [ ] `vitest.config.ts` coverage reporters — **`smp-nl77`** proposes adding `lcov` and
  `html` reporters and explicit `reportsDirectory`. For template: keep minimal
  (`['text', 'json', 'json-summary']`). Apply richer reporters to admin repo only.

#### 0.9 Gitignore

- [ ] **`smp-4bff`** — Add `tmp/`, `*.tmp.*` entries and verify `dist/` is properly
  ignored as standalone entry (currently embedded in a comment block).
- [ ] **`smp-4nmp`** — Verify and fix `dist/` gitignore entry if needed.

#### 0.10 CI workflows

- [ ] Actions versions — **`smp-yf1d`** — Bump `actions/checkout@v4→v6` and
  `actions/setup-node@v4→v6` in both `ci.yml` and `release.yml`. Guidelines confirm v6
  is current.
- [ ] Node version in CI — **`smp-jq0u`** — Update `ci.yml` to Node 22+ and
  `release.yml` to Node 24. Align with 0.7 decision.
- [ ] CI structure — **`smp-qd6a`** proposes multi-OS matrix (ubuntu, macos, windows)
  and separating coverage into its own job.
  For template: keep single-OS (ubuntu-latest) for simplicity.
  Apply multi-OS only to admin repo CI if desired.
- [x] Release workflow pattern — **Resolved:** tag-triggered + OIDC trusted publishing.
  Changesets removed (see 0.11). **`smp-gaot`**
- [ ] **`smp-kwxd`** — Verify `permissions` scope is minimal.

#### 0.11 Release workflow: OIDC + tag-triggered (no Changesets)

**Decision:** Changesets has been removed.
The release workflow is tag-triggered with OIDC trusted publishing to npm (no
`NPM_TOKEN` secrets).

Rationale: Changesets adds ceremony (temp markdown files → version command → changelog
extraction → cleanup) that provides no value for a single-package template.
Agents and humans can write changelogs directly.
OIDC eliminates token management entirely — GitHub Actions presents an OIDC identity to
npm, which issues a one-time credential per workflow run with provenance attestation.

**Release flow:**

1. `pnpm release:changes` — review commits since last tag
2. Write `release-notes.md` — agent or human summarizes changes
3. (Optional) Review with user — agent checks if notes look ready
4. Bump version in `packages/PACKAGE/package.json`
5. Commit everything (including `release-notes.md`)
6. Tag and push — triggers CI

CI publishes automatically on `v*` tags and creates a GitHub Release using
`release-notes.md` as the body (`body_path: release-notes.md` in the workflow).

**Design principles:**

- `release-notes.md` is the source of truth for the GitHub Release body
- It is written and reviewed *before* tagging, not extracted from CHANGELOG after
- No package names are hardcoded in the release workflow — the workflow reads a single
  file from the repo root, making it package-name-agnostic
- No inline bash scripts in the workflow YAML beyond minimal GitHub Actions wiring
- `pnpm release:changes` is a simple `git log` one-liner (no external scripts) that
  shows all commits since the last tag; falls back to showing all commits if no tags
  exist

#### 0.12 CLAUDE.md and agent configs (admin-only)

These are excluded from template output.
Changes here improve the admin repo only.

- [ ] **`smp-i4fb`** — Add `CLAUDE.md` at repo root pointing to project documentation.
  Must also add `CLAUDE.md` to compile script exclusion list.
- [ ] **`smp-i6ri`** — Claude Code settings: add `CLAUDE_CODE_SUBAGENT_MODEL` env var,
  fix hook ordering (ensure-gh-cli before tbd-session).
- [ ] Verify exclusion list includes `.claude/`, `.tbd/`, `CLAUDE.md`, `AGENTS.md`.

#### 0.13 Remaining config files

- [ ] `LICENSE` — Root keeps real license, template gets placeholder.
  Already addressed in this spec.
  *(no bead)*
- [ ] **`smp-9qjw`** — Create `.gitattributes` file at repo root.
  (Missing from original checklist.
  tbd has one? Verify what it should contain — typically `* text=auto` for line ending
  normalization.)

#### Audit Decisions Summary

After completing the audit, the key decisions to make are:

1. **Node version floor**: `>=20` vs `>=22` for generated projects.
   **`smp-jq0u`**
2. **Vitest version**: Stay on v2 or jump to v4? **`smp-0brk`**
3. **Lefthook version**: Stay on v1 or upgrade to v2? **`smp-d5yn`**
4. **CI actions versions**: Upgrade to v6 — verify runner compat.
   **`smp-yf1d`**
5. **tsdown version**: Use caret range (`^0.20.1`) not pinned beta.
   **`smp-71bs`**
6. **Release workflow pattern**: ~~Tag-triggered or changesets/action?~~ **Resolved:**
   Tag-triggered + OIDC, no changesets.
   **`smp-gaot`**
7. **ESM-only or dual-format exports**: For starter package.
   **`smp-4uik`**
8. **TypeScript target**: ES2023 or ES2024? **`smp-bo1i`**

### Phase 1: Convert Working Project and Create Compile Infrastructure

- [ ] **`smp-bw6h`** — Replace all `TODO-*` placeholders with fixed working values (see
  mapping table)
- [ ] **`smp-bw6h`** — Rename `packages/TODO-package-name/` to
  `packages/placeholder-package/`
- [ ] **`smp-bw6h`** — Run `pnpm install` to regenerate lockfile, verify
  `pnpm build && pnpm test` pass
- [ ] **`smp-41bx`** — Create `copier.yml` with variable definitions and
  `_subdirectory: template`
- [ ] **`smp-41bx`** — Create `admin/compile_template.py` (the reverse-compile script)
- [ ] **`smp-41bx`** — Run compile script to generate `template/`
- [ ] **`smp-lj06`** — Verify compiled output: check `.jinja` suffixes, directory
  naming, variable substitutions
- [ ] **`smp-6z1z`** — Add `"compile-template": "python admin/compile_template.py"`
  script to root package.json
- [ ] **`smp-4kai`** — Rewrite `README.md` as template documentation (Copier usage,
  workflows)
- [ ] **`smp-4kai`** — Create `admin/admin-readme.md` documenting the admin/ directory
  structure, the reverse-compile workflow, and template boundary
- [ ] **`smp-4kai`** — Create `admin/updating.md` with template maintenance guide
- [ ] Move `docs/` into `admin/docs/` *(already done)*

### Phase 2: CI Validation and End-to-End Testing

- [ ] **`smp-gz3b`** — Add `template-sync` job to CI that runs compile script and
  verifies `template/` matches committed version (`git diff --exit-code`)
- [ ] **`smp-gz3b`** — Add template rendering test to CI:
  `copier copy --defaults --trust . /tmp/test` then verify key files exist with correct
  substituted values
- [ ] **`smp-ttr1`** — Test Workflow 1 manually: `copier copy` into a temp dir,
  `pnpm install && build && test`
- [ ] **`smp-ttr1`** — Test `copier update` manually: make a change to template, tag,
  update downstream
- [ ] Commit everything

### Phase 3: Push Findings Upstream to Guidelines

**`smp-lli3`** — After completing the audit and implementation, push learnings back to
the `tbd guidelines pnpm-monorepo-patterns` document so the guidelines stay in sync with
what we actually ship in this template.

- [ ] Review each audit decision (items 1-8 above) and update the guidelines version
  table and recommendations where our findings differ
- [ ] Update Node.js version recommendations if we settled on different targets
- [ ] Update CI workflow examples (actions versions, Node versions) to match what we
  validated
- [ ] Update Vitest version recommendation based on v2→v4 research findings
- [ ] Update Lefthook version recommendation based on v1→v2 research findings
- [ ] Update tsdown version recommendation (caret range, stable vs beta)
- [ ] Add any new patterns discovered (e.g., ESM-only vs dual exports guidance, release
  workflow pattern recommendation)
- [ ] Update `.prettierignore` example if it changed
- [ ] Update `lefthook.yml` examples if the recommended pattern changed
- [ ] Note any open items or corrections in the guidelines’ “Open Research Questions”
  section
- [ ] Verify the “Last Researched Versions” table in the guidelines is current

## Testing Strategy

- **Working project CI**: Existing CI continues to build/test the working project
  itself.
- **Template sync check**: CI verifies `template/` matches compile script output.
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
