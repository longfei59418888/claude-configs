---
name: install-npm-package
description: Install npm ecosystem packages into an existing JavaScript/TypeScript project. Use when the user asks to install, add, or update an npm package/dependency, including requests such as "安装 lodash", "add react-query", "install this as a dev dependency", or "把 eslint 加到项目里". Before installing, detect the project's package manager and use the matching install command.
---

# Install NPM Package

## Overview

Install npm packages with the package manager already used by the target project. Do not assume `npm`; inspect the project first and preserve the existing dependency workflow.

## Workflow

1. Identify the target project directory.
   - Use the user's explicit directory when provided.
   - Otherwise use the current working directory.
   - If the current directory is inside a project, walk upward until finding the nearest `package.json`.
   - If no `package.json` is found, ask for the target project directory before installing.

2. Determine the package manager from project files, in this order:
   - `package.json` `packageManager` field, such as `pnpm@...`, `yarn@...`, `npm@...`, or `bun@...`.
   - Lockfiles in the target project root:
     - `pnpm-lock.yaml` -> `pnpm`
     - `yarn.lock` -> `yarn`
     - `package-lock.json` or `npm-shrinkwrap.json` -> `npm`
     - `bun.lockb` or `bun.lock` -> `bun`
   - Workspace indicators:
     - `pnpm-workspace.yaml` -> `pnpm`
     - Yarn workspace configuration with `yarn.lock` -> `yarn`
   - If evidence conflicts, prefer the `packageManager` field. If there is no reliable signal, ask before installing.

3. Classify the dependency type from the user's request.
   - Default to a production dependency.
   - Use dev dependency when the user says dev, development, `-D`, `--save-dev`, tooling, linting, testing, types, build tooling, or similar.
   - Use peer or optional dependency only when the user explicitly asks.
   - Preserve any version/range/tag from the request, such as `react@18`, `@types/node@latest`, or `eslint@^9`.

4. Install with the detected package manager from the target project root.

| Package manager | Production dependency | Dev dependency | Peer dependency | Optional dependency |
| --- | --- | --- | --- | --- |
| `pnpm` | `pnpm add <pkg>` | `pnpm add -D <pkg>` | `pnpm add --save-peer <pkg>` | `pnpm add -O <pkg>` |
| `yarn` | `yarn add <pkg>` | `yarn add -D <pkg>` | `yarn add -P <pkg>` | `yarn add -O <pkg>` |
| `npm` | `npm install <pkg>` | `npm install -D <pkg>` | `npm install --save-peer <pkg>` | `npm install -O <pkg>` |
| `bun` | `bun add <pkg>` | `bun add -d <pkg>` | `bun add --peer <pkg>` | `bun add --optional <pkg>` |

5. Verify the result.
   - Check `package.json` and the relevant lockfile changed as expected.
   - Run the package manager's install command only once unless there is a clear failure to recover from.
   - If the install command fails because dependencies cannot be downloaded due to restricted network or sandboxing, rerun the same command with the required escalation/approval flow.
   - Do not run broad test suites unless the user asks or the package install obviously requires a project-specific validation step.

## Workspace Projects

For monorepos, install into the package that owns the user's requested change:

- If the user names a workspace package, run the package manager command in that package directory or use the package manager's established workspace filter syntax.
- If the request applies to the root tooling, install at the workspace root.
- If the target package is ambiguous, inspect the files related to the user's task. Ask only when the target still cannot be inferred safely.

## Command Discipline

- Do not mix package managers in the same project.
- Do not manually edit dependency entries or lockfiles when the package manager can do it.
- Do not delete lockfiles or regenerate unrelated package metadata.
- Include the exact command run and the detected package manager in the final response.
