#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZODIAC RACING 2D - Servidor Local Multiplataforma (Android y Windows)
Permite jugar en Windows y conectar celulares Android en la misma red Wi-Fi
mediante Código QR o enlace directo.
"""

import os
import sys
import io
import json
import socket
import threading
import webbrowser
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer

# Intentar importar qrcode para terminal y SVG
QRCODE_AVAILABLE = False
try:
    import qrcode
    from qrcode.image.svg import SvgImage
    QRCODE_AVAILABLE = True
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent

def get_local_ip():
    """Obtiene la dirección IP local de la computadora en la red Wi-Fi / LAN"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def find_available_port(start_port=8000, max_attempts=25):
    """Busca un puerto libre a partir de start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    return start_port

LOCAL_IP = get_local_ip()
PORT = find_available_port(8000)
SERVER_URL = f"http://{LOCAL_IP}:{PORT}"
LOCAL_URL = f"http://localhost:{PORT}"

class ZodiacGameHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def end_headers(self):
        # Habilitar CORS y evitar problemas de caché en desarrollo
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_GET(self):
        # Endpoint de información de red para el frontend
        if self.path == '/api/info':
            payload = json.dumps({
                "local_ip": LOCAL_IP,
                "port": PORT,
                "url": SERVER_URL,
                "local_url": LOCAL_URL,
                "qrcode_available": QRCODE_AVAILABLE
            }).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # Endpoint de Código QR en formato SVG
        if self.path == '/api/qr.svg':
            if QRCODE_AVAILABLE:
                qr = qrcode.QRCode(image_factory=SvgImage, border=1)
                qr.add_data(SERVER_URL)
                img = qr.make_image()
                buf = io.BytesIO()
                img.save(buf)
                svg_data = buf.getvalue()
                self.send_response(200)
                self.send_header('Content-Type', 'image/svg+xml')
                self.send_header('Content-Length', str(len(svg_data)))
                self.end_headers()
                self.wfile.write(svg_data)
                return
            else:
                self.send_response(404)
                self.end_headers()
                return

        # Redirigir la raíz al juego principal si index.html no existe
        if self.path == '/' or self.path == '/index.html':
            target = BASE_DIR / 'index.html'
            if not target.exists():
                fallback = BASE_DIR / 'Zodiac_Racing_2D_calendario_animales.html'
                if fallback.exists():
                    self.path = '/Zodiac_Racing_2D_calendario_animales.html'

        return super().do_GET()

    def guess_type(self, path):
        # Asegurar tipos MIME correctos para PWA
        if path.endswith('.webmanifest') or path.endswith('manifest.json'):
            return 'application/manifest+json'
        if path.endswith('.svg'):
            return 'image/svg+xml'
        if path.endswith('.js'):
            return 'application/javascript; charset=utf-8'
        return super().guess_type(path)

    def log_message(self, format, *args):
        # Silenciar logs ruidosos de archivos estáticos individuales
        first_arg = args[0] if args else ''
        if any(ext in first_arg for ext in ['.png', '.svg', '.ico', '/api/']):
            return
        super().log_message(format, *args)

def print_banner():
    width = 68
    print("\n" + "=" * width)
    print(" 🐉  ZODIAC RACING 2D - SERVIDOR PARA ANDROID Y WINDOWS  🏁 ".center(width))
    print("=" * width)
    print(f" * PC (Windows):            {LOCAL_URL}")
    print(f" * Celular Android (Wi-Fi): {SERVER_URL}")
    print("=" * width)

    if QRCODE_AVAILABLE:
        print("\n [!] ESCANEA ESTE CÓDIGO QR CON LA CÁMARA DE TU CELULAR ANDROID:\n")
        try:
            qr = qrcode.QRCode(border=1)
            qr.add_data(SERVER_URL)
            qr.print_ascii(invert=True)
        except Exception:
            pass
        print("")

    print(" INSTRUCCIONES PARA ANDROID:")
    print(" 1. Asegúrate de que el celular esté conectado a tu misma red Wi-Fi.")
    print(f" 2. Abre Google Chrome o Firefox y ve a: {SERVER_URL}")
    print(" 3. Para instalarlo como App nativa en tu celular:")
    print("    Toca los 3 puntos (⋮) arriba a la derecha y pulsa:")
    print("    'Instalar aplicación' o 'Agregar a la pantalla principal'.")
    print("=" * width)
    print(" Presiona Ctrl + C en esta ventana para detener el servidor.\n")

def main():
    ThreadingTCPServer.allow_reuse_address = True
    with ThreadingTCPServer(('0.0.0.0', PORT), ZodiacGameHandler) as httpd:
        print_banner()

        # Abrir automáticamente en el navegador de Windows tras 1 segundo
        def open_browser():
            try:
                webbrowser.open(LOCAL_URL)
            except Exception:
                pass
        threading.Timer(0.8, open_browser).start()

        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nDeteniendo servidor... ¡Gracias por jugar a Zodiac Racing 2D!\n")
            httpd.server_close()

if __name__ == '__main__':
    main()
