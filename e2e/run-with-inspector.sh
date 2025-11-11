#!/usr/bin/env bash
# run-with-inspector.sh — run your single-window runner with Playwright Inspector
# Usage: ./run-with-inspector.sh [--url http://localhost:3000]

export PWDEBUG=1

# Change to the e2e directory
cd "$(dirname "$0")"

# optionally pass through any args to node
node ./single_window_runner.js "$@"
