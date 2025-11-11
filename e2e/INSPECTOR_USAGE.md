# 🔍 Playwright Inspector Usage Guide

## Quick Start

```bash
cd /home/yuvaraj/Projects/LibreChat/e2e
./run-with-inspector.sh
```

## What You'll See

### 1. Two Windows Open

- **Browser Window**: Initially shows `about:blank` - this is normal!
- **Playwright Inspector Window**: Separate UI with code view and debugging controls

### 2. Test Starts Paused

The test is **paused at the first breakpoint** waiting for you to continue.

You'll see in the Inspector:
- **Top section**: Your test code with current line highlighted
- **Bottom section**: "Navigate to '/' (http://localhost:3080)" - this is the NEXT action waiting

## How to Run the Test

### ▶️ Resume Execution

**Click the green "Resume" button** in the Inspector toolbar (top-left area)

OR

**Press F8** on your keyboard

The test will then:
1. Navigate browser to `http://localhost:3080`
2. Execute all 33 test steps
3. Pause at the next breakpoint (if any)

### 🎯 Step-by-Step Execution

**Press F10** to execute ONE action at a time

Useful when you want to see each step slowly.

### ⏸️ Pause Anytime

Click the **Pause** button to stop execution at the current action.

## Inspector Controls Reference

| Control | Keyboard | Action |
|---------|----------|--------|
| Resume | F8 | Continue to next breakpoint |
| Step Over | F10 | Execute next action only |
| Pause | - | Stop at current point |
| Record | - | Start recording new actions |

## Understanding the Display

### Code View (Top)
- Shows your `single_window_runner.js` file
- Yellow highlight = current paused line
- Green checkmark = completed action

### Action Panel (Bottom)
- **Locator tab**: Shows upcoming actions
- **Log tab**: Execution history
- **Call Stack**: Where you are in the code

## Common Issues

### "Browser shows about:blank"
✅ **This is normal!** The test is paused BEFORE navigation. Click Resume (F8) to continue.

### "Inspector didn't open"
❌ Check that you ran `./run-with-inspector.sh` (not `node single_window_runner.js`)

### "Test stopped after I closed browser"
❌ Don't close the browser manually! Use Inspector controls instead.

## Event Logging

All test actions are logged to `e2e-events.log` in NDJSON format:

```bash
# Watch events in real-time
tail -f e2e-events.log | jq
```

Each event includes:
- `ts`: Timestamp
- `kind`: Event type (action.start, action.end, etc.)
- `payload`: Event details

## Next Steps

1. ✅ Click **Resume (F8)** to run your first test
2. Watch the browser execute all 33 test steps
3. Review the event log: `cat e2e-events.log | jq`
4. Check screenshots in `test-screenshots/` folder

## Tips

- **Slow down tests**: They run with 100ms delay between actions (slowMo)
- **DevTools**: Browser DevTools are open automatically - use for element inspection
- **Screenshots**: Taken automatically on errors
- **Debug specific steps**: Add `await page.pause()` in code where you want to stop

---

**Happy Testing! 🚀**
