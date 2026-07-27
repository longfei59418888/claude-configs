---
name: commit-code
description: Generate a Conventional Commit message and commit current repository changes. Use when the user asks to commit, submit, save, or create a git commit for the current modified code, including Chinese requests such as "提交代码", "commit 当前修改", or "把当前改动提交一下".
---

# Commit Code

Create a git commit for the current repository changes using a concise Conventional Commit message.

## Workflow

1. Inspect repository state.
   - Run `git status --short`.
   - If there are no modified, staged, or untracked files, report that there is nothing to commit and stop.
   - Run `git diff --stat`, `git diff`, and `git diff --cached` as needed to understand the actual change.

2. Generate commit message fields.
   - **Type**: What kind of change is this?
   - **Scope**: What area/module is affected?
   - **Description**: One-line summary of what changed, in present tense and imperative mood, under 72 characters.

3. Use this message format:

```text
<type>[optional scope]: <description>
```

Examples:

```text
feat(auth): add password reset flow
fix(api): handle empty response payloads
docs: update setup instructions
```

4. Choose the type from this table.

| Type | Purpose |
| --- | --- |
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `style` | Formatting/style, no logic |
| `refactor` | Code refactor, no feature/fix |
| `perf` | Performance improvement |
| `test` | Add/update tests |
| `build` | Build system/dependencies |
| `ci` | CI/config changes |
| `chore` | Maintenance/misc |
| `revert` | Revert commit |

5. Select a scope when it adds clarity.
   - Prefer an existing module, package, page, feature, config area, or filename stem.
   - Omit scope when the change is broad, repo-wide, or clearer without one.
   - Keep scope lowercase and hyphenated when possible.

6. Commit the changes.
   - Stage the current relevant changes with `git add`.
   - Do not revert, amend, rebase, squash, or force-push unless the user explicitly asks.
   - If unrelated changes are present and the requested commit target is ambiguous, ask before staging.
   - Run `git commit -m "<message>"`.

7. Report the result.
   - Include the exact commit message.
   - Include the new commit hash from `git rev-parse --short HEAD`.
   - Mention if tests were not run.

## Message Rules

- Use English commit messages unless the user explicitly requests another language.
- Use imperative mood: `add`, `fix`, `update`, `remove`, `refactor`.
- Keep the description specific to the main behavioral or project change.
- Keep the first line under 72 characters.
- Do not end the description with a period.
- Use `revert:` only when the commit actually reverts a previous commit.
