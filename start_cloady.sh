#!/bin/bash
cd "$(dirname "$0")"
echo "Starting health server..."
python3 -m http.server "${SERVER_PORT:-3000}" > /dev/null 2>&1 &
echo "Starting POT Provider..."
if command -v node > /dev/null 2>&1 && [ -f pot-provider/server/build/main.js ]; then
  (cd pot-provider/server && node build/main.js > /dev/null 2>&1 &)
fi
echo "Starting SHUKLAMUSIC Bot..."
python3 -m SHUKLAMUSIC
