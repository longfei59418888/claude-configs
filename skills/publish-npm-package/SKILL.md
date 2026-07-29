---
name: publish-npm-package
description: Bump the package.json version and publish an npm package to the public npm registry. Use when the user asks to upload, release, publish, or deploy an npm package, including Chinese requests such as "上传npm包", "发布 npm 包", "上传npm包 小版本", or "上传npm包 大版本".
---

# Publish Npm Package

## Overview

Publish an npm package by first updating `package.json` version, then running `npm publish --access public`. Stop for manual login when npm authentication is missing.

## Workflow

1. Identify the package root.
   - Use the user's explicit directory when provided.
   - Otherwise use the current working directory.
   - If the current directory is inside a package, walk upward until finding the nearest `package.json`.
   - If no `package.json` is found, ask for the target package directory before publishing.

2. Inspect the current package state.
   - Read `package.json` and confirm it has `name` and `version`.
   - Run `git status --short` and report unrelated uncommitted changes before editing.
   - If the package name or version is missing, stop and ask before publishing.

3. Determine the version bump.
   - Default request such as `上传npm包`: bump the patch version.
     - Example: `1.0.1` -> `1.0.2`
   - `上传npm包 小版本`: bump the minor version and reset patch to `0`.
     - Example: `1.0.2` -> `1.1.0`
   - `上传npm包 大版本`: bump the major version and reset minor and patch to `0`.
     - Example: `1.1.2` -> `2.0.0`
   - If the user provides an explicit version, use that exact version after verifying it is greater than the current version.
   - If the current version is not a normal SemVer value like `1.2.3`, ask before editing.

4. Update the version.
   - Prefer `npm version <new-version> --no-git-tag-version` from the package root so `package.json` and `package-lock.json` stay consistent when applicable.
   - If no lockfile is present, directly editing `package.json` is acceptable, but preserve formatting.
   - Do not create a git tag unless the user explicitly asks.

5. Verify npm authentication before publishing.

```bash
npm whoami
```

If `npm whoami` fails because the user is not logged in, stop and tell the user to run `npm login` manually. After the user confirms login is complete, run `npm whoami` again.

6. Publish to the public npm registry.

```bash
npm publish --access public
```

7. Verify and report the result.
   - Report the package name and old/new version.
   - Include the exact publish command.
   - If publishing fails because the version already exists on npm, do not retry with another version unless the user explicitly asks.
   - If publishing succeeds, report that the package was published.

## Version Examples

| Request | Current version | New version |
| --- | --- | --- |
| `上传npm包` | `1.0.1` | `1.0.2` |
| `上传npm包 小版本` | `1.0.2` | `1.1.0` |
| `上传npm包 大版本` | `1.1.2` | `2.0.0` |

## Safety Rules

- Do not run `npm login` on behalf of the user.
- Do not publish without bumping or explicitly confirming the version.
- Do not use `--force`.
- Do not change package manager dependencies or unrelated files.
- Do not publish private packages publicly unless the user explicitly confirms public publishing.
