#!/usr/bin/env python3
"""Generate a project-local Figma-to-code skill/workflow from repository signals."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SKILL_DIR = Path(".codex") / "skills" / "figma-to-project"
SKILL_FILE = SKILL_DIR / "SKILL.md"
OPENAI_YAML = SKILL_DIR / "agents" / "openai.yaml"


@dataclass
class Scan:
    root: Path
    project_name: str
    package_manager: str
    scripts: dict[str, str]
    framework: str
    language: str
    ui_library: str
    styling: str
    tokens: str
    route_paths: list[str]
    page_discovery: str
    route_boundaries: str
    aliases: str
    components: str
    assets: str
    commands: str
    static_commands: str
    dev_server: str
    dev_url: str
    auto_imports: str
    icons: str
    theme_entry: str
    references: list[str]


def read_text(path: Path, limit: int = 300_000) -> str:
    if not path.exists() or not path.is_file():
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="ignore")[:limit]
    except OSError:
        return ""


def load_json(path: Path) -> dict:
    text = read_text(path)
    if not text:
        return {}
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {}


def exists_any(root: Path, patterns: Iterable[str]) -> list[Path]:
    found: list[Path] = []
    for pattern in patterns:
        found.extend(sorted(root.glob(pattern)))
    return [p for p in found if p.exists()]


def rel(root: Path, path: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def first_existing(root: Path, candidates: Iterable[str]) -> str:
    for candidate in candidates:
        if (root / candidate).exists():
            return candidate
    return ""


def detect_package_manager(root: Path) -> str:
    if (root / "pnpm-lock.yaml").exists():
        return "pnpm"
    if (root / "yarn.lock").exists():
        return "yarn"
    if (root / "bun.lockb").exists() or (root / "bun.lock").exists():
        return "bun"
    if (root / "package-lock.json").exists():
        return "npm"
    return "npm"


def detect_framework(package: dict, config_names: set[str]) -> str:
    deps = all_deps(package)
    if "next" in deps:
        return "Next.js"
    if "nuxt" in deps or any(name.startswith("nuxt.config.") for name in config_names):
        return "Nuxt"
    if "vue" in deps:
        if "vite" in deps:
            return "Vue 3 + Vite" if str(deps.get("vue", "")).startswith("^3") or str(deps.get("vue", "")).startswith("3") else "Vue + Vite"
        return "Vue"
    if "react" in deps:
        return "React + Vite" if "vite" in deps else "React"
    if "svelte" in deps:
        return "Svelte"
    if "vite" in deps:
        return "Vite"
    return "Unknown frontend framework"


def all_deps(package: dict) -> dict[str, str]:
    deps: dict[str, str] = {}
    for key in ("dependencies", "devDependencies", "peerDependencies"):
        value = package.get(key)
        if isinstance(value, dict):
            deps.update(value)
    return deps


def detect_language(root: Path, package: dict) -> str:
    has_ts = bool(exists_any(root, ["tsconfig*.json", "src/**/*.ts", "src/**/*.tsx"]))
    has_vue = bool(exists_any(root, ["src/**/*.vue"]))
    if has_ts and has_vue:
        return "TypeScript with Vue SFCs"
    if has_ts:
        return "TypeScript"
    return "JavaScript"


def detect_ui_library(package: dict, config_text: str) -> str:
    deps = all_deps(package)
    libraries = []
    mapping = [
        ("naive-ui", "Naive UI"),
        ("element-plus", "Element Plus"),
        ("ant-design-vue", "Ant Design Vue"),
        ("antd", "Ant Design"),
        ("@mui/material", "MUI"),
        ("@chakra-ui/react", "Chakra UI"),
        ("@radix-ui/react-dialog", "Radix UI"),
        ("shadcn", "shadcn/ui"),
    ]
    for dep, label in mapping:
        if dep in deps:
            libraries.append(label)
    if "NaiveUiResolver" in config_text:
        if "Naive UI" not in libraries:
            libraries.append("Naive UI")
        return ", ".join(libraries) + ", auto-registered through `NaiveUiResolver` when matching existing files"
    return ", ".join(libraries) if libraries else "Project-native components / no detected UI library"


def detect_auto_imports(config_text: str) -> str:
    match = re.search(r"AutoImport\(\s*\{(?P<body>.*?)\}\s*\)", config_text, re.DOTALL)
    if not match:
        return "No auto-import config detected; follow nearby import style."
    body = match.group("body")
    imports = re.search(r"imports\s*:\s*\[(?P<items>[^\]]+)\]", body, re.DOTALL)
    if imports:
        names = [item.strip().strip("'\"") for item in imports.group("items").split(",") if item.strip()]
        return "Auto imports configured for " + ", ".join(f"`{name}`" for name in names) + "; match nearby files when deciding explicit imports."
    return "AutoImport plugin is configured; inspect framework config and nearby files before adding imports."


def detect_styling(root: Path, package: dict, config_text: str) -> str:
    deps = all_deps(package)
    parts = []
    if "unocss" in deps or first_existing(root, ["uno.config.ts", "uno.config.js", "uno.config.mjs"]):
        parts.append("UnoCSS")
        if "presetAttributify" in config_text:
            parts.append("Attributify preset")
        if "presetIcons" in config_text:
            parts.append("Icon preset")
        if "presetRemToPx" in config_text:
            parts.append("rem-to-px preset")
    if "tailwindcss" in deps or first_existing(root, ["tailwind.config.ts", "tailwind.config.js", "tailwind.config.cjs"]):
        parts.append("Tailwind CSS")
    if "sass" in deps or "less" in deps:
        parts.append("Sass/Less")
    if exists_any(root, ["src/**/*.module.css", "src/**/*.module.scss"]):
        parts.append("CSS Modules")
    return ", ".join(dict.fromkeys(parts)) if parts else "Project stylesheets and component-scoped styles"


def detect_icons(root: Path, config_text: str) -> str:
    hints = []
    if "presetIcons" in config_text:
        hints.append("UnoCSS icon classes")
    if (root / "src" / "assets" / "icons" / "feather").exists():
        hints.append("`i-fe:*` from `src/assets/icons/feather`")
    if (root / "src" / "assets" / "icons" / "app").exists():
        hints.append("`i-app:*` from `src/assets/icons/app`")
    if "pluginIcons" in config_text:
        hints.append("custom `pluginIcons()` safelist")
    return ", ".join(dict.fromkeys(hints)) if hints else "Use the project's existing icon family and avoid emoji as structural icons."


def detect_theme_entry(root: Path, config_text: str) -> str:
    candidates = []
    for candidate in ("src/App.vue", "src/theme/index.ts", "src/styles/variables.css", "src/styles/variables.scss"):
        if (root / candidate).exists():
            text = read_text(root / candidate, 80_000)
            if any(token in text for token in ("--primary-color", "NConfigProvider", "theme", "auto-bg", "card-border")):
                candidates.append(candidate)
    if candidates:
        return "Inspect " + ", ".join(f"`{path}`" for path in candidates[:4]) + " before adding theme-specific styles."
    return "Inspect existing app/theme entry files before adding raw theme values."


def scan_config_text(root: Path) -> tuple[set[str], str]:
    files = exists_any(
        root,
        [
            "vite.config.*",
            "next.config.*",
            "vue.config.*",
            "nuxt.config.*",
            "uno.config.*",
            "tailwind.config.*",
            "postcss.config.*",
            "tsconfig*.json",
        ],
    )
    return {p.name for p in files}, "\n".join(read_text(p, 80_000) for p in files)


def detect_tokens(root: Path, config_text: str) -> str:
    token_hints = []
    for pattern in ("--primary-color", "bg-primary", "text-primary", "color-primary", "auto-bg", "card-border"):
        if pattern in config_text or rg_like(root, pattern):
            token_hints.append(f"`{pattern}`")
    if token_hints:
        return "Prefer existing theme shortcuts/tokens such as " + ", ".join(dict.fromkeys(token_hints)) + "."
    theme_files = [rel(root, p) for p in exists_any(root, ["src/**/theme.*", "src/**/tokens.*", "src/**/variables.*", "src/**/var.*"])]
    if theme_files:
        return "Inspect theme/token files: " + ", ".join(theme_files[:8]) + "."
    return "Use project theme variables and existing component styles before adding raw colors."


def rg_like(root: Path, needle: str, max_files: int = 300) -> bool:
    count = 0
    for path in root.glob("src/**/*"):
        if not path.is_file() or path.suffix.lower() not in {".vue", ".ts", ".tsx", ".js", ".jsx", ".css", ".scss", ".less"}:
            continue
        count += 1
        if count > max_files:
            return False
        if needle in read_text(path, 40_000):
            return True
    return False


def detect_routes(root: Path, config_text: str) -> tuple[list[str], str, str]:
    route_files = [
        rel(root, p)
        for p in exists_any(
            root,
            [
                "src/router/**/*.ts",
                "src/router/**/*.js",
                "src/routes/**/*",
                "src/app/**/*",
                "src/pages/**/*",
                "app/**/*",
                "pages/**/*",
            ],
        )
    ]
    route_files = [p for p in route_files if not p.endswith(".d.ts")][:12]

    discovery = []
    build_index = read_text(root / "build" / "index.ts")
    if "pluginPagePathes" in config_text:
        discovery.append("`pluginPagePathes()` is configured in `vite.config.ts`.")
    if "getPagePathes" in build_index and "src/views/**/*.vue" in build_index:
        discovery.append("`build/index.ts#getPagePathes()` scans `src/views/**/*.vue` for page-path selection.")
    if (root / "src" / "views").exists():
        discovery.append("Page-level files commonly live under `src/views`.")
    if not discovery and (root / "src" / "pages").exists():
        discovery.append("Page-level files commonly live under `src/pages`.")
    if not discovery and (root / "app").exists():
        discovery.append("App Router files live under `app`.")

    guard_text = "\n".join(read_text(p, 80_000) for p in exists_any(root, ["src/router/guards/**/*.ts", "src/router/**/*.ts"]))
    if "permission" in guard_text.lower() or "menu" in guard_text.lower():
        boundaries = "Respect the permission/menu route model; do not bypass dynamic routes by adding normal admin pages to static seed routes unless they are truly global."
    elif any("basic-routes" in p for p in route_files):
        boundaries = "Treat static route files as global entry/error/login routes unless nearby code shows ordinary pages belong there."
    else:
        boundaries = "Follow the existing route ownership pattern and avoid changing global routing when a feature-level page is enough."

    return route_files, " ".join(discovery) if discovery else "Inspect existing route/page files before adding navigation.", boundaries


def detect_aliases(root: Path, config_text: str) -> str:
    aliases: list[str] = []
    config_alias_keys: list[str] = []
    for match in re.finditer(r"['\"]([^'\"]+)['\"]\s*:\s*path\.resolve\(process\.cwd\(\),\s*['\"]([^'\"]+)['\"]\)", config_text):
        key = match.group(1)
        config_alias_keys.append(key)
        aliases.append(f"`{key}` -> `{match.group(2)}`")
    for match in re.finditer(r"(?m)^\s*([A-Za-z0-9_~@-]+)\s*:\s*path\.resolve\(process\.cwd\(\),\s*['\"]([^'\"]+)['\"]\)", config_text):
        key = match.group(1)
        if key not in config_alias_keys:
            config_alias_keys.append(key)
            aliases.append(f"`{key}` -> `{match.group(2)}`")
    tsconfig = load_json(root / "tsconfig.json")
    paths = (((tsconfig.get("compilerOptions") or {}).get("paths")) or {})
    ts_alias_keys: set[str] = set()
    if isinstance(paths, dict):
        for key, value in paths.items():
            target = value[0] if isinstance(value, list) and value else value
            ts_alias_keys.add(str(key).replace("/*", ""))
            aliases.append(f"`{key}` -> `{target}` in tsconfig")
    for key in config_alias_keys:
        if key not in ts_alias_keys and key not in {"@"}:
            aliases.append(f"`{key}` is configured in the bundler; confirm TypeScript path support before using it in typed business code")
    return ", ".join(dict.fromkeys(aliases)) if aliases else "Inspect framework config and tsconfig paths before importing."


def detect_components(root: Path) -> str:
    candidates = [
        "src/components/common",
        "src/components/ui",
        "src/components",
        "components",
    ]
    parts = []
    for candidate in candidates:
        path = root / candidate
        if path.exists() and path.is_dir():
            names = [p.stem for p in sorted(path.glob("*.vue"))[:8]]
            suffix = f" ({', '.join(names)})" if names else ""
            parts.append(f"`{candidate}`{suffix}")
            if {"AppPage", "CommonPage", "AppCard"}.intersection(names):
                parts.append("prefer existing page shells such as `AppPage`, `CommonPage`, and `AppCard` by matching nearby page examples")
    return "; ".join(parts) if parts else "Inspect existing shared component directories before creating new primitives."


def detect_assets(root: Path) -> str:
    candidates = [
        "src/assets/images",
        "src/assets/img",
        "src/assets/icons",
        "src/assets",
        "public",
    ]
    found = [c for c in candidates if (root / c).exists()]
    if found:
        return "Prefer " + ", ".join(f"`{c}`" for c in found[:5]) + "; import app assets through project aliases when possible."
    return "Create assets under the nearest existing project asset directory; verify generated/downloaded files stay inside the project root."


def detect_commands(package_manager: str, scripts: dict[str, str]) -> tuple[str, str, str]:
    def run_script(name: str) -> str:
        if package_manager == "npm":
            return f"`npm run {name}`"
        return f"`{package_manager} {name}`"

    preferred = []
    for name in ("dev", "build", "build:check", "typecheck", "lint", "test", "preview"):
        if name in scripts:
            preferred.append(run_script(name))
    commands = ", ".join(preferred) if preferred else f"`{package_manager} install` then inspect package scripts"
    dev_server = run_script("dev") if "dev" in scripts else "Use the project's documented dev command."
    static_preferred = []
    for name in ("typecheck", "build:check", "lint", "test", "build"):
        if name in scripts:
            static_preferred.append(run_script(name))
    static_commands = ", ".join(static_preferred) if static_preferred else "Use the smallest relevant static check from package scripts."
    return commands, dev_server, static_commands


def detect_dev_url(root: Path, config_text: str) -> tuple[str, str]:
    port_match = re.search(r"\bport\s*:\s*(\d+)", config_text)
    port = port_match.group(1) if port_match else ""
    host = "localhost"
    if port:
        return f"http://{host}:{port}/", f"Vite/dev server appears to use port `{port}`."
    return "Project dev URL after starting the dev server.", "No fixed dev port detected."


def build_scan(root: Path) -> Scan:
    root = root.resolve()
    package = load_json(root / "package.json")
    scripts = package.get("scripts") if isinstance(package.get("scripts"), dict) else {}
    package_manager = detect_package_manager(root)
    config_names, config_text = scan_config_text(root)
    framework = detect_framework(package, config_names)
    commands, dev_server, static_commands = detect_commands(package_manager, scripts)
    dev_url, dev_hint = detect_dev_url(root, config_text)
    route_paths, page_discovery, route_boundaries = detect_routes(root, config_text)

    refs = []
    for candidate in [
        "AGENTS.md",
        "package.json",
        "vite.config.ts",
        "uno.config.ts",
        "eslint.config.ts",
        "src/router/basic-routes.ts",
        "build/index.ts",
        "src/views/login/index.vue",
    ]:
        if (root / candidate).exists():
            refs.append(candidate)

    return Scan(
        root=root,
        project_name=str(package.get("name") or root.name),
        package_manager=package_manager,
        scripts={str(k): str(v) for k, v in scripts.items()},
        framework=framework,
        language=detect_language(root, package),
        ui_library=detect_ui_library(package, config_text),
        styling=detect_styling(root, package, config_text),
        tokens=detect_tokens(root, config_text),
        route_paths=route_paths,
        page_discovery=page_discovery,
        route_boundaries=route_boundaries,
        aliases=detect_aliases(root, config_text),
        components=detect_components(root),
        assets=detect_assets(root),
        commands=commands,
        static_commands=static_commands,
        dev_server=dev_server + f" ({dev_hint})",
        dev_url=dev_url,
        auto_imports=detect_auto_imports(config_text),
        icons=detect_icons(root, config_text),
        theme_entry=detect_theme_entry(root, config_text),
        references=refs,
    )


def bullet_lines(items: Iterable[str]) -> str:
    values = [item for item in items if item]
    if not values:
        return "   - nearest existing page/component implementation"
    return "\n".join(f"   - `{item}`" for item in values)


def render_skill(scan: Scan) -> str:
    route_files = ", ".join(f"`{path}`" for path in scan.route_paths[:8]) if scan.route_paths else "Inspect route/page files before adding navigation."
    return f"""---
