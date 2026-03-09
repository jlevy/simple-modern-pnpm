# Feature: Clarify Copier Workflows and Harden Agent-Friendly Template UX

**Date:** 2026-03-09 (last updated 2026-03-09)

**Author:** Codex

**Status:** Implemented

## Overview

Harden the template so a freshly rendered project works cleanly, then rewrite the
documentation around the full set of intended Copier workflows:

- create a brand-new project from the template
- render into a local scratch directory
- adopt the template into an existing TypeScript repo
- pull future upstream changes with `copier update`

The end state should match the intended positioning for this repo: an agent-friendly
template for a modern model repo in TypeScript using pnpm.

## Goals

- Generated projects work on first render without shipping broken admin-only commands or
  config.
- The root README clearly guides users to the right workflow for new, existing, and
  ongoing-template-update scenarios.
- Generated project docs are concrete, consistent, and usable by both humans and coding
  agents.
- Template validation catches render regressions before they ship.

## Non-Goals

- Redesigning the underlying TypeScript, pnpm, Vitest, ESLint, or tsdown stack.
- Expanding the template to multiple starter packages.
- Adding optional scaffolding for admin-only tools such as `.tbd/` or `.claude/`.
- Reworking unrelated backlog items such as broader CI matrix expansion.

## Background

The 2026-03-09 review found several verified gaps between the intended template UX and
the actual shipped behavior:

- generated projects include a broken `compile-template` script that points to a missing
  `admin/compile_template.py`
- the documented standalone bootstrap path fails because `pnpm install` runs
  `lefthook install` before the directory is a Git repo
- docs recommend `pnpm ci`, which conflicts with pnpm’s built-in `ci` command
- the rendered project does not currently pass its own advertised local CI path
- public docs omit the retrofit workflow for existing TypeScript repos
- generated output still leaks template-admin concepts such as `template/**` and
  `attic/**`
- generated publishing/readme/license defaults are inconsistent

These problems combine into a larger issue: the template’s agent-friendly positioning is
not yet backed by a deterministic, well-documented first-run experience.

Follow-up automation work also exposed a retrofit-specific refinement: when an older
single-package repo keeps TypeScript at the root, the adoption workflow must explicitly
migrate that code into the generated workspace package layout, or update the workspace
configuration before running `pnpm check`.

## Design

### Approach

Treat rendered-template correctness as the source of truth, then align all public docs
with the actual workflow that passes validation.

Implementation should follow this order:

1. Remove or fix correctness defects in generated output.
2. Add automated validation that renders a project and exercises the bootstrap path.
3. Rewrite the docs and generated README around explicit workflow selection.
4. Tighten the agent-friendly positioning so it describes real guarantees rather than
   aspirations.

### Components

- `admin/compile_template.py` and compiled `template/`
- root `README.md`
- generated `template/README.md.jinja`
- generated `docs/development.md` and `docs/publishing.md`
- root and generated `package.json` scripts
- root and generated `lefthook.yml` and `eslint.config.js`
- GitHub Actions workflows, especially template validation

### API Changes

There are no runtime library API changes.

Implemented user-facing workflow changes:

- the documented local full-check command is now `pnpm check`
- the bootstrap flow supports `pnpm install` before `git init`, with `pnpm prepare`
  documented for the post-Git hook-install step
- the generated README now includes template lineage, update guidance, and agent context

## Implementation Plan

### Phase 1: Template Correctness and Validation

- [x] Remove admin-only leakage from generated output, including broken scripts and
  irrelevant ignore patterns.
- [x] Fix the scratch-directory bootstrap path so the documented install sequence works.
- [x] Make the rendered template pass its first-run validation path: install, build,
  test, and local full-check command.
- [x] Reconcile committed `template/` output with `pnpm compile-template`.
- [x] Add an admin-only rendered-template smoke test in CI.

### Phase 2: Workflow and Documentation Clarity

- [x] Rewrite the root README around workflow selection instead of a single generic
  quick start.
- [x] Document the existing-repo adoption flow as a first-class supported path.
- [x] Expand generated README and development docs so command names, update flow, and
  agent context files are explicit.
- [x] Replace unresolved publishing placeholders with real template variables and make
  licensing guidance consistent across generated files.
- [x] Update the project positioning and tagline to clearly state the template is
  agent-friendly and explain what that means in practice.
- [x] Clarify the retrofit path for flat legacy repos that keep `src/` and `tests/` at
  the root, and validate that migration path in automation.

## Tracking Beads

