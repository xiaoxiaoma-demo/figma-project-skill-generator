# figma-project-skill-generator

Project-local Figma-to-code skill generator for Codex.

中文说明：这是一个面向团队复用的 Codex 公共 Skill。它会扫描前端项目的技术栈、UI 框架、路由、组件、资源目录和验证命令，然后在项目内生成专属的 `figma-to-project` Skill。后续做 Figma 设计稿还原时，Codex 就能直接按当前项目规范生成代码，而不是每次都重复写一大段提示词。

This skill scans a JavaScript/TypeScript frontend project and generates a project-specific Codex skill at:

```text
.codex/skills/figma-to-project/SKILL.md
```

The generated project skill helps future Codex runs implement Figma designs directly in the target project using that project's real UI framework, route model, components, assets, responsive rules, and verification commands.

生成出来的项目 Skill 会固定该项目的真实规范，例如 UI 组件库、样式方案、页面放置位置、路由/菜单边界、Figma 资源下载目录、响应式要求和截图验证方式。

## What It Solves

## 解决什么问题

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

这个公共 Skill 的作用就是把这些重复提示词沉淀下来：先生成项目专属 Skill，再用项目专属 Skill 做实际页面开发。

## Repository Contents

## 仓库内容

```text
figma-project-skill-generator/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    generate_project_skill.py
```

## Install

## 安装

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

把整个仓库目录放进团队成员自己的 Codex skills 目录后，重启 Codex 或刷新 skills，即可通过 `$figma-project-skill-generator` 触发。

## Daily Usage

## 日常使用

Use this generator once per project, or whenever the project stack/routing/UI conventions change.

这个生成器通常只在两种情况下使用：

- 第一次给某个项目建立 Figma-to-code 规范。
- 项目技术栈、路由、UI 框架、组件目录、资源目录或命令发生变化，需要刷新规范。

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

## 在 Codex 中使用

You can ask Codex:

```text
Use $figma-project-skill-generator to scan the current repository and create a project-specific Figma-to-code skill.
```

After the project skill is generated, use it for implementation:

```text
Use $figma-to-project to implement this Figma page:
<Figma URL>
```

中文提示词示例：

```text
使用 $figma-project-skill-generator 扫描当前项目，并生成项目专属 Figma-to-code skill。
```

项目 Skill 生成后，实际做页面时使用：

```text
使用 $figma-to-project 按项目规范实现这个 Figma 页面：
<Figma URL>
```

推荐理解：

```text
figma-project-skill-generator = 生成/刷新项目规范
figma-to-project = 按项目规范实现 Figma 页面
```

## Scanner Behavior

## 扫描器行为

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

扫描结果是高质量草稿，不是绝对正确的项目规范。成熟项目建议人工再检查：

- 普通页面是否应该进入静态路由。
- 菜单/权限是否由后端或动态路由控制。
- 是否存在跨仓库 alias。
- 是否有必须复用的页面壳组件。
- 是否有团队设计 token 或主题变量。

## Safety Rules

## 安全规则

- Existing `SKILL.md` is not overwritten unless `--force` is passed.
- Existing `agents/openai.yaml` is not overwritten unless `--force` is passed.
- Output outside the project root is blocked unless `--allow-outside-output` is passed.
- `AGENTS.md` is updated only when `--update-agents-md` is passed.
- Figma asset instructions use "current project root" instead of hardcoded user paths.

默认不会覆盖已有项目 Skill。需要刷新时，先 `--dry-run` 看草稿，再确认是否使用 `--force`。

## Useful Flags

## 常用参数

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

最常用的是：

```text
--dry-run   只预览，不写文件
--force     确认后覆盖已有项目 Skill
```

## Recommended Workflow

## 推荐流程

```text
1. Run dry-run.
2. Review detected project conventions.
3. Generate the project-local figma-to-project skill.
4. Manually tighten project-specific route/menu/design-system rules if needed.
5. Use $figma-to-project for actual Figma implementation tasks.
```

The generated skill is a strong draft, not a substitute for project knowledge. For mature projects, review route ownership, permission/menu boundaries, cross-repository aliases, UI shell components, and design token rules before relying on it for production page work.

中文流程：

```text
1. 先 dry-run 预览项目扫描结果。
2. 检查识别出的技术栈、UI 框架、路由、组件、资源目录和命令是否正确。
3. 生成项目内 .codex/skills/figma-to-project。
4. 如有必要，人工补充权限路由、菜单边界、主题 token、页面壳组件等项目特有规则。
5. 后续用 $figma-to-project 做实际 Figma 页面开发。
```

## Requirements

## 运行要求

- Python 3.10+
- A JavaScript/TypeScript frontend project with `package.json`
- Codex skill support
- Optional: Figma MCP configured for future `$figma-to-project` implementation tasks

实际做 Figma 页面实现时，建议提前配置好 Figma MCP，这样 `$figma-to-project` 可以读取 Figma 节点并下载本地资源。

## Validation

## 校验

Validate the skill folder with the Codex skill validation script:

```powershell
python "<path-to-skill-creator>\scripts\quick_validate.py" "<skill-root>"
```

Expected result:

```text
Skill is valid!
```
