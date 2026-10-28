#!/usr/bin/env bash
# Start the AGY Web Terminal on port 7681
set -e

PORT="${PORT:-7681}"

echo "=========================================================="
echo "  🚀 Starting AGY Web Terminal on port $PORT"
echo "  Access this terminal from any browser or mobile device!"
echo "=========================================================="

if [ -n "$WEB_TERMINAL_PASSWORD" ]; then
  echo "Basic auth enabled: User: admin"
  exec ttyd -p "$PORT" -W -c "admin:${WEB_TERMINAL_PASSWORD}" agy
else
  exec ttyd -p "$PORT" -W agy
fi
