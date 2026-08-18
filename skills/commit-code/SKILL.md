---
name: commit-code
description: Generate a Conventional Commit message and commit current repository changes. Use when the user asks to commit, submit, save, or create a git commit for the current modified code, including Chinese requests such as "提交代码", "commit 当前修改", or "把当前改动提交一下".
---

# Commit Code

Create a git commit for the current repository changes using a concise Conventional Commit message.

## Workflow

1. Load project-specific commit rules before inspecting or committing changes.
   - Determine the project directory with `git rev-parse --show-toplevel`.
   - If `<project directory>/.commit-code-rule` exists, read its complete contents before continuing.
   - Treat the file as project-specific instructions: apply its commit-message requirements, validation/check commands, formatting or other required skills to the changes being committed.
   - If it names another available skill, read and use that skill's instructions as part of this workflow. If it requests a check or change, perform it and then re-inspect the resulting changes.
   - Higher-priority system, developer, and user instructions override the rule file. Do not run unsafe or out-of-scope actions; if a rule conflicts with those instructions or cannot be applied, stop and report the conflict instead of committing.
   - If the file does not exist, continue with the default workflow below.

2. Inspect repository state.
   - Run `git status --short`.
   - If there are no modified, staged, or untracked files, report that there is nothing to commit and stop.
   - Run `git diff --stat`, `git diff`, and `git diff --cached` as needed to understand the actual change.

3. Generate commit message fields.
   - **Type**: What kind of change is this?
   - **Scope**: What area/module is affected?
   - **Description**: One-line summary of what changed, in present tense and imperative mood, under 72 characters.

4. Use this message format:

```text
<type>[optional scope]: <description>
```

Examples:

```text
feat(auth): add password reset flow
fix(api): handle empty response payloads
docs: update setup instructions
```

5. Choose the type from this table.

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

6. Select a scope when it adds clarity.
   - Prefer an existing module, package, page, feature, config area, or filename stem.
   - Omit scope when the change is broad, repo-wide, or clearer without one.
   - Keep scope lowercase and hyphenated when possible.

7. Commit the changes.
   - Commit on the currently checked-out branch. Do not create, switch to, check out, or pull another branch.
   - Stage all current repository changes with `git add -A`.
   - Do not revert, amend, rebase, squash, or force-push unless the user explicitly asks.
   - Run `git commit -m "<message>"`.

8. Report the result.
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
