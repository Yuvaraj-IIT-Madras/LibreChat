#!/usr/bin/env bash
# run-tests.sh — run playwright test in headed debug mode
# requires playwright set up in project

# ensure browsers are installed
npx playwright install --with-deps

# run headed test suite with Playwright inspector enabled
PWDEBUG=1 npx playwright test --headed "$@"