name: figma-to-project
description: Implement Figma designs and review UI/module code directly in this {scan.project_name} project using its UI framework, component library, styling tokens, code conventions, routing, asset, responsive, and verification workflow. Use when the user provides a Figma link/node and asks to build, restore, convert, or update a page/component from the design, or when the user asks to check whether a module/page/component complies with project UI and Figma-to-code conventions.
---

# Figma To Project

Use this skill to implement Figma designs as project-native code in `{scan.project_name}` and to review existing UI/module code against the same project conventions. Do not generate standalone HTML unless the user explicitly asks for an isolated prototype.

## Project Conventions

- Framework: {scan.framework}.
- Language: {scan.language}.
- UI library: {scan.ui_library}.
- Styling: {scan.styling}.
- Token/theme source: {scan.tokens}
- Theme entry: {scan.theme_entry}
- Auto imports: {scan.auto_imports}
- Icons: {scan.icons}
- Routes/pages: {route_files}
- Page discovery: {scan.page_discovery}
- Route/menu boundaries: {scan.route_boundaries}
- Path aliases: {scan.aliases}
- Components: {scan.components}
- Assets: {scan.assets}
- Commands: {scan.commands}
- Dev server: {scan.dev_server}
- Dev URL: `{scan.dev_url}`

## Figma Implementation Workflow

