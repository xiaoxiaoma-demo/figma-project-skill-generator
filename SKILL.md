---
name: figma-project-skill-generator
description: Generate or update a reusable project-local Figma-to-code Codex skill inside the current repository. Use when the user asks to create, scaffold, refresh, or maintain a project-specific skill that captures UI framework, design-system, code-style, routing, asset, responsive, and verification conventions for future Figma implementation tasks.
---

# Figma Project Skill Generator

Create a project-local skill that lets future Codex runs implement Figma designs directly in the current project with the project's own UI framework, code style, assets, routing, responsive rules, and verification commands.

Default output path:

```text
.codex/skills/figma-to-project/SKILL.md
```

## Semi-Automatic Scanner

Use the bundled scanner first when the target project is a JavaScript/TypeScript frontend repository:

```powershell
cd "<skill-root>"
python ".\scripts\generate_project_skill.py" "<project-root>" --dry-run
```

After reviewing the generated draft, create the project skill with:

```powershell
cd "<skill-root>"
python ".\scripts\generate_project_skill.py" "<project-root>"
```

Refresh an existing generated skill only after reviewing the current project rules:

```powershell
cd "<skill-root>"
python ".\scripts\generate_project_skill.py" "<project-root>" --force
```

`<skill-root>` is the installed `figma-project-skill-generator` skill directory. When Codex runs this skill, resolve `scripts/generate_project_skill.py` relative to this `SKILL.md`; do not hardcode user-specific home paths.

Optional flags:

- `--output <path>` writes the generated skill to another file or skill directory.
- `--update-agents-md` appends the short Figma skill pointer to `AGENTS.md` when that file exists and the pointer is missing.
- `--allow-outside-output` permits writing a temporary draft outside the project root; omit it for normal project skill creation.

The script scans `package.json`, lockfiles, Vite/Next/Nuxt/Vue config, TypeScript paths, style config, route/page files, shared components, asset folders, and project commands. Treat its output as a high-signal draft: keep concrete detected facts, then manually tighten route ownership, permission/menu rules, cross-repository aliases, and project-specific UI conventions that require human judgment.

## Workflow

1. Confirm the current working directory is the target project root.
2. Run the semi-automatic scanner with `--dry-run` when applicable, and use the output as the first project-convention draft.
3. Read project guidance first:
   - `AGENTS.md` files, nearest first
   - `package.json`, lockfiles, workspace files
   - framework config files such as `vite.config.*`, `next.config.*`, `vue.config.*`, `nuxt.config.*`
   - TypeScript config, lint config, formatter config
   - style config such as Tailwind, UnoCSS, Sass, CSS Modules, PostCSS, theme files
   - route/page directories
   - shared UI component directories
   - asset directories
   - existing login/form/page implementations when relevant
   - local `$ui-ux-pro-max` skill when available, using it as the UI/UX quality reference
4. Summarize the project's conventions before writing:
   - framework and language
   - UI library and component primitives
   - styling approach and token source
   - routing/page registration
   - page discovery or menu generation mechanisms, including file-scanning plugins
   - path aliases and cross-repository aliases that may affect UI implementation
   - asset import/path convention
   - naming and file placement
   - dev server, build, test, lint, and screenshot commands
5. Extract the UI/UX quality rules to embed:
   - accessibility: contrast, focus states, alt text, keyboard navigation, labels
   - touch and interaction: 44px+ targets, press feedback, no hover-only behavior
   - performance: reserved image dimensions, no layout shift, no expensive reflow loops
   - responsive layout: mobile-first breakpoints, no horizontal scroll, viewport-safe sizing
   - typography and color: semantic tokens, readable text, no arbitrary ad-hoc palette
   - forms: labels, autocomplete/input modes, error placement, submit feedback
   - verification: desktop, tablet, mobile, and reduced-motion checks when feasible
6. Generate or update `.codex/skills/figma-to-project/SKILL.md`.
   Also create or update `.codex/skills/figma-to-project/agents/openai.yaml` when the environment supports skill UI metadata. Keep `display_name`, `short_description`, and `default_prompt` aligned with the generated skill name and project purpose.
7. If the project has an `AGENTS.md`, add a short pointer only when missing:

```md
For Figma design implementation, use the project skill `figma-to-project` and follow project UI framework, component, styling, asset, responsive, and verification conventions.
```

Do not overwrite unrelated project instructions.

## Generated Skill Requirements

The generated `figma-to-project` skill must be project-specific. It must include:

- exact project stack and UI framework
- directories to inspect before coding
- components/tokens/helpers to prefer
- where to put pages, components, styles, and assets
- how to call Figma MCP with concrete tool names when available
- how to translate Figma values into project-native code
- page discovery/menu generation rules
- route ownership and permission/menu registration boundaries
- path aliases and cross-repository lookup rules
- Figma asset download root safety rules
- responsive rules for desktop/tablet/mobile
- UI/UX quality gates adapted from `$ui-ux-pro-max`
- commands to run for dev server, lint/build/tests
- browser screenshot verification expectations
- concrete dev server URL/port when the project defines one
- rules for avoiding standalone HTML unless explicitly requested

