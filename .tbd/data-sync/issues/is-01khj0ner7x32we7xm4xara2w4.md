---
type: is
id: is-01khj0ner7x32we7xm4xara2w4
title: Vitest coverage outputs — decide whether admin repo should add lcov/html reporters and explicit reportsDirectory; template stays minimal
kind: task
status: open
priority: 3
version: 2
labels: []
dependencies: []
created_at: 2026-02-16T01:22:30.790Z
updated_at: 2026-03-09T17:33:48.341Z
---

## Notes

The current template intentionally keeps Vitest coverage reporters minimal: text, json, and json-summary. The active template architecture spec explicitly recommends keeping richer outputs such as lcov/html and explicit reportsDirectory out of generated repos unless we decide the admin repo separately benefits from them.
