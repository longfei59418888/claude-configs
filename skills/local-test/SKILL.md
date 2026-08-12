---
name: local-test
description: Test a running local web application in a real browser through the local Playwright MCP, covering requirements, tasks, user flows, UI behavior, and regressions. Use when needs to open a localhost or other project-local URL, interact with the page, verify acceptance criteria, handle login-gated pages with project-local credentials, or report that the local server is unavailable without starting it.
---

# Playwright MCP Local Test

Use this skill to perform browser-based validation against a local project server. Treat the rendered browser page as the source of truth for UI behavior; do not infer results from source code alone.

## Operating constraints

- Use the available local Playwright MCP/browser tools for every webpage action: navigation, inspection, clicking, typing, screenshots, and assertions.
- Do not start, restart, stop, or otherwise modify the project's local server. If no server is running or the URL cannot be reached, tell the user exactly what URL was checked and ask them to start it.
- Do not substitute HTTP requests or guessed results for browser validation. Use source inspection only to diagnose a browser failure.
- Treat credentials as sensitive. Never print, quote, screenshot, or include the password in the final report.
- Unless the user explicitly asks to keep it open, close pages, contexts, and the browser after testing, including after failures.

## Workflow

### 1. Load project configuration safely

At the beginning of every test, identify the project root and check for `<project-root>/.playwright-mcp-config` before choosing a URL or performing any user operation.

- If the file does not exist, create it with restrictive permissions (`0600` when supported). Create only this non-secret template; do not invent credentials or a server address:

  ```text
  # Local Playwright MCP configuration
  PLAYWRIGHT_MCP_BASE_URL=
  PLAYWRIGHT_MCP_USERNAME=
  PLAYWRIGHT_MCP_PASSWORD=
  ```

- If the file exists, read its values before navigation, login, or other user interactions. Preserve and reuse unrelated configuration keys when updating it.
- Use `PLAYWRIGHT_MCP_BASE_URL` as the target local server URL when it is non-empty. Accept a complete URL, including a path, and do not replace it with a guessed localhost URL. If it is empty, determine the URL from the user's request or project documentation; ask only when no reasonable URL can be determined.
- Treat all values as sensitive. Never print, quote, screenshot, or include passwords, tokens, or other secret values in the final report.

Use this simple dotenv-like format when reading or writing it:

```text
PLAYWRIGHT_MCP_USERNAME=...
PLAYWRIGHT_MCP_PASSWORD=...
```

- Ignore blank lines and lines beginning with `#`.
- Values may be single- or double-quoted; remove only the wrapping quotes.
- Do not display parsed values in tool output or chat.
- Make all configuration values available to the test workflow when needed for login and other user operations; do not expose them in logs or screenshots.
- If the file is incomplete, continue until the missing value actually blocks the requested operation, then ask the user only for that value.
- After the user provides credentials, save them to the project-root file in the format above, preserving unrelated existing keys if present. Create the file with restrictive permissions (`0600`) when the environment supports it. Do not save credentials anywhere else.
- Never commit, stage, upload, or include `.playwright-mcp-config` in screenshots or test artifacts. If the repository has ignore rules, add the file to the project's local ignore configuration only if the user has authorized repository configuration changes; otherwise warn the user that it should be ignored.

If credentials already exist, fill the login form only when needed. Do not proactively log out or overwrite a working authenticated session. If stored credentials fail, do not repeatedly retry; report that the saved credentials were rejected and ask the user whether to update them.

### 2. Establish the target

1. Use the non-empty `PLAYWRIGHT_MCP_BASE_URL` from the configuration file as the entry URL. Otherwise use the URL determined from the user's request or project documentation.
2. Check reachability by opening the selected URL with Playwright MCP. A refused connection, timeout, DNS failure, or unavailable page means the local server is not ready; stop and ask the user to start it. Do not run a package script, shell command, Docker command, or MCP startup command on the user's behalf.

### 3. Translate the request into checks

Before acting, turn the requirement or task into a short checklist of observable outcomes:

- entry URL and required preconditions;
- controls, navigation, and data to exercise;
- expected visible states, URL changes, feedback, and error handling;
- responsive or accessibility checks explicitly requested;
- negative, boundary, and regression cases implied by the requirement.

Prefer stable user-facing selectors such as roles, labels, visible text, and placeholders. Use CSS or XPath only when necessary. Do not mutate application data beyond what the requested test requires; when mutation is required, state the test data or side effect before performing it.

### 4. Execute and collect evidence

For each checklist item:

1. Navigate or continue from the appropriate state.
2. Inspect the relevant rendered content before acting.
3. Perform the smallest realistic user interaction.
4. Assert the expected outcome using visible text, role/state, URL, form value, or other observable browser state.
5. Capture a screenshot or other Playwright evidence for failures and important acceptance criteria when useful.

When a failure occurs, preserve the first actionable error, current URL, visible page state, and reproduction steps. Distinguish clearly between:

- **blocked**: server unavailable, Playwright MCP unavailable, or credentials required from the user;
- **failed**: the app is reachable but an expected behavior is wrong;
- **passed**: the observable acceptance criterion was verified.

Do not claim a check passed merely because navigation succeeded.

### 5. Clean up and report

Before responding, close all pages, browser contexts, and the browser instance created or used for the test. Confirm that no Playwright browser resources remain when the MCP exposes that state. If cleanup fails, report it separately.

Report concisely:

- target URL and whether the local server was reachable;
- checks passed, failed, or blocked;
- failure details with safe evidence and reproduction steps;
- whether login was required (never include credentials);
- cleanup status;
- the exact action the user must take for any blocker, such as starting the local server or providing missing login details.

The configuration file is intentionally project-local and should remain untracked. Do not commit or stage it.
