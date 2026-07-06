# figma-project-skill-generator

Project-local Figma-to-code skill generator for Codex.

This skill scans a JavaScript/TypeScript frontend project and generates a project-specific Codex skill at:

```text
.codex/skills/figma-to-project/SKILL.md
```

The generated project skill helps future Codex runs implement Figma designs directly in the target project using that project's real UI framework, route model, components, assets, responsive rules, and verification commands.

## What It Solves

When implementing Figma designs, teams usually repeat the same prompt instructions:

- read the project stack first
- use the existing UI framework
- reuse components and design tokens
- download Figma assets into the right folder
- avoid standalone HTML for production code
- keep layouts responsive
- run the right project commands
- verify with screenshots

This skill turns those repeated instructions into a reusable project-local skill.

## Repository Contents

```text
figma-project-skill-generator/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    generate_project_skill.py
```

## Install

Copy this folder into your Codex skills directory:

```text
<codex-home>/skills/figma-project-skill-generator
```

Common locations:

```text
Windows: %USERPROFILE%\.codex\skills\figma-project-skill-generator
macOS/Linux: ~/.codex/skills/figma-project-skill-generator
```

Then restart Codex or reload skills if your environment requires it.

## Daily Usage

Use this generator once per project, or whenever the project stack/routing/UI conventions change.

From the installed skill directory:

```powershell
cd "<skill-root>"
python ".\scripts\generate_project_skill.py" "<project-root>" --dry-run
```

Review the generated draft. If it looks correct, create the project skill:

```powershell
cd "<skill-root>"
python ".\scripts\generate_project_skill.py" "<project-root>"
```

Refresh an existing generated project skill only after reviewing the current rules:

```powershell
cd "<skill-root>"
python ".\scripts\generate_project_skill.py" "<project-root>" --force
```

## Using It Inside Codex

You can ask Codex:

```text
Use $figma-project-skill-generator to scan the current repository and create a project-specific Figma-to-code skill.
```

After the project skill is generated, use it for implementation:

```text
Use $figma-to-project to implement this Figma page:
<Figma URL>
```

## Scanner Behavior

The bundled scanner reads common frontend project signals:

- `package.json` and package manager lockfiles
- Vite, Next, Nuxt, Vue, TypeScript, Tailwind, UnoCSS, and related config files
- route and page directories
- shared component directories
- asset directories
- path aliases
- scripts for dev/build/typecheck/lint/test
- detected dev server port
- common UI libraries such as Naive UI, Element Plus, Ant Design, MUI, Chakra UI, Radix UI

It generates:

```text
<project-root>/.codex/skills/figma-to-project/SKILL.md
<project-root>/.codex/skills/figma-to-project/agents/openai.yaml
```

## Safety Rules

- Existing `SKILL.md` is not overwritten unless `--force` is passed.
- Existing `agents/openai.yaml` is not overwritten unless `--force` is passed.
- Output outside the project root is blocked unless `--allow-outside-output` is passed.
- `AGENTS.md` is updated only when `--update-agents-md` is passed.
- Figma asset instructions use "current project root" instead of hardcoded user paths.

## Useful Flags

```text
--dry-run
  Print the generated skill without writing files.

--force
  Overwrite an existing generated skill.

--output <path>
  Write to another skill directory or a single draft markdown file.

--allow-outside-output
  Allow writing a temporary draft outside the project root.

--update-agents-md
  Append a short pointer to AGENTS.md when present and missing.
```

## Recommended Workflow

```text
1. Run dry-run.
2. Review detected project conventions.
3. Generate the project-local figma-to-project skill.
4. Manually tighten project-specific route/menu/design-system rules if needed.
5. Use $figma-to-project for actual Figma implementation tasks.
```

The generated skill is a strong draft, not a substitute for project knowledge. For mature projects, review route ownership, permission/menu boundaries, cross-repository aliases, UI shell components, and design token rules before relying on it for production page work.

## Requirements

- Python 3.10+
- A JavaScript/TypeScript frontend project with `package.json`
- Codex skill support
- Optional: Figma MCP configured for future `$figma-to-project` implementation tasks

## Validation

Validate the skill folder with the Codex skill validation script:

```powershell
python "<path-to-skill-creator>\scripts\quick_validate.py" "<skill-root>"
```

Expected result:

```text
Skill is valid!
```
