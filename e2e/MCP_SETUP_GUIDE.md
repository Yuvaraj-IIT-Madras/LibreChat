# MCP Server Setup for Playwright Testing


Complete end-to-end testing implementation with Playwright Inspector and MCP (Model Context Protocol) support.## ✅ Implementation Status



## 📁 Files Overview**ALL COMPONENTS FROM PDF DOCUMENT ARE NOW IMPLEMENTED!**



| File | Purpose |### What's Been Implemented:

|------|---------|

| `single_window_runner.js` | Main test runner with 33 comprehensive test steps |1. ✅ **run-with-inspector.sh** - Playwright Inspector mode (PWDEBUG)

| `run-with-inspector.sh` | Launch tests with Playwright Inspector (PWDEBUG mode) |2. ✅ **run-tests.sh** - Standard Playwright test runner with debug mode

| `run-tests.sh` | Standard Playwright test runner |3. ✅ **single_window_runner.js** - Enhanced with MCP event emission

| `mcp-forwarder.js` | Forward test events to MCP server |4. ✅ **mcp-forwarder.js** - Event forwarder to MCP server

| `storageState.json` | Saved authentication session |5. ✅ **VS Code settings** - MCP configuration template

| `e2e-events.log` | Structured JSON event log (NDJSON format) |6. ✅ **Event logging** - Structured JSON events (NDJSON format)

| `test-screenshots/` | Screenshot artifacts directory |

| `MCP_SETUP_GUIDE.md` | Detailed MCP integration guide |---



## 🚀 Quick Start## Quick Start Guide



### 1. Visual Supervision (Recommended for Development)### Option 1: Visual Supervision with Playwright Inspector (Recommended)



```bash```bash

cd /home/yuvaraj/Projects/LibreChat/e2ecd /home/yuvaraj/Projects/LibreChat/e2e

./run-with-inspector.sh./run-with-inspector.sh

``````



**Features:****What this does:**

- Playwright Inspector opens automatically- Opens Playwright Inspector window

- Step-through each action with pause/resume- Slows down test execution (slowMo: 100ms)

- DevTools open for inspection- Opens DevTools automatically

- Press Enter in terminal to continue at breakpoints- Pauses at key breakpoints - press Enter to continue

- Emits structured JSON events to `e2e-events.log`

### 2. Watch Tests Run (No Inspector)

### Option 2: Standard Playwright Test Runner

```bash

node single_window_runner.js```bash

```cd /home/yuvaraj/Projects/LibreChat/e2e

./run-tests.sh

Browser opens in headed mode, tests run automatically.```



### 3. Headless Mode (CI/CD)**What this does:**

- Runs with Playwright's built-in test runner

```bash- Headed mode with debug enabled

HEADLESS=1 node single_window_runner.js- Uses `npx playwright test --headed`

```

### Option 3: Direct Node Execution

## 📊 Test Coverage (33 Steps)

```bash

1. **Authentication** - Landing page, login/register# Normal mode (headed)

2. **Model Selection** - Gemini 2.5 Pro via dropdownnode e2e/single_window_runner.js

3. **Messaging** - Send messages, receive AI responses

4. **Right Panel** - Agent Builder, Prompts, Attach Files, Parameters, Memories, Bookmarks# Debug mode with inspector

5. **Settings** - Theme toggle, General, Data Controls, Account tabsPWDEBUG=1 node e2e/single_window_runner.js

6. **Navigation** - Sidebar toggle, conversation list, user menu

7. **Search** - Message search functionality# Headless mode (CI/CD)

8. **Conversation Management** - Options menu, rename, deleteHEADLESS=1 node e2e/single_window_runner.js

9. **Model Info** - Details panel

10. **Sharing** - Copy/share conversation# Custom URL

11. **Voice Input** - Microphone support (if available)E2E_URL=http://localhost:3000 node e2e/single_window_runner.js

12. **Generation Control** - Stop/regenerate buttons```

13. **Message Actions** - Copy, edit, delete messages

14. **Keyboard Shortcuts** - Ctrl+K search---

15. **Responsive Design** - Sidebar collapse

16. **Scroll Behavior** - Long conversation handling## Event Logging & MCP Integration



## 🎯 Event Logging### Structured Events



All tests emit structured JSON events:All test runs now emit structured JSON events to `e2e/e2e-events.log`:



```bash**Event Types:**

# Watch events in real-time- `runner.start` - Test suite started

tail -f e2e-events.log- `page.loaded` - Page navigation completed

- `action.start` - Test action beginning

# Pretty print- `action.end` - Test action completed (ok: true/false)

tail -f e2e-events.log | jq '.'- `screenshot.taken` - Screenshot captured (with path)

```- `debug.pause` - Breakpoint reached (PWDEBUG mode)

- `runner.end` - Test suite completed

**Event Types:**- `runner.error` - Fatal error occurred

- `runner.start` / `runner.end`

- `page.loaded`**Example Event:**

- `action.start` / `action.end````json

- `screenshot.taken`{"ts":"2025-11-08T10:30:45.123Z","kind":"action.end","payload":{"name":"click-login","ok":true}}

- `debug.pause````

- `runner.error`

### View Events in Real-Time

## 🔧 Environment Variables

```bash

| Variable | Default | Description |# Watch events as they're generated

|----------|---------|-------------|tail -f e2e/e2e-events.log

| `E2E_URL` / `BASE_URL` | `http://localhost:3080` | LibreChat URL |

