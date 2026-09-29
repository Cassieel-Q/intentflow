---
name: figma-to-real-feature
description: "Turn a specified Figma frame/node into real frontend or full-stack functionality by classifying new-build vs retrofit scope, mapping to existing project components and API truth, asking evidence-backed product questions, implementing through the repo workflow, and verifying in a browser. Use when the user provides or references Figma designs that must land in an existing codebase."
---

# Figma To Real Feature

关键词：Figma 设计稿 落地 真实功能 前端 后端 接口 旧页面改造 新功能 grill-me Playwright 验证.

## Purpose

This skill is a baseline workflow for taking Figma into production-shaped code. Figma is a design input, not the only source of truth. The final implementation must obey the current repository's components, routes, API contracts, permissions, state model, and verification standards.

Use this skill when:

- A Figma frame/node needs to become a working page, form, dialog, workflow, or full-stack feature.
- A Figma design contains both new functionality and changes to existing pages.
- The user wants Codex to ask targeted questions first, but continue independently when the user says they do not know.

Do not use this skill for:

- Pure design critique with no code target.
- Pixel-only experiments that do not need repository integration.
- Backend-only work with no Figma/UI source.

## Operating Contract

- Persist stable conclusions, assumptions, decisions, source mappings, and verification notes into the project docs or task notes.
- Ask the user before spending high token budget on broad discovery. Offer concrete options when possible.
- If the user says "不知道", "你自己判断", or explicitly asks Codex to continue, inspect Figma/code/environment and choose a default based on evidence.
- Ask only questions that change user-visible behavior, business boundaries, or acceptance criteria.
- Do not ask about implementation details that repository conventions can decide.
- If using a project workflow such as Comet, enter through its public entrypoint and let it route design, build, verify, and review phases.
- For frontend work, before writing new UI code, produce a component reuse/new-design report and wait for user approval when the work introduces new reusable components, changes shared components, or substantially reinterprets the Figma design.

## Recommended Skill Stack

- `figma-to-real-feature`: Orchestrates the Figma-to-function intake, classification, and truth-source mapping.
- `figma-skill` or Figma MCP: Reads the specified frame/node, metadata, design context, screenshots, variables, and assets.
- `frontend-design`: Maps Figma intent to existing UI components, tokens, layout patterns, responsive behavior, accessibility, and state coverage.
- `grill-me` / `grilling`: Resolves one evidence-backed product decision at a time when Figma and code cannot decide.
- `comet`: Persists plan/build/verify state and coordinates repository changes.
- `webapp-testing`: Verifies real browser behavior with Playwright, screenshots, console, network, and responsive checks.
- `requesting-code-review`: Reviews high-risk frontend diffs, shared-layer changes, and explicit review requests.

## Workflow

### 1. Intake

Collect the smallest useful input:

- Figma file/frame/node URL or ID.
- Target repository and client, if known.
- Whether the design is new, retrofit, or mixed.
- Optional reference route/page/component.
- Optional API or backend source.
- Optional test account, route, and sample data.

If any item is unknown, ask with options. If the user cannot answer, proceed by inspecting the repo and record the assumption.

### 2. Figma Extraction

Read only the specified Figma frame/node unless the user authorizes broader discovery.

Extract:

- User-visible text and hierarchy.
- Layout regions, table/list/form/dialog structure, navigation, and actions.
- Component candidates and repeated patterns.
- Visual tokens: color, typography, spacing, borders, shadows, icons, assets.
- Interaction states visible or implied by the design.
- Responsive variants if present.

Avoid full-file Figma traversal by default.

### 3. Scope Classification

Classify each screen or module before planning implementation:

| Type | Meaning | Default strategy |
| --- | --- | --- |
| `new-build` | No existing page owns this behavior | Create route/page using existing components and API truth |
| `retrofit` | Existing page/workflow is being changed | Build a Figma-vs-current diff and preserve old required behavior |
| `mixed` | New parts attach to existing workflow | Split into small work units with explicit integration points |

For `retrofit`, identify:

- Existing route and source files.
- Current user flow.
- Behaviors that must be preserved.
- Behaviors explicitly replaced by Figma.
- Compatibility risks: permissions, fields, query params, cache, navigation, exports, printing, uploads, mobile/native bridge.

