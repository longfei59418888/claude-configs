# claude-configs

## npm 全局安装

执行：

```bash
npm install -g @xlong/get-skill
```

安装 npm 包时，会自动将内置的 `skills/get-skill` 复制到当前用户主目录下的系统级 skills 配置目录：

```text
<用户主目录>/.agent/skills/get-skill
<用户主目录>/.claude/skills/get-skill
```

在 macOS/Linux 中，用户主目录通常是 `$HOME`；在 Windows 中，用户主目录通常是 `%USERPROFILE%`。安装脚本使用 Node.js 的
`os.homedir()` 获取用户主目录，因此兼容 Windows、macOS 和 Linux。

安装后即可通过 `get-skill` 获取本仓库中的 skill 或 rule。

## get-skill 使用说明

`skills/get-skill` 用于将 /skills 目录下指定 skill 安装到 skills 目录中。

### skill 安装到项目中

输入：

```text
获取/安装 api-doc-update skill
```

会下载安装到项目中：

```text
.agent/skills/api-doc-update
.claude/skills/api-doc-update
```

### skill 安装到系统中

输入：

```text
全局安装 api-doc-update
```

会下载安装到：

```text
$HOME/.agent/skills/api-doc-update
$HOME/.claude/skills/api-doc-update
```

### rule 安装到项目中

输入：

```text
获取/安装 directory-structure rule
```

会下载安装到项目中：

```text
.agent/rules/directory-structure.md
.claude/rules/directory-structure.md
```

## Skills

- api-doc-update<API生成skill>
- commit-code<git提交skill>
- design-format<网站样式规范生成skill>
- get-skill<skill和rule安装skill>
- install-npm-package<npm包安装skill>
- publish-npm-package<npm包发布上传skill>
- worktree-option<git worktree工作区管理skill>

## Rules

- directory-structure<react项目规范>
- figma-component-development<figma组件开发规范>
- nestjs-code-convention<nestjs项目规范>
- nestjs-sql-migration<nestjs项目sql迁移规范>
- playwright-use<Playwright MCP使用规范>
- task-planning<任务分析规范>
