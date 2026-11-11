#!/bin/bash
# Iniciar Servidor para macOS (Doble clic en Finder)
cd "$(dirname "$0")"
echo "=========================================================="
echo "  🐉 ZODIAC RACING - SERVIDOR MULTIPLATAFORMA (MACOS) 🏁"
echo "=========================================================="
echo "Iniciando servidor local y multijugador..."

if command -v python3 &> /dev/null; then
    python3 server.py
elif command -v python &> /dev/null; then
    python server.py
else
    echo "[ERROR] Python no está instalado en este sistema macOS."
    echo "Puedes abrir directamente JUGAR_MAC.command para jugar localmente."
    read -p "Presiona Enter para cerrar..."
fi