### 4. Project Truth Mapping

Before coding, map the design to repository truth:

- Frontend stack, routes, UI library, component patterns, style tokens, stores, API wrappers.
- Existing similar pages and reusable components.
- Backend Controller/API paths, DTO/VO/types, enums, permissions, status transitions.
- Data ownership: which fields are persisted, derived, optional, or display-only.
- Cross-client impact: PC, mobile, app, H5, admin, agent, or legacy clients.

If a field or behavior cannot be verified, stop for one `grill-me` question or record an evidence-based default when authorized.

### 4.5 Frontend Component Approval Gate

Before writing new frontend UI code, create a short report:

- Which pages/routes will be changed or created.
- Which existing components will be reused.
- Which existing components will be extended or behaviorally changed.
- Which new components are proposed and why existing components are not enough.
- Which design tokens/styles will be reused, and which new visual rules are proposed.
- Risks to consistency, maintainability, responsive behavior, and old-page compatibility.

Approval rule:

- MUST wait for user approval before creating new reusable components, changing shared components, or introducing new visual patterns.
- MAY proceed without approval for page-local glue code, simple composition of existing components, or one-off local markup that does not establish a reusable pattern.
- If the user previously authorized autonomous decisions for the current task, record the report and proceed using the recommended option.

### 5. Grill-Me Decision Rules

Use `grill-me` only for real product decisions.

Good questions:

- Is this Figma module a new page or an existing page replacement?
- When Figma conflicts with current behavior, should the old behavior remain?
- After submit, should the user stay, refresh, return, or navigate to detail?
- Should a missing backend field be added now, deferred, or represented as read-only?
- Which user roles should see this action?

Bad questions:

- Which filename should be used?
- Should I reuse the obvious local component?
- Should the button be named like the design when the project already has a convention?
- Should I run normal tests?

Each question must include:

- The visible difference between options.
- Recommended option.
- Evidence from Figma or code.
- The plan or acceptance change caused by each option.

### 6. Implementation Planning

Create an implementation plan that separates:

- New pages/components.
- Existing page diffs.
- Shared components or API wrappers.
- Backend changes, if any.
- State coverage: loading, empty, error, disabled, success, permission denied, validation, long text, responsive.
- Verification scenarios and required test data.

Prefer small vertical slices over one huge Figma-to-code pass.

### 7. Build

Implementation rules:

- Reuse existing components, style tokens, API wrappers, stores, route guards, and form validation patterns first.
- Do not introduce new UI libraries, CSS-in-JS runtimes, or broad design systems unless the user explicitly requests it.
- Keep old behavior intact for retrofit work unless Figma or user decisions explicitly replace it.
- Use backend truth for field names, enums, permissions, and status transitions.
- Add minimal comments only for non-obvious business constraints.

### 8. Verification

Visible UI changes need browser evidence unless the environment is genuinely unavailable.

Verify:

- Main happy path.
- Loading, empty, error, disabled, validation, permission, and success states that are in scope.
- Responsive layout for relevant viewports.
- Keyboard/focus/accessibility basics for forms, dialogs, and buttons.
- Console errors and failed network requests.
- Retrofit regressions for old behavior that must remain.

For high-value visual pages, optionally add screenshot comparison. Pixel-perfect tuning is not default because it is token-expensive.

## Token Budget Guidance

High-token zones:

- Finding existing analogous pages and component conventions.
- Tracing API fields, enums, permissions, and backend status flow.
- Understanding legacy behavior for retrofit work.
- Browser verification that requires login, test data, and repeated screenshots.
- Pixel-level visual tuning.

Low-value manual work:

- Hand-copying every Figma style value.
- Writing broad boilerplate code for Codex to patch later.
- Asking Codex to scan an entire Figma file or whole repository without target frames/routes.

Best user inputs for saving token:

- Exact Figma frame/node.
- Reference route or page path.
- Known API/backend entry.
- Main flow and acceptance result.
- Test account, route, and sample data.

## Output Artifacts

Produce or update:

- A short Figma-to-feature intake summary.
- A new-build/retrofit/mixed classification table.
- A Figma-to-current-code diff for retrofit work.
- API and field truth-source notes.
- A compact implementation plan.
- Verification evidence or documented skip reason.
- Project docs summarizing durable decisions.