- `smp-cpve` Epic: Clarify Copier workflows and harden agent-friendly template UX
- `smp-qbk5` Fix broken generated-template commands and bootstrap flow
- `smp-6h0j` Strip admin-only hook and lint config from generated output
- `smp-t15x` Reconcile compiled template output and add rendered-template CI smoke tests
- `smp-93h6` Rewrite README for new, retrofit, scratch, and update Copier workflows
- `smp-y7w4` Refresh generated docs, tagline, and licensing guidance for agent-friendly
  usage
- `smp-ttr1` End-to-end testing of all three user workflows
- `smp-3w9o` Fold standalone review into active spec and remove obsolete review doc
- `smp-d4x5` Clarify retrofit migration for flat legacy TypeScript repos

## Findings Coverage

This spec now replaces the standalone 2026-03-09 review note.
Every verified review finding, plus the retrofit-layout follow-up discovered during
automation, is tracked and resolved here.

- Broken generated `compile-template` script: removed from generated `package.json`;
  tracked by `smp-qbk5`.
- Scratch-directory bootstrap failure before `git init`: fixed with conditional hook
  installation and documented `pnpm prepare`; tracked by `smp-qbk5`.
- `pnpm ci` command collision and missing root command wrappers: replaced with
  deterministic `pnpm check` and added root `dev` / `test:watch` wrappers; tracked by
  `smp-qbk5`.
- Rendered CI workflow formatting failure: normalized generated workflow output and
  covered it in rendered smoke validation; tracked by `smp-t15x`.
- `template/` drift and missing Copier answers file output: compile step now regenerates
  committed template state and restores `.copier-answers.yml`; tracked by `smp-t15x`.
- Missing retrofit workflow docs: root README now covers new repo, scratch, retrofit,
  and update flows; tracked by `smp-93h6`.
- Admin-only leakage in generated config: compile sanitization strips `template/**`,
  `attic/**`, and other admin-only details from generated output; tracked by `smp-6h0j`.
- Weak agent-friendly positioning: README, generated docs, and tagline now explain
  deterministic commands, agent context files, and update behavior; tracked by
  `smp-93h6` and `smp-y7w4`.
- Publishing placeholders and license inconsistency: generated publishing docs now use
  real Copier variables and generated repos ship a consistent MIT default; tracked by
  `smp-y7w4`.
- Missing rendered-template CI smoke test: admin CI now runs a smoke harness over the
  supported workflows; tracked by `smp-t15x`.
- Generated README ownership concern: README generation stays in
  `admin/compile_template.py` for now, but the generated content was expanded and is now
  covered by smoke validation; tracked by `smp-y7w4`.
- Retrofit ambiguity for flat legacy repos: docs now require moving root `src/` and
  `tests/` into `packages/<package>/` or updating workspace config before validation,
  and the smoke test automates that migration path; tracked by `smp-d4x5` and
  `smp-ttr1`.

## Testing Strategy

- Run `pnpm compile-template` and verify the committed `template/` output matches the
  compiler result.
- Run `pnpm check` in the root template-maintainer repo.
- Render the template into a fresh directory with Copier and verify `pnpm install`,
  `pnpm build`, `pnpm test`, `pnpm check`, and post-`git init` hook installation.
- Run `copier update` against the rendered repo and verify upstream template changes
  apply without dropping local non-template files.
- Overlay the template onto a flat legacy repo, migrate root `src/` and `tests/` into
  the generated workspace package, and verify `pnpm install` plus `pnpm check`.
- Keep the admin CI workflow running the smoke harness so these paths stay enforced.

## Rollout Plan

Land this as a tracked template-maintenance change set.

Keep the public docs, compiled template, and validation workflow changes in sync so the
repo does not temporarily advertise unsupported workflows.

## Resolved Decisions

- The local full-check command is `pnpm check`, not `pnpm ci`, to avoid pnpm command
  collisions.
- The template supports `pnpm install` before `git init` by making hook installation
  conditional and exposing `pnpm prepare` for the post-Git step.
- Generated repos default to MIT consistently across package metadata, README guidance,
  and the generated `LICENSE`.
- Existing-repo adoption is supported as an in-place Copier overlay followed by an
  explicit migration of legacy code into workspace packages, or a coordinated workspace
  config update for custom layouts.
- Generated README content remains compile-script-owned for now, but it is treated as
  first-class output and validated by the smoke test.

## References

- [Previous Architecture Spec](/Users/levy/wrk/github/simple-modern-pnpm/admin/docs/project/specs/active/plan-2026-02-15-copier-template-architecture.md)