1. Read relevant project files before coding:
{bullet_lines(scan.references)}
   - closest existing page/component near the target feature
   - existing assets under the project asset directories
2. Use Figma MCP on the exact selected node/frame. With F2C MCP Plugin, confirm the target layer is selected in the F2C Chrome extension workflow before calling the tool.
3. Use `mcp__F2C_MCP.get_code_to_component` to generate high-fidelity reference code for the selected node/frame. Set `framework` to the closest project match (`vue`, `react`, or `html`) and set `style` to `css` unless this project already uses Tailwind-compatible utilities. If the tool is not exposed in the current session, stop and ask the user to enable/restart F2C MCP Plugin or provide Figma JSON, screenshots, and exported assets; do not silently use an unspecified fallback.
4. Extract layout, colors, typography, spacing, radii, shadows, image refs, SVG/icon nodes, and component hierarchy from the F2C output. Treat generated code as reference unless it exactly matches this project's stack.
5. If using F2C `localPath`, write only to a project-contained temporary draft directory first, then move verified assets into the project asset directory and confirm the files exist inside the project root.
6. Implement directly in the project using existing components, tokens, and styling primitives first.
7. Put pages/components in the detected project directories and respect route/menu ownership boundaries.
8. Keep changes scoped. Do not touch unrelated dirty files.
9. Run the smallest useful verification command, then use browser screenshots for desktop and mobile when a page changes.

