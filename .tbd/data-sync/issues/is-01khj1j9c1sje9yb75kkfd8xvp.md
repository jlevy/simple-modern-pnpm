---
type: is
id: is-01khj1j9c1sje9yb75kkfd8xvp
title: Sync current template decisions back into pnpm-monorepo-patterns guideline
kind: task
status: closed
priority: 3
version: 3
labels: []
dependencies: []
created_at: 2026-02-16T01:38:15.552Z
updated_at: 2026-03-09T17:44:07.016Z
closed_at: 2026-03-09T17:44:07.015Z
close_reason: "Synced pnpm-monorepo-patterns with current template defaults: tag-triggered releases, pnpm check, conditional prepare, single-job CI, and minimal Vitest coverage outputs."
---
## Notes

Part of this work was already pushed upstream in commit c9c9d62 (Node 24 alignment, Actions v6, Lefthook v2, ESM-only guidance, OIDC tag-triggered publishing, flowmark). Remaining gap: the internal pnpm-monorepo-patterns guideline still leans toward Changesets-first and broader CI examples, and does not yet reflect the latest template decisions around pnpm check, conditional pnpm prepare after git init, intentionally single-OS template CI, and intentionally minimal Vitest coverage outputs.
