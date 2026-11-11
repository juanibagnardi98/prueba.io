@echo off
title Zodiac Racing 2D - Windows
chcp 65001 >nul
cd /d "%~dp0"

echo ========================================================
echo     🐉 ZODIAC RACING 2D - INICIANDO EN WINDOWS 🏁
echo ========================================================
echo.

:: 1. Comprobar si Microsoft Edge existe para abrirlo en Modo Aplicación dedicado
if exist "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" (
    echo Abriendo en Modo Aplicacion nativa con Edge...
    start "" "C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe" --app="file:///%~dp0index.html"
    exit /b
)

if exist "C:\Program Files\Microsoft\Edge\Application\msedge.exe" (
    echo Abriendo en Modo Aplicacion nativa con Edge...
    start "" "C:\Program Files\Microsoft\Edge\Application\msedge.exe" --app="file:///%~dp0index.html"
    exit /b
)

:: 2. Comprobar si Google Chrome existe
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    echo Abriendo en Modo Aplicacion con Chrome...
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --app="file:///%~dp0index.html"
    exit /b
)

:: 3. Abrir en el navegador predeterminado de Windows
echo Abriendo en tu navegador predeterminado...
start "" "%~dp0index.html"
exit /b
