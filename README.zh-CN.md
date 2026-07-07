# figma-project-skill-generator

语言：[English](README.md) | 简体中文

这是一个面向团队复用的通用 Figma-to-code 与 UI 合规校验工作流生成器，适用于支持 rules、memory、skills 或类似机制的 AI 编码助手。默认输出格式兼容 Codex。

它会扫描前端项目的技术栈、UI 框架、路由、组件、资源目录和验证命令，然后在项目内生成专属的 Figma 实现与模块规范校验工作流说明。后续做 Figma 设计稿还原或检查模块代码是否符合项目约定时，AI 编码助手就能直接按当前项目规范工作，而不是每次都重复写一大段提示词。

默认 Codex 兼容输出路径：

```text
.codex/skills/figma-to-project/SKILL.md
```

生成出来的项目 Skill 会固定该项目的真实规范，例如 UI 组件库、样式方案、页面放置位置、路由/菜单边界、Figma 资源下载目录、响应式要求、模块校验规则和截图验证方式。

如果使用的不是 Codex，也可以通过 `--output` 输出 Markdown 草稿，再把生成内容迁移到对应工具的 rules、memory、prompt 或 skill 机制中。

## 解决什么问题

做 Figma 设计稿落地时，团队通常会反复提醒 AI 编码助手：

- 先读取项目技术栈
- 使用项目现有 UI 框架
- 复用组件和设计 token
- 把 Figma 资源下载到正确目录
- 正式项目不要先生成独立 HTML
- 页面必须响应式
- 运行项目正确的验证命令
- 用截图检查效果
- 检查已有模块是否符合项目和设计规范

这个公共工作流的作用就是把这些重复提示词沉淀下来：先生成项目专属规范，再用项目专属规范做实际页面开发和模块规范校验。

## 仓库内容

```text
figma-project-skill-generator/
  SKILL.md
  agents/
    openai.yaml
  scripts/
    generate_project_skill.py
```

## 安装

把整个仓库目录复制到你的 AI 编码助手 skills/rules 目录。Codex 默认位置为：

```text
<codex-home>/skills/figma-project-skill-generator
```

常见位置：

```text
Windows: %USERPROFILE%\.codex\skills\figma-project-skill-generator
macOS/Linux: ~/.codex/skills/figma-project-skill-generator
```

然后重启或刷新你的 AI 编码助手。

## 日常使用

这个生成器通常只在两种情况下使用：

- 第一次给某个项目建立 Figma 实现与 UI/模块合规校验规范
- 项目技术栈、路由、UI 框架、组件目录、资源目录或命令发生变化，需要刷新规范

生成出来的项目工作流支持两种模式：

- 实现模式：根据 Figma 节点创建或更新页面/组件
- 校验模式：检查已有模块、页面、组件或 diff 是否符合项目和设计约定

从安装后的 skill 目录运行：

```powershell
cd "<skill-root>"
python ".\scripts\generate_project_skill.py" "<project-root>" --dry-run
```

先检查生成草稿。如果草稿符合项目实际，再创建项目 Skill：

```powershell
cd "<skill-root>"
python ".\scripts\generate_project_skill.py" "<project-root>"
```

刷新已有项目 Skill 时，先检查当前项目规则，再使用：

```powershell
cd "<skill-root>"
python ".\scripts\generate_project_skill.py" "<project-root>" --force
```

## 在 AI 编码助手中使用

可以直接对 AI 编码助手说。Codex 示例：

```text
使用 $figma-project-skill-generator 扫描当前项目，并生成项目专属 Figma 实现与 UI/模块合规校验工作流。
```

项目 Skill 生成后，实际做页面时使用：

```text
使用 $figma-to-project 按项目规范实现这个 Figma 页面：
<Figma URL>
```

也可以用来做规范校验：

```text
使用 $figma-to-project 按项目规范检查这个 UI 模块：
<文件、路由、组件或 diff>
```

推荐理解：

```text
figma-project-skill-generator = 生成/刷新项目规范
figma-to-project = 按项目规范实现 Figma 页面或校验模块代码
```

## 扫描器行为

内置扫描脚本会读取常见前端项目信息：

- `package.json` 和包管理器锁文件
- Vite、Next、Nuxt、Vue、TypeScript、Tailwind、UnoCSS 等配置
- 路由和页面目录
- 公共组件目录
- 资源目录
- 路径别名
- dev、build、typecheck、lint、test 等脚本命令
- 检测到的 dev server 端口
- 常见 UI 库，例如 Naive UI、Element Plus、Ant Design、MUI、Chakra UI、Radix UI

它会生成：

```text
<project-root>/.codex/skills/figma-to-project/SKILL.md
<project-root>/.codex/skills/figma-to-project/agents/openai.yaml
```

生成的项目工作流会包含 Figma 实现流程、模块合规校验流程、UI/UX 质量门禁、项目验证命令，以及实现和审查两种任务的报告格式。

扫描结果是高质量草稿，不是绝对正确的项目规范。成熟项目建议人工再检查：

- 普通页面是否应该进入静态路由
- 菜单/权限是否由后端或动态路由控制
- 是否存在跨仓库 alias
- 是否有必须复用的页面壳组件
- 是否有团队设计 token 或主题变量

## 安全规则

- 已存在的 `SKILL.md` 不会被覆盖，除非显式传入 `--force`
- 已存在的 `agents/openai.yaml` 不会被覆盖，除非显式传入 `--force`
- 默认禁止输出到项目根目录外，除非显式传入 `--allow-outside-output`
- 只有传入 `--update-agents-md` 时才会更新 `AGENTS.md`
- Figma 资源说明使用“当前项目根目录”，不会写死用户本机路径

默认不会覆盖已有项目 Skill。需要刷新时，先 `--dry-run` 看草稿，再确认是否使用 `--force`。

## 常用参数

```text
--dry-run
  只打印生成结果，不写文件。

--force
  覆盖已有生成结果。

--output <path>
  输出到其他 skill 目录，或输出为单个草稿 markdown 文件。

--allow-outside-output
  允许把临时草稿写到项目根目录外。

--update-agents-md
  当 AGENTS.md 存在且缺少提示时，追加一条项目 skill 使用提示。
```

最常用的是：

```text
--dry-run   只预览，不写文件
--force     确认后覆盖已有项目 Skill
```

## 推荐流程

```text
1. 先 dry-run 预览项目扫描结果。
2. 检查识别出的技术栈、UI 框架、路由、组件、资源目录和命令是否正确。
3. 生成项目内 .codex/skills/figma-to-project。
4. 如有必要，人工补充权限路由、菜单边界、主题 token、页面壳组件等项目特有规则。
5. 后续用 $figma-to-project 做实际 Figma 页面开发或 UI/模块合规校验。
```

生成出来的 skill 是强草稿，不是项目知识的替代品。成熟项目在正式使用前，建议重点检查路由归属、权限/菜单边界、跨仓库 alias、页面壳组件和设计 token 规则。

## 运行要求

- Python 3.10+
- 带有 `package.json` 的 JavaScript/TypeScript 前端项目
- AI 编码助手支持 rules、memory、skills 或类似机制；默认兼容 Codex skills
- 可选：实际做 Figma 页面实现时，建议提前配置好 Figma MCP

## 校验

如果使用 Codex，可以用 Codex skill 校验脚本检查：

```powershell
python "<path-to-skill-creator>\scripts\quick_validate.py" "<skill-root>"
```

期望结果：

```text
Skill is valid!
```
