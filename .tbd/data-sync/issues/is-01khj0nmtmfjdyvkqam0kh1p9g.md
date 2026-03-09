---
type: is
id: is-01khj0nmtmfjdyvkqam0kh1p9g
title: CI workflow improvements — decide whether admin CI needs a multi-OS matrix or split coverage job; template stays single-OS on Node 24
kind: task
status: open
priority: 3
version: 2
labels: []
dependencies: []
created_at: 2026-02-16T01:22:37.011Z
updated_at: 2026-03-09T17:33:48.344Z
---

## Notes

Node version alignment is already complete: repo and generated workflows now use Node 24, matching .nvmrc and current template guidance. The remaining question is admin-only CI breadth: whether to add a multi-OS matrix and/or split coverage into a separate job. The active template architecture spec intentionally keeps generated-project CI single-OS (ubuntu-latest) for simplicity.
