---
name: worktree-option
description: Create, delete, and clean Git worktrees for a repository. Use when the user asks to create a workspace/worktree, such as "创建工作区 feature-login", "创建worktree feature-login", or asks to delete/clean one or all worktrees, such as "删除工作区feature-login", "删除工作区", "清理 worktree".
---

# Worktree

Manage Git worktrees from the current repository, using sibling directories for added worktrees.

## Naming Rules

- Treat the user-provided worktree name as the sibling directory name.
  - Example: `feature-login` -> `../feature-login`
- Infer the branch name from the worktree name when the user does not provide an explicit branch.
  - For names like `feature-login`, use `feature/login`.
  - Prefer common branch prefixes such as `feature`, `fix`, `bugfix`, `hotfix`, `chore`, `docs`, `refactor`, `test`, and `release`.
  - If the branch name is ambiguous, ask before running Git commands.
- If the user provides a branch name with `/`, preserve it exactly.

## Create A Worktree

1. Inspect branch/worktree state:

```bash
git branch --list <branch>
git worktree list
```

2. If the local branch already exists, add the worktree with the existing branch:

```bash
git worktree add ../feature-login feature/login
```

3. If the local branch does not exist, create it from `origin/main` while adding the worktree:

```bash
git worktree add ../feature-login -b feature/login origin/main
```

4. If the target sibling directory already exists, stop and report the conflict. Do not overwrite or delete it unless the user explicitly asks.

5. After the worktree is created, link the new worktree's `node_modules` to the current repository's `node_modules` so the added worktree reuses the primary project's installed dependencies:

```bash
ln -s "$(pwd)/node_modules" ../feature-login/node_modules
```

- Run this only when the current repository has a `node_modules` directory.
- If `../feature-login/node_modules` already exists, do not overwrite it. Report the existing path and ask before changing it.
- Report the source and target paths of the `node_modules` link.

## Delete One Worktree

For a request such as `删除工作区 feature-login`, remove only that sibling worktree and then prune:

```bash
git worktree remove ../feature-login
git worktree prune
```

Before removing, check whether the target worktree has uncommitted changes:

```bash
git -C ../feature-login status --short
```

If there are changes, warn that removal may discard uncommitted work and stop for explicit user confirmation. Do not use `--force` unless the user explicitly confirms.

## Delete All Added Worktrees

For a request like `删除工作区` with no specific name, treat it as deleting all added worktrees.

1. List worktrees:

```bash
git worktree list
```

2. Identify added worktrees from the list. Do not remove the primary repository worktree.
3. For each added worktree, check for uncommitted changes:

```bash
git -C <worktree-path> status --short
```

4. If any added worktree has uncommitted changes, warn that deleting it may discard uncommitted work and skip deletion until the user explicitly confirms what to remove.
5. Remove each confirmed clean worktree:

```bash
git worktree remove <worktree-path>
```

6. Prune stale worktree metadata:

```bash
git worktree prune
```

## Safety Rules

- Never delete the current repository directory as part of "delete all worktrees".
- Never use `git worktree remove --force` without explicit user confirmation.
- Never run destructive cleanup commands outside the repository's sibling worktree paths unless the user explicitly provides the path and confirms.
- Report the exact worktree paths and branch names used.
