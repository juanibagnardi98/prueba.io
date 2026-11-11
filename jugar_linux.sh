#!/bin/bash
# Lanzador para Linux (Ubuntu, Debian, Fedora, Arch, etc.)
cd "$(dirname "$0")"
echo "======================================================"
echo "    🐉 ZODIAC RACING - INICIANDO EN LINUX 🏁"
echo "======================================================"

if command -v google-chrome &> /dev/null; then
    google-chrome --app="file://$(pwd)/index.html" &
elif command -v chromium-browser &> /dev/null; then
    chromium-browser --app="file://$(pwd)/index.html" &
elif command -v chromium &> /dev/null; then
    chromium --app="file://$(pwd)/index.html" &
elif command -v firefox &> /dev/null; then
    firefox index.html &
elif command -v xdg-open &> /dev/null; then
    xdg-open index.html &
else
    echo "Abre index.html en cualquier navegador web."
fi
