---
name: get-skill
description: Fetch a named skill folder from https://github.com/longfei59418888/claude-configs/tree/main/skills and install it into agent skill directories. Use when the user asks to get, download, install, copy, sync, or globally install a skill from the longfei59418888/claude-configs skills collection. Ordinary requests like "获取 api-doc-update skill" install into the current project; explicit global requests like "全局安装 api-doc-update" install into the user's system-level agent directories.
---

# Get Skill

Install a skill from `longfei59418888/claude-configs` into agent skill locations.

Default to project-level installation when the user says "获取 <skill-name> skill", "安装 <skill-name> skill", or similar requests without "全局安装":

- `<current-project>/.agent/skills/<skill-name>`
- `<current-project>/.claude/skills/<skill-name>`

Use system-level installation only when the user explicitly says "全局安装":

- `$HOME/.agent/skills/<skill-name>`
- `$HOME/.claude/skills/<skill-name>`

## Workflow

1. Determine the requested skill name.
   - Use the explicit name from the user, such as `api-doc-update`.
   - If no skill name is provided, ask for it before running commands.
   - Treat the name as a path segment under the remote `skills/` directory; reject names containing `/`, `..`, or shell metacharacters.

2. Determine the install scope.
   - Use project-level installation for "获取 api-doc-update skill", "安装 api-doc-update skill", and similar requests that do not explicitly say "全局安装".
   - Use system-level installation only when the request explicitly says "全局安装".
   - For project-level installation, destinations are `.agent/skills/$skill_name` and `.claude/skills/$skill_name` under the current working directory.
   - For system-level installation, destinations are `$HOME/.agent/skills/$skill_name` and `$HOME/.claude/skills/$skill_name`.

3. Download the remote repository to a temporary directory.
   - Prefer a GitHub archive because it does not require a full git checkout:

```bash
tmp_dir="$(mktemp -d)"
curl -L "https://github.com/longfei59418888/claude-configs/archive/refs/heads/main.zip" -o "$tmp_dir/claude-configs-main.zip"
unzip -q "$tmp_dir/claude-configs-main.zip" -d "$tmp_dir"
```

4. Verify the requested skill exists before writing into the destination.

```bash
skill_name="api-doc-update"
source_dir="$tmp_dir/claude-configs-main/skills/$skill_name"
test -d "$source_dir"
```

If the source directory does not exist, report that the skill was not found and do not create or modify target directories.

5. Create destination directories.

For system-level installation:

```bash
agent_dest="$HOME/.agent/skills/$skill_name"
claude_dest="$HOME/.claude/skills/$skill_name"
mkdir -p "$agent_dest" "$claude_dest"
```

For project-level installation:

```bash
agent_dest=".agent/skills/$skill_name"
claude_dest=".claude/skills/$skill_name"
mkdir -p "$agent_dest" "$claude_dest"
```

6. Copy the remote skill contents into both destinations.
   - Copy all files, including dotfiles.
   - Overwrite same-name files from the remote skill.
   - Do not delete extra existing local files unless the user explicitly asks for a clean reinstall.

```bash
cp -R "$source_dir"/. "$agent_dest/"
cp -R "$source_dir"/. "$claude_dest/"
```

7. Verify both installed copies contain `SKILL.md`.

```bash
test -f "$agent_dest/SKILL.md"
test -f "$claude_dest/SKILL.md"
```

8. Clean up the temporary directory when the install succeeds or fails.

```bash
rm -rf "$tmp_dir"
```

## Notes

- Use `$HOME/.agent` and `$HOME/.claude` for system-level installs.
- Run project-level installs from the user's current project root unless the user specifies another destination.
- If network access is blocked, request approval to run the download command with network access.
- If `unzip` is unavailable, use a shallow sparse git checkout of `skills/<skill-name>` into a temporary directory, then copy from there.
- After installation, summarize the source skill name, install scope, and the two destination paths that were updated.