## Module Compliance Review Workflow

Use this workflow when asked to review an existing module, page, component, or diff for project/Figma-to-code compliance.
Compliance reviews are read-only by default: report findings without editing files unless the user explicitly asks you to fix the issues.

1. Identify the review target:
   - files, route, component, feature folder, or git diff range
   - related Figma node/link when provided
   - whether the expected output is findings only or fixes are allowed
2. Read the same project conventions listed above plus the closest existing comparable implementation.
3. Check project integration:
   - uses the detected framework, UI library, theme tokens, styling utilities, icon system, and component shells
   - places pages, components, styles, and assets in the expected directories
   - respects route/menu ownership and permission boundaries
   - avoids introducing new UI frameworks, design systems, global styles, or unapproved dependencies
4. Check Figma/design compliance when a design reference exists:
   - layout hierarchy, spacing, typography, colors, radii, shadows, imagery, and component states
   - desktop high-fidelity and tablet/mobile reflow
   - no fixed full-canvas scaling or viewport-ratio blank bands
5. Check UI/UX quality gates:
   - accessibility: labels, alt text, keyboard order, visible focus, contrast
   - interaction: 44px+ targets where practical, press/focus/disabled/loading states, no hover-only critical actions
   - forms: semantic inputs, autocomplete/inputmode, inline errors, submit feedback
   - responsive safety: no horizontal scroll, clipped controls, text overlap, or layout jumps
   - performance: reserved image dimensions/aspect ratios and no avoidable resize/layout loops
