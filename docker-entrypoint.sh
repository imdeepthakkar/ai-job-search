#!/usr/bin/env bash
set -e

PORT="${PORT:-7681}"

echo "=========================================================="
echo " 🚀 AGY Cloud Terminal Daemon Running on Port $PORT"
echo "=========================================================="

TTYD_THEME='{"background": "#030712", "foreground": "#f0f6fc", "cursor": "#58a6ff", "selection": "rgba(47, 129, 247, 0.4)"}'

if [ -n "$TERMINAL_PASSWORD" ]; then
  echo "Security: Basic authentication enabled for user 'deept'"
  exec ttyd -p "$PORT" -W -t fontSize=14 -t fontFamily="JetBrains Mono, Fira Code, monospace" -t theme="$TTYD_THEME" -c "deept:${TERMINAL_PASSWORD}" agy
else
  exec ttyd -p "$PORT" -W -t fontSize=14 -t fontFamily="JetBrains Mono, Fira Code, monospace" -t theme="$TTYD_THEME" agy
fi
