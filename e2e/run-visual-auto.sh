#!/usr/bin/env bash
# run-visual-auto.sh — run tests visually but automatically (no pause/F8 needed)
# The test runs with slowMo so you can see each action, but continues automatically

# Change to the e2e directory
cd "$(dirname "$0")"

# Run without PWDEBUG so no pause, but still headed with slowMo
node ./single_window_runner.js "$@"