6. Run or recommend the smallest useful verification command from the project command list.
7. Report findings first, ordered by severity, with concrete file references. If no issues are found, say so and mention remaining verification gaps.

## Implementation Rules

- Do not introduce a new UI library, CSS framework, or icon system without explicit approval.
- Do not create a parallel design system. Prefer existing components, theme variables, and project styling utilities.
- If this project already uses visual atomic/utility-first classes, prefer those utilities and project shortcuts for new page/component layout, spacing, color, typography, radius, and common state styling. Do not make atomic classes mandatory: scoped styles remain appropriate for third-party component deep overrides, complex selectors, media queries, dynamic values, and one-off effects that are clearer outside utility classes.
- Do not convert Figma into fixed full-canvas scaling such as `transform: scale(...)` on a 1920px design.
- Desktop should closely match the Figma design; tablet/mobile may reflow while preserving hierarchy, brand, and core interactions.
- Use responsive grid/flex utilities, `max-width`, percentages, `clamp()`, and project breakpoints instead of fixed viewport assumptions.
- Background hero images should generally use cover/object-cover behavior and fill the viewport or containing panel without blank bands.
- Avoid horizontal scroll, clipped controls, blank viewport bands, text overlap, and layout jumps.
- Keep click/touch targets at least 44px high where practical.
- Preserve semantic form behavior: visible labels or accessible labels, autocomplete/inputmode, loading states, and inline validation/messages where applicable.
- Use meaningful alt text for content images; decorative icons/images can use empty alt.
- Use component-scoped or feature-local styles as a complement to project utilities for design-specific effects that are awkward in utility classes.

