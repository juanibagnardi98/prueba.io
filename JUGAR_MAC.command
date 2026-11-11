#!/bin/bash
# Lanzador de Zodiac Racing para macOS (Doble clic en Finder)
cd "$(dirname "$0")"
echo "======================================================"
echo "    🐉 ZODIAC RACING - INICIANDO EN MACOS 🏁"
echo "======================================================"

if [ -d "/Applications/Google Chrome.app" ]; then
    echo "Abriendo en modo aplicación con Google Chrome..."
    open -na "Google Chrome" --args --app="file://$(pwd)/index.html"
elif [ -d "/Applications/Microsoft Edge.app" ]; then
    echo "Abriendo en modo aplicación con Microsoft Edge..."
    open -na "Microsoft Edge" --args --app="file://$(pwd)/index.html"
else
    echo "Abriendo en el navegador predeterminado..."
    open index.html
fi
