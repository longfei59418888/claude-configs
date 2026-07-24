---
name: get-rule
description: Fetch a named rule markdown file from https://github.com/longfei59418888/claude-configs/tree/main/rules and install it into the current project's .agent/rules and .claude/rules directories. Use when the user asks to get, download, install, copy, or sync a rule from the longfei59418888/claude-configs rules collection, for example "获取 code-convention rule" or "install the directory-structure rule". This skill only supports project-level rule installation and must not perform global rule installation.
---

# Get Rule

Install a rule from `longfei59418888/claude-configs` into the current project.

Rules are markdown files under the remote `rules/` directory. Normalize the user-provided rule name to a markdown
filename:

- `code-convention` becomes `code-convention.md`
- `code-convention.md` stays `code-convention.md`

Install into both project-level rule locations:

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

## Workflow

1. Determine the requested rule name.
    - Use the explicit name from the user, such as `code-convention`.
    - If no rule name is provided, ask for it before running commands.
    - Reject names containing `/`, `..`, or shell metacharacters.
    - Append `.md` when the user did not include it.

2. Use project-level installation only.
    - Do not support `全局安装` or global rule installation.
    - If the user asks for global rule installation, explain that `get-rule` only installs rules into the current
      project.

3. Download the remote repository to a temporary directory.
    - Prefer a GitHub archive because it does not require a full git checkout:

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

- Run commands from the user's current project root unless the user specifies another destination.
- If network access is blocked, request approval to run the download command with network access.
- If `unzip` is unavailable, use a shallow sparse git checkout of `rules/<rule-name>.md` into a temporary directory,
  then copy from there.
- After installation, summarize the source rule name, the two copied rule paths, and whether `CLAUDE.md` and `AGENTS.md`
  were updated or already contained the reference.