## UI/UX Quality Gates

Apply `$ui-ux-pro-max` as the generic quality reference when UI is changed:

- Accessibility first: contrast, focus visibility, labels, alt text, keyboard order.
- Touch and interaction: 44px+ hit areas, pointer cursor, visible press/focus states, no hover-only behavior.
- Performance: reserve image dimensions or aspect ratios, avoid layout shift, avoid JS resize loops when CSS can solve layout.
- Responsive layout: verify small phone, tablet, desktop, and wide desktop where practical.
- Form UX: semantic inputs, autocomplete/inputmode, clear error placement, submit loading feedback.
- Motion: keep transitions purposeful around 150-300ms and respect `prefers-reduced-motion`.

## Verification

- Static checks: run the smallest relevant command from {scan.static_commands}.
- Dev server: {scan.dev_server}
- Dev URL: `{scan.dev_url}`
- Screenshot viewports:
  - desktop: 1440x900 or the Figma desktop frame ratio
  - tablet/small desktop: 1024x768
  - mobile: 390x844 or 375x812
- Required visual checks:
  - compare against Figma for layout, spacing, typography, colors, and assets
  - no horizontal scroll or clipped controls
  - no blank viewport bands caused by fixed frame ratios
  - focus state is visible on form controls and buttons
  - page remains usable in the active project layout
- Review checks:
  - findings are grounded in project files and conventions
  - route/menu/asset/style concerns are separated from visual polish concerns
  - when fixes are requested, keep patches scoped and reversible

## Reporting

When finished, report:

- files changed
- route or URL to inspect
- Figma node used
- assets downloaded
- verification commands and screenshot results
- any intentional deviations from the Figma design for responsive behavior

For compliance reviews, report:

