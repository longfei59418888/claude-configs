---
name: design-format
description: 获取股票的最新财报，并对财报进行分析，然后对比近半年的研报，给出财报是否符合预期
---

【!!!!! ⚠️警告: 访问浏览器之前，先关闭MCP playwright浏览器所有的 tab】

## Inputs

- **网站地址**：
- 项目目录以及所有代码

## output

- 文件 preview.html
- 文件 DESIGN.md

## 访问说明

使用 MCP playwright 访问网页，不可只依赖页面首屏内容，根据数据需求，访问内部页面；

## 核心

- 访问 网站地址 获取网站的样式和结构，不止是访问首页，需要访问 85% 以上的页面，分析页面样式
- 访问 项目目录以及所有代码，分析出项目和代码整体设计模型、样式

```md

The structure of a DESIGN.md file
A DESIGN.md file has 9 standard sections. Each one is a layer the agent reaches for when making a specific design
decision.

1. Visual theme and atmosphere
   The top of the file describes the brand's feel. Not tokens or pixels. Attitude and philosophy.

## Visual theme and atmosphere

Linear's interface embodies "opinionated calm." Every surface is dark,
every motion is restrained, every element earns its place through
information density, not decoration. The aesthetic borrows from
developer tooling: monospaced accents, tight spacing, muted palettes.
This section answers "why does it look like this?" The other 8 sections tell you what. This one tells you why.

2. Color palette and roles
   Every color is defined with its hex value and its semantic role. The file doesn't just say "blue." It says what that
   blue does.

## Color palette

| Role              | Token              | Value     |
|-------------------|--------------------|-----------|
| Background        | --bg-primary       | #000000   |
| Surface           | --bg-surface       | #141414   |
| Brand accent      | --accent-primary   | #5E6AD2   |
| Destructive       | --color-danger     | #E5484D   |
| Text primary      | --text-primary     | #EDEDEF   |
| Border default    | --border-default   | #2A2A2A   |

3. Typography rules
   Font family, size hierarchy, weight, line-height, and letter-spacing, all in a table, with context for which one goes
   where.

## Typography

Font: Inter (UI), JetBrains Mono (code)

| Level          | Size  | Weight | Line-height | Letter-spacing |
|----------------|-------|--------|-------------|----------------|
| Display        | 52px  | 500    | 1.1         | -2.4px         |
| Heading 1      | 32px  | 500    | 1.2         | -1.2px         |
| Body           | 14px  | 400    | 1.6         | -0.1px         |
| Caption        | 12px  | 400    | 1.4         | 0              |

4. Component styles
   Style definitions for core elements like buttons, cards, inputs, navigation, and badges, including all states.
   Padding, border-radius, shadow, hover/focus/disabled behavior.

## Components

### Button (primary)

- Background: var(--accent-primary)
- Padding: 6px 12px
- Border-radius: 6px
- Font-size: 13px, weight 500
- Hover: brightness(1.15)
- Focus: 2px ring offset 2px
- Disabled: opacity 0.5, pointer-events none

### Card

- Background: var(--bg-surface)
- Border: 1px solid var(--border-default)
- Border-radius: 8px
- Padding: 16px
- Shadow: none (depth comes from borders only)

5. Layout principles
   Spacing scale, grid system, container widths, whitespace approach, and border-radius scale.

## Layout

- Base unit: 4px
- Spacing scale: 4, 8, 12, 16, 24, 32, 48, 64
- Max content width: 1080px
- Section gap: 64-96px
- Border-radius scale: 4px (badge), 6px (button), 8px (card), 12px (modal)

6. Depth and elevation
   The shadow system, surface hierarchy, and elevation levels. Which layer gets which shadow, with specific rgba values.

## Depth and elevation

| Level     | Usage          | Shadow                                        |
|-----------|----------------|-----------------------------------------------|
| Level 0   | Page bg        | none                                          |
| Level 1   | Card, panel    | 0 1px 2px rgba(0,0,0,0.3)                     |
| Level 2   | Dropdown       | 0 4px 12px rgba(0,0,0,0.4)                    |
| Level 3   | Modal, dialog  | 0 8px 24px rgba(0,0,0,0.5)                    |

7. Do's and don'ts
   Design boundaries and anti-patterns. The "don't" list matters at least as much as the "do" list.

## Do's and don'ts

Do:

- Use border for separation, not shadow
- Keep letter-spacing tight on headings (-1px or more)
- Use opacity for disabled states, not gray tints

Don't:

- Don't use rounded-full on rectangular buttons
- Don't mix warm and cool grays in the same surface
- Don't use gradients on interactive elements
- Don't exceed 3 font weights on a single page

8. Responsive behavior
   Breakpoints, touch target sizes, and how things collapse on smaller screens.

## Responsive

| Breakpoint | Width   | Behavior                        |
|------------|---------|--------------------------------|
| Mobile     | < 640px | Single column, bottom nav       |
| Tablet     | < 1024px| Sidebar collapses to overlay   |
| Desktop    | >= 1024px| Full layout with persistent nav|

- Touch target minimum: 44x44px
- Font sizes don't drop below 13px on mobile

9. Agent prompt guide
   A quick-reference color summary and ready-to-use component prompts for the agent.

## Agent prompt guide

Quick palette: bg=#000, surface=#141414, accent=#5E6AD2, text=#EDEDEF

### Ready-to-use prompts:

- "Create a settings page" -> dark bg, grouped sections with subtle borders,
  toggle switches using accent color, 14px body text
- "Build a data table" -> compact rows (36px height), monospaced numbers,
  sticky header, hover row highlight at 4% white overlay

```

- 生成文件
    - 文件 preview.html，模版 './preview.html'
    - 文件 DESIGN.md，模版 './DESIGN.md'




