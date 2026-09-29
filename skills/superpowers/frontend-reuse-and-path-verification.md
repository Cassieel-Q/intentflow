# Frontend Reuse and Path Verification

## Purpose

Keep frontend changes consistent with the existing project while verifying the
user-visible path instead of checking only source code.

## Before implementation

- Confirm the framework, build commands, and existing component patterns.
- Find reusable components, styles, state helpers, and request wrappers.
- Map the main path plus loading, empty, error, disabled, and success states.
- Confirm the target viewport and any design or accessibility constraints.

Reuse should preserve established behavior unless a requirement explicitly
changes it. Keep new visual rules local and avoid broad global selectors.

## Verification

Use the least expensive checks that still provide convincing evidence:

1. Existing tests and build scripts.
2. A focused browser or device path.
3. Targeted end-to-end checks for important interactions.
4. Screenshots for visual states that are easy to misunderstand.

At minimum, verify that the page opens, key controls work, important states
render, text fits its container, and related content does not overlap.

## Cost control

- Do not run a full end-to-end suite for an isolated copy or styling change.
- Do not capture every page when a few changed states are sufficient.
- Prefer focused paths and record what was not checked.
