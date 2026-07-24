---
name: get-skill
description: Fetch a named skill folder or rule markdown file from the longfei59418888/claude-configs repository and install it into local agent directories. Use when the user asks to get, download, install, copy, sync, or globally install a skill from the skills collection, or asks to get, download, install, copy, or sync a rule from the rules collection. Ordinary skill requests like "获取 api-doc-update skill" install into the current project; explicit global skill requests like "全局安装 api-doc-update" install into system-level agent directories. Rule requests like "获取 code-convention rule" only install into the current project and update CLAUDE.md and AGENTS.md.
---

# Get Skill

Fetch configuration content from `longfei59418888/claude-configs`.

Supported content types:

- **Skill**: remote directory under `skills/<skill-name>`
- **Rule**: remote markdown file under `rules/<rule-name>.md`

## Intent Detection

1. Treat requests containing `rule`, `规则`, or a known rule-oriented phrase as rule requests.
   - Example: `获取 code-convention rule`
   - Example: `安装 directory-structure 规则`

2. Treat requests containing `skill`, `技能`, or no explicit rule indicator as skill requests.
   - Example: `获取 api-doc-update skill`
   - Example: `全局安装 api-doc-update`

3. If the content type is ambiguous, ask whether the user wants a skill or a rule before writing files.

4. Reject names containing `/`, `..`, or shell metacharacters.

## Skill Installation

Install a skill folder from remote `skills/<skill-name>`.

Default to project-level installation when the user says "获取 <skill-name> skill", "安装 <skill-name> skill", or similar requests without "全局安装":

- `<current-project>/.agent/skills/<skill-name>`
- `<current-project>/.claude/skills/<skill-name>`

Use system-level installation only when the user explicitly says "全局安装":

- `$HOME/.agent/skills/<skill-name>`
- `$HOME/.claude/skills/<skill-name>`

### Skill Workflow

1. Determine the requested skill name.
   - Use the explicit name from the user, such as `api-doc-update`.
   - If no skill name is provided, ask for it before running commands.

2. Determine the install scope.
   - Use project-level installation for "获取 api-doc-update skill", "安装 api-doc-update skill", and similar requests that do not explicitly say "全局安装".
   - Use system-level installation only when the request explicitly says "全局安装".
   - For project-level installation, destinations are `.agent/skills/$skill_name` and `.claude/skills/$skill_name` under the current working directory.
   - For system-level installation, destinations are `$HOME/.agent/skills/$skill_name` and `$HOME/.claude/skills/$skill_name`.

3. Download the remote repository to a temporary directory.

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

## Rule Installation

Install a rule markdown file from remote `rules/<rule-name>.md`.

Rule installation is project-level only:

- `.agent/rules/<rule-name>.md`
- `.claude/rules/<rule-name>.md`

Then ensure both project instruction files reference the installed Claude rule:

- `CLAUDE.md`
- `AGENTS.md`

Add this section when missing:

```markdown
## 规则
@.claude/rules/<rule-name>.md
```

If `## 规则` already exists, append only the missing `@.claude/rules/<rule-name>.md` line under that section.

### Rule Workflow

1. Determine the requested rule name.
   - Use the explicit name from the user, such as `code-convention`.
   - If no rule name is provided, ask for it before running commands.
   - Append `.md` when the user did not include it.

2. Use project-level installation only.
   - Do not support `全局安装` or global rule installation for rules.
   - If the user asks for global rule installation, explain that rule installation only writes into the current project.

3. Download the remote repository to a temporary directory.

```bash
tmp_dir="$(mktemp -d)"
curl -L "https://github.com/longfei59418888/claude-configs/archive/refs/heads/main.zip" -o "$tmp_dir/claude-configs-main.zip"
unzip -q "$tmp_dir/claude-configs-main.zip" -d "$tmp_dir"
```

4. Verify the requested rule exists before writing into the project.

```bash
rule_name="code-convention"
rule_file="${rule_name%.md}.md"
source_file="$tmp_dir/claude-configs-main/rules/$rule_file"
test -f "$source_file"
```

If the source file does not exist, report that the rule was not found and do not create or modify target files.

5. Create destination directories in the current working directory.

```bash
mkdir -p ".agent/rules" ".claude/rules"
```

6. Copy the remote rule file into both destinations.
   - Overwrite same-name rule files from the remote rule.
   - Do not delete extra existing local files unless the user explicitly asks for a clean reinstall.

```bash
cp "$source_file" ".agent/rules/$rule_file"
cp "$source_file" ".claude/rules/$rule_file"
```

7. Ensure `CLAUDE.md` and `AGENTS.md` exist in the project root.

```bash
touch CLAUDE.md AGENTS.md
```

8. Add the rule reference to both files.
   - Reference the `.claude` copy, not the `.agent` copy.
   - Add exactly one reference line per rule:

```markdown
@.claude/rules/code-convention.md
```

   - If a file has no `## 规则` section, append a blank line, then:

```markdown
## 规则
@.claude/rules/code-convention.md
```

   - If `## 规则` exists and the reference is missing, append the reference under that section.
   - If the same reference already exists anywhere in the file, do not add a duplicate.

9. Verify installed rule files and references.

```bash
test -f ".agent/rules/$rule_file"
test -f ".claude/rules/$rule_file"
grep -F "@.claude/rules/$rule_file" CLAUDE.md
grep -F "@.claude/rules/$rule_file" AGENTS.md
```

10. Clean up the temporary directory when the install succeeds or fails.

```bash
rm -rf "$tmp_dir"
```

## Notes

- Run project-level installs from the user's current project root unless the user specifies another destination.
- Use `$HOME/.agent` and `$HOME/.claude` only for explicit global skill installs.
- Never use system-level destinations for rule installs.
- If network access is blocked, request approval to run the download command with network access.
- If `unzip` is unavailable, use a shallow sparse git checkout of the needed `skills/<skill-name>` directory or `rules/<rule-name>.md` file into a temporary directory, then copy from there.
- After installation, summarize the content type, source name, install scope, and paths updated.