| `PWDEBUG` | `0` | Enable Playwright Inspector |# Pretty print with jq

| `HEADLESS` | `0` | Run in headless mode |tail -f e2e/e2e-events.log | jq '.'

| `MCP_INGEST_URL` | `http://localhost:8000/ingest` | MCP server endpoint |```

| `MCP_API_KEY` | - | API key for MCP authentication |

---

## 📸 Screenshots

## MCP Server Integration (Optional Advanced Setup)

Automatically captured at key points:

- `test-screenshots/1-landing-page.png`### Prerequisites

- `test-screenshots/6-agent-builder-panel.png`

- `test-screenshots/7-prompts-panel.png`1. **Install MCP Server Package** (choose one):

- etc.

```bash

Total: ~20+ screenshots per run# Option A: GitHub Agent HQ

npm install -g @github/agent-hq-mcp-server

## 🤖 MCP Integration (Optional)

# Option B: Custom MCP server

For AI-powered test analysis and feedback:# (depends on your organization's setup)

```

### Start MCP Forwarder

2. **Start MCP Forwarder**:

```bash

# Default```bash

node mcp-forwarder.js# Default: forwards to http://localhost:8000/ingest

node e2e/mcp-forwarder.js

# With custom endpoint

MCP_INGEST_URL=https://your-mcp.com/ingest node mcp-forwarder.js# Custom endpoint

MCP_INGEST_URL=https://your-mcp-server.com/api/ingest node e2e/mcp-forwarder.js

# With authentication

MCP_API_KEY=secret node mcp-forwarder.js# With API key authentication

```MCP_API_KEY=your-secret-key MCP_INGEST_URL=https://mcp.example.com/ingest node e2e/mcp-forwarder.js

```

### Configure VS Code

3. **Configure VS Code** (already done in `.vscode/settings.json`):

Edit `.vscode/settings.json`:

```jsonUncomment and update these lines:

{```json

  "copilot.agent.mcp.endpoint": "http://localhost:8000/agent-mcp",{

  "copilot.agent.mcp.apiKey": "${env:MCP_API_KEY}"  "copilot.agent.mcp.endpoint": "http://localhost:8000/agent-mcp",

}  "copilot.agent.mcp.apiKey": "${env:MCP_API_KEY}"

```}

```

## 🐛 Debugging

### MCP Forwarder Features

### Inspector Mode Features

The `mcp-forwarder.js` script:

1. **Pause at breakpoints** - Test pauses, press Enter to continue- ✅ Watches `e2e-events.log` for changes

2. **Selector Playground** - Test and refine element selectors- ✅ Forwards events to MCP server via HTTP/HTTPS POST

3. **Step-by-step execution** - Click through each action- ✅ Supports API key authentication

4. **DevTools integration** - Inspect page state live- ✅ Handles connection errors gracefully

- ✅ Tracks file position to avoid duplicate events

### Common Issues- ✅ Auto-reconnects on network failures



**Issue:** Tests fail on model selection  ### Running Tests with MCP

**Solution:** Increase timeout in `safeClick` (currently 3s)

```bash

**Issue:** Screenshots not capturing  # Terminal 1: Start MCP forwarder (if you have an MCP server)

**Solution:** Check `test-screenshots/` directory permissionsMCP_INGEST_URL=http://localhost:8000/ingest node e2e/mcp-forwarder.js



**Issue:** PWDEBUG not working  # Terminal 2: Run tests with inspector

**Solution:** Ensure `PWDEBUG=1` is set before running./e2e/run-with-inspector.sh

```

## 📖 Best Practices (from PDF)

---

1. ✅ **Use Copilot Agent Mode** to generate/refactor test scripts

2. ✅ **Run tests locally** with `--headed --debug`## What is MCP (Model Context Protocol)?

3. ✅ **Connect to MCP** for structured feedback (optional)

4. ✅ **Visual supervision** with Playwright InspectorMCP allows your AI assistant to get structured JSON feedback from test runs:

- **Pass/fail status** for each test action

## 🔗 Related Documentation- **Screenshots** captured during tests (with file paths)

- **Error logs** with stack traces

- [MCP_SETUP_GUIDE.md](./MCP_SETUP_GUIDE.md) - Complete MCP integration guide- **Model learns** from failures and adjusts intelligently

- [Playwright Docs](https://playwright.dev) - Official Playwright documentation- **Timestamps** for performance analysis

- [LibreChat Docs](https://docs.librechat.ai) - LibreChat documentation

### Benefits of MCP Integration

## 🆘 Support

✅ **Structured Feedback**: JSON responses instead of parsing terminal output  

For issues or questions:✅ **Screenshot Analysis**: AI can analyze visual failures  

1. Check `e2e-events.log` for detailed event history✅ **Smart Retries**: Model learns from failures and adjusts selectors  

2. Review screenshots in `test-screenshots/`✅ **Better Debugging**: Stack traces linked to code locations  

3. Run with `PWDEBUG=1` for step-by-step debugging✅ **Historical Data**: Track test reliability over time  

4. Review MCP_SETUP_GUIDE.md for advanced configuration✅ **Agent Autonomy**: LLM can request reruns and analyze patterns  



------

**Implementation Based On:** Playwright Inspector + MCP Setup For LibreChat E2E (PDF Document)  
**Status:** ✅ All components from PDF implemented and ready to use
