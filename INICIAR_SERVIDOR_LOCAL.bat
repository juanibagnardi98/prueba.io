@echo off
title Zodiac Racing 2D - Servidor para Android y Windows
chcp 65001 >nul
cd /d "%~dp0"

echo ==========================================================
echo   🐉 ZODIAC RACING 2D - SERVIDOR ANDROID Y WINDOWS 🏁
echo ==========================================================
echo.
echo Iniciando servidor local...
python server.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [AVISO] Python no se pudo ejecutar directamente.
    echo Puedes abrir el juego en Windows directamente haciendo doble clic en:
    echo "JUGAR_WINDOWS.bat" o en "index.html"
    pause
)