Keep the generated skill concise. Include only stable project conventions and reusable workflow rules. Do not include one-off task details, temporary file paths, or specific Figma URLs.

## Figma Implementation Policy To Embed

The generated project skill must instruct future runs to:

- use Figma MCP on the exact selected node/frame before coding
- parse Figma URLs into `fileKey` and `nodeId`; for GLips/Framelink, call `mcp__Framelink_Figma_MCP.get_figma_data` when available
- download required Figma assets into the project asset directory
- for GLips/Framelink image assets, call `mcp__Framelink_Figma_MCP.download_figma_images` when available
- if Figma MCP tools are not exposed in the current session, stop and ask the user to enable/restart MCP or provide Figma JSON/screenshots/exported assets; do not silently switch to an unspecified fallback
- before downloading assets, confirm the MCP image root or current working directory is the target project root; otherwise download to a known temporary directory and move/verify files into the project asset directory
- treat Figma output as design context, not final code style
- reuse project components and tokens before creating new ones
- implement directly in the project rather than generating standalone HTML
- avoid fixed full-canvas scaling such as `scale(1920px design)`
- use project responsive primitives, `flex`/`grid`, `max-width`, `clamp`, percentages, and breakpoints
- make desktop high-fidelity to Figma
- allow mobile/tablet reflow while preserving hierarchy and brand intent
- avoid blank browser areas, horizontal scroll, text overlap, and clipped controls
- start the app and verify with desktop and mobile screenshots

## UI/UX Pro Max Integration

When `$ui-ux-pro-max` is installed, use it as the generic UI/UX rule source and keep this skill focused on project-specific generation.

Embed a concise quality gate in the generated project skill:

- Use project tokens and components first; use `$ui-ux-pro-max` only to guide UX decisions.
- Check accessibility before visual polish: contrast, focus, labels, alt text, keyboard order.
- Check interaction quality: 44px+ touch targets, pointer/press states, no hover-only actions.
- Check responsive quality: 375px, 768px, 1024px, 1440px where practical.
- Check layout safety: no blank viewport bands, no horizontal scroll, no clipped controls, no text overlap.
- Check motion safety: 150-300ms purposeful transitions and `prefers-reduced-motion`.
- Check form quality: semantic inputs, autocomplete, clear validation and recovery path.

Do not copy the full `$ui-ux-pro-max` contents into the generated project skill. Reference it by name and include only the small project-relevant checklist.

## Generated Skill Template

Use this structure for `.codex/skills/figma-to-project/SKILL.md`:

```md
---
name: figma-to-project
description: Implement Figma designs directly in this project using its UI framework, component library, styling tokens, code conventions, responsive rules, and verification workflow. Use when the user provides a Figma link/node and asks to build, restore, convert, or update a page/component from the design.
---

# Figma To Project

## Project Conventions

- Framework:
- Language:
- UI library:
- Styling:
- Token/theme source:
- Routes/pages:
- Page discovery:
- Route/menu boundaries:
- Path aliases:
- Components:
- Assets:
- Commands:

## Required Workflow

1. Read project guidance and relevant existing code.
2. Parse the Figma URL into `fileKey` and `nodeId`; use Figma MCP to read the exact node/frame from the provided link.
3. Extract layout, colors, typography, spacing, radii, shadows, images, icons, and component hierarchy.
4. Confirm Figma MCP asset downloads will land inside the target project; download assets into the project asset directory and verify the files exist there.
5. Implement directly in the project using existing components and tokens.
6. Apply responsive behavior with project-native patterns.
7. Run the dev server/build/lint/test commands that fit the change.
8. Capture desktop and mobile screenshots, compare against Figma, and iterate.

## Implementation Rules

- Do not create standalone HTML unless explicitly requested.
- Do not introduce new UI libraries unless explicitly approved.
- Do not create a parallel design system.
- Prefer existing components/tokens/helpers.
- Keep changes scoped and reversible.
- Desktop should closely match Figma.
- Mobile/tablet may reflow but must preserve hierarchy.
- No horizontal scroll, clipped controls, blank viewport bands, or text overlap.
- Apply `$ui-ux-pro-max` quality gates for accessibility, touch targets, responsive layout, form UX, motion, and visual consistency when UI is changed.
- Prefer project-native responsive utilities over raw viewport hacks.

## Verification

- Dev server:
- Dev URL:
- Route to inspect:
- Desktop viewport:
- Mobile viewport:
- Required checks:
  - Figma visual comparison
  - no horizontal scroll or viewport blank bands
  - keyboard focus is visible
  - form inputs have semantic labels/autocomplete where applicable
  - responsive screenshots at project-relevant breakpoints
```

Fill every placeholder from the actual project. Remove lines that do not apply.

## Validation

After writing the project skill:

1. Re-read the generated `SKILL.md`.
2. Check that it names concrete project paths, aliases, commands, dev URL/port, Figma MCP tools, and asset directories.
3. Check that `agents/openai.yaml`, when present, mentions `$figma-to-project` correctly in `default_prompt`.
4. Check that it does not mention temporary examples or unrelated projects.
5. Report the generated file path and a brief summary of captured project rules.