- findings first, ordered by severity
- file/line references where available
- project convention or Figma requirement violated
- suggested fix or confirmation that no issue was found
- verification gaps that remain
"""


def render_openai_yaml(project_name: str) -> str:
    return f"""interface:
  display_name: "Figma To Project"
  short_description: "Implement Figma designs and review UI code in {project_name}."
  default_prompt: "Use $figma-to-project to implement this Figma URL/node or review this UI module in {project_name} from the project root."
"""


def add_agents_pointer(root: Path) -> bool:
    path = root / "AGENTS.md"
    if not path.exists():
        return False
    text = read_text(path)
    pointer = "For Figma design implementation or UI/module compliance review, use the project skill `figma-to-project`"
    if pointer in text or "figma-to-project" in text:
        return False
    addition = "\n\n" + pointer + " and follow project UI framework, component, styling, asset, routing, responsive, and verification conventions.\n"
    path.write_text(text.rstrip() + addition, encoding="utf-8")
    return True


def write_outputs(scan: Scan, output: Path, force: bool, update_agents_md: bool) -> list[Path]:
    written: list[Path] = []
    output = output.resolve()
    is_file_output = output.name.lower() == "skill.md" or bool(output.suffix)
    is_skill_output = not output.suffix or output.name.lower() == "skill.md"
    skill_path = output if is_file_output else output / "SKILL.md"
    skill_dir = skill_path.parent
    openai_path = skill_dir / "agents" / "openai.yaml"
    if skill_path.exists() and not force:
        raise SystemExit(f"{skill_path} already exists. Re-run with --force to overwrite, or pass --output to write a draft elsewhere.")
    if is_skill_output and openai_path.exists() and not force:
        raise SystemExit(f"{openai_path} already exists. Re-run with --force to overwrite, or pass --output to write a draft elsewhere.")
    skill_dir.mkdir(parents=True, exist_ok=True)
    skill_path.write_text(render_skill(scan), encoding="utf-8")
    written.append(skill_path)

    if is_skill_output:
        agents_dir = skill_dir / "agents"
        agents_dir.mkdir(parents=True, exist_ok=True)
        openai_path.write_text(render_openai_yaml(scan.project_name), encoding="utf-8")
        written.append(openai_path)

    if update_agents_md and add_agents_pointer(scan.root):
        written.append(scan.root / "AGENTS.md")
    return written


def is_inside(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def print_summary(scan: Scan, skill_text: str) -> None:
    print(f"Project: {scan.project_name}")
    print(f"Root: {scan.root}")
    print(f"Framework: {scan.framework}")
    print(f"UI library: {scan.ui_library}")
    print(f"Styling: {scan.styling}")
    print(f"Commands: {scan.commands}")
    print(f"Dev URL: {scan.dev_url}")
    print("")
    print(skill_text)


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="Generate a project-local figma-to-project skill from repository files.")
    parser.add_argument("project_root", nargs="?", default=".", help="Target project root. Defaults to current directory.")
    parser.add_argument("--output", default=str(SKILL_FILE), help="Output SKILL.md path or skill directory relative to project root.")
    parser.add_argument("--force", action="store_true", help="Overwrite an existing output skill.")
    parser.add_argument("--dry-run", action="store_true", help="Print the generated skill without writing files.")
    parser.add_argument("--update-agents-md", action="store_true", help="Append the Figma skill pointer to AGENTS.md when present and missing.")
    parser.add_argument("--allow-outside-output", action="store_true", help="Allow --output to write outside the project root. Intended for temporary drafts only.")
    args = parser.parse_args(argv)

    root = Path(args.project_root).resolve()
    if not root.exists() or not root.is_dir():
        raise SystemExit(f"Project root does not exist: {root}")
    if not (root / "package.json").exists():
        raise SystemExit(f"package.json not found in {root}; run from the frontend project root or pass the correct path.")

    scan = build_scan(root)
    skill_text = render_skill(scan)
    if args.dry_run:
        print_summary(scan, skill_text)
        return 0

    output = Path(args.output)
    if not output.is_absolute():
        output = root / output
    if not args.allow_outside_output and not is_inside(output, root):
        raise SystemExit(f"Refusing to write outside the project root: {output}. Pass --allow-outside-output for a temporary external draft.")
    written = write_outputs(scan, output, args.force, args.update_agents_md)
    for path in written:
        print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
