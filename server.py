#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ZODIAC RACING 2D - Servidor Multiplataforma con Soporte Multijugador en Tiempo Real
- Servidor HTTP (Puerto 8000): Sirve el juego, PWA, iconos y assets.
- Servidor WebSocket (Puerto 8001): Salas multijugador para 1 a 4 jugadores (humanos o IAs).
Compatible con Windows y Android a través de red local (Wi-Fi) o cualquier IP configurada.
"""

import os
import sys
import io
import json
import socket
import random
import string
import threading
import asyncio
import webbrowser
from pathlib import Path
from http.server import SimpleHTTPRequestHandler
from socketserver import ThreadingTCPServer

# Soporte para WebSockets
try:
    import websockets
    from websockets.asyncio.server import serve as ws_serve
    WEBSOCKETS_AVAILABLE = True
except ImportError:
    WEBSOCKETS_AVAILABLE = False

# Soporte opcional de qrcode
QRCODE_AVAILABLE = False
try:
    import qrcode
    from qrcode.image.svg import SvgImage
    QRCODE_AVAILABLE = True
except ImportError:
    pass

BASE_DIR = Path(__file__).resolve().parent

def get_local_ip():
    """Detecta la IP local de la máquina en la red Wi-Fi o Ethernet"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        ip = s.getsockname()[0]
    except Exception:
        ip = '127.0.0.1'
    finally:
        s.close()
    return ip

def find_available_port(start_port, max_attempts=25):
    """Busca el primer puerto libre a partir de start_port"""
    for port in range(start_port, start_port + max_attempts):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('0.0.0.0', port))
                return port
            except OSError:
                continue
    return start_port

LOCAL_IP = get_local_ip()
HTTP_PORT = find_available_port(8000)
WS_PORT = find_available_port(8001 if HTTP_PORT != 8001 else 8002)

SERVER_HTTP_URL = f"http://{LOCAL_IP}:{HTTP_PORT}"
SERVER_WS_URL = f"ws://{LOCAL_IP}:{WS_PORT}"
LOCAL_HTTP_URL = f"http://localhost:{HTTP_PORT}"
LOCAL_WS_URL = f"ws://localhost:{WS_PORT}"

# =====================================================================
# GESTIÓN DE SALAS MULTIJUGADOR (WEBSOCKETS)
# =====================================================================
# Estructura: rooms[room_code] = RoomInstance
rooms = {}
rooms_lock = threading.Lock()

def generate_room_code():
    chars = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
    while True:
        code = "".join(random.choice(chars) for _ in range(4))
        if code not in rooms:
            return code

class Room:
    def __init__(self, code, host_ws, host_info):
        self.code = code
        self.host_ws = host_ws
        self.state = "lobby"  # lobby, countdown, racing, finished
        self.track_seed = random.randint(1000, 999999)
        self.track_length = 1000
        # 4 slots para jugadores
        self.slots = [None, None, None, None]
        self.slots[0] = {
            "name": host_info.get("name", "Corredor 1"),
            "character": host_info.get("character", {}),
            "is_ai": False,
            "ws": host_ws,
            "ready": True
        }

    def to_dict(self):
        return {
            "code": self.code,
            "state": self.state,
            "track_seed": self.track_seed,
            "track_length": self.track_length,
            "slots": [
                {
                    "slot": idx,
                    "name": s["name"],
                    "character": s["character"],
                    "is_ai": s["is_ai"],
                    "occupied": True
                } if s is not None else {
                    "slot": idx,
                    "occupied": False
                }
                for idx, s in enumerate(self.slots)
            ]
        }

    def get_sockets(self):
        return [s["ws"] for s in self.slots if s is not None and s.get("ws") is not None]

async def broadcast_room(room, message_dict):
    payload = json.dumps(message_dict)
    sockets = room.get_sockets()
    for ws in sockets:
        try:
            await ws.send(payload)
        except Exception:
            pass

async def handle_ws_client(websocket):
    current_room_code = None
    player_slot = None

    try:
        async for raw_message in websocket:
            try:
                data = json.loads(raw_message)
            except json.JSONDecodeError:
                continue

            msg_type = data.get("type")

            # 1. PING para medir latencia y probar conexión
            if msg_type == "ping":
                await websocket.send(json.dumps({"type": "pong", "time": data.get("time", 0)}))
                continue

            # 2. CREAR SALA
            if msg_type == "create_room":
                with rooms_lock:
                    code = generate_room_code()
                    room = Room(code, websocket, data)
                    rooms[code] = room
                    current_room_code = code
                    player_slot = 0

                await websocket.send(json.dumps({
                    "type": "room_joined",
                    "code": code,
                    "slot": 0,
                    "is_host": True,
                    "room": room.to_dict()
                }))
                continue

            # 3. UNIRSE A SALA
            if msg_type == "join_room":
                code = str(data.get("code", "")).strip().upper()
                with rooms_lock:
                    room = rooms.get(code)
                    if not room:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": f"Sala '{code}' no encontrada."
                        }))
                        continue

                    if room.state != "lobby":
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "La carrera en esta sala ya ha comenzado."
                        }))
                        continue

                    # Buscar slot libre
                    free_slot = None
                    for idx in range(4):
                        if room.slots[idx] is None:
                            free_slot = idx
                            break

                    if free_slot is None:
                        await websocket.send(json.dumps({
                            "type": "error",
                            "message": "La sala ya está llena (máximo 4 jugadores)."
                        }))
                        continue

                    room.slots[free_slot] = {
                        "name": data.get("name", f"Corredor {free_slot + 1}"),
                        "character": data.get("character", {}),
                        "is_ai": False,
                        "ws": websocket,
                        "ready": True
                    }
                    current_room_code = code
                    player_slot = free_slot

                await websocket.send(json.dumps({
                    "type": "room_joined",
                    "code": code,
                    "slot": free_slot,
                    "is_host": False,
                    "room": room.to_dict()
                }))

                # Notificar a todos en la sala del nuevo integrante
                await broadcast_room(room, {
                    "type": "room_updated",
                    "room": room.to_dict()
                })
                continue

            # 4. CONFIGURAR / RELLENAR CON IA (Solo Anfitrión)
            if msg_type == "set_slot_ai":
                slot_idx = data.get("slot")
                enable_ai = data.get("enable", True)
                ai_info = data.get("ai_info", {})

                with rooms_lock:
                    room = rooms.get(current_room_code)
                    if room and room.host_ws == websocket and 0 < slot_idx < 4:
                        if enable_ai:
                            room.slots[slot_idx] = {
                                "name": ai_info.get("name", f"IA Bot {slot_idx + 1}"),
                                "character": ai_info.get("character", {}),
                                "is_ai": True,
                                "ws": None,
                                "ready": True
                            }
                        else:
                            room.slots[slot_idx] = None

                if room:
                    await broadcast_room(room, {
                        "type": "room_updated",
                        "room": room.to_dict()
                    })
                continue

            # 5. INICIAR CARRERA (Solo Anfitrión)
            if msg_type == "start_race":
                with rooms_lock:
                    room = rooms.get(current_room_code)
                    if room and room.host_ws == websocket:
                        room.state = "racing"
                        room.track_seed = random.randint(1000, 999999)

                if room:
                    await broadcast_room(room, {
                        "type": "race_started",
                        "seed": room.track_seed,
                        "track_length": room.track_length,
                        "room": room.to_dict()
                    })
                continue

            # 6. ACTUALIZACIÓN DE POSICIÓN EN CARRERA (Retransmisión a los demás)
            if msg_type == "race_update":
                room = rooms.get(current_room_code)
                if room and room.state == "racing":
                    payload = json.dumps({
                        "type": "player_moved",
                        "slot": player_slot,
                        "x": data.get("x", 0),
                        "lane": data.get("lane", 0),
                        "speed": data.get("speed", 0),
                        "powerActive": data.get("powerActive", False),
                        "nitroActive": data.get("nitroActive", False)
                    })
                    for ws in room.get_sockets():
                        if ws != websocket:
                            try:
                                await ws.send(payload)
                            except Exception:
                                pass
                continue

            # 7. ACTUALIZACIÓN DE BOTS IA POR PARTE DEL HOST
            if msg_type == "ai_update":
                room = rooms.get(current_room_code)
                if room and room.host_ws == websocket and room.state == "racing":
                    payload = json.dumps({
                        "type": "player_moved",
                        "slot": data.get("slot"),
                        "x": data.get("x", 0),
                        "lane": data.get("lane", 0),
                        "speed": data.get("speed", 0),
                        "powerActive": data.get("powerActive", False),
                        "nitroActive": data.get("nitroActive", False)
                    })
                    for ws in room.get_sockets():
                        if ws != websocket:
                            try:
                                await ws.send(payload)
                            except Exception:
                                pass
                continue

            # 8. JUGADOR O BOT CRUZA LA META
            if msg_type == "player_finish":
                room = rooms.get(current_room_code)
                if room:
                    finish_slot = data.get("slot", player_slot)
                    finish_time = data.get("time", 0)
                    await broadcast_room(room, {
                        "type": "player_finished",
                        "slot": finish_slot,
                        "time": finish_time
                    })
                continue

    except Exception:
        pass
    finally:
        # Limpieza cuando un jugador se desconecta
        if current_room_code:
            with rooms_lock:
                room = rooms.get(current_room_code)
                if room:
                    if room.host_ws == websocket:
                        # Si se va el anfitrión, cerramos la sala
                        rooms.pop(current_room_code, None)
                        await broadcast_room(room, {
                            "type": "error",
                            "message": "El anfitrión ha cerrado la sala."
                        })
                    else:
                        # Si se va un cliente, liberamos su slot
                        if player_slot is not None and 0 <= player_slot < 4:
                            room.slots[player_slot] = None
                        await broadcast_room(room, {
                            "type": "room_updated",
                            "room": room.to_dict()
                        })

# =====================================================================
# SERVIDOR HTTP (ESTÁTICOS + PWA + API)
# =====================================================================
class ZodiacGameHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(BASE_DIR), **kwargs)

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_GET(self):
        # Endpoint de información de red para el cliente
        if self.path == '/api/info':
            payload = json.dumps({
                "local_ip": LOCAL_IP,
                "http_port": HTTP_PORT,
                "ws_port": WS_PORT,
                "http_url": SERVER_HTTP_URL,
                "ws_url": SERVER_WS_URL,
                "local_ws_url": LOCAL_WS_URL,
                "qrcode_available": QRCODE_AVAILABLE,
                "websockets_available": WEBSOCKETS_AVAILABLE
            }).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json; charset=utf-8')
            self.send_header('Content-Length', str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        # Endpoint de Código QR en SVG
        if self.path == '/api/qr.svg':
            if QRCODE_AVAILABLE:
                qr = qrcode.QRCode(image_factory=SvgImage, border=1)
                qr.add_data(SERVER_HTTP_URL)
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

        # Redirección a index.html
        if self.path == '/' or self.path == '/index.html':
            target = BASE_DIR / 'index.html'
            if not target.exists():
                fallback = BASE_DIR / 'Zodiac_Racing_2D_calendario_animales.html'
                if fallback.exists():
                    self.path = '/Zodiac_Racing_2D_calendario_animales.html'

        return super().do_GET()

    def guess_type(self, path):
        if path.endswith('.webmanifest') or path.endswith('manifest.json'):
            return 'application/manifest+json'
        if path.endswith('.svg'):
            return 'image/svg+xml'
        if path.endswith('.js'):
            return 'application/javascript; charset=utf-8'
        return super().guess_type(path)

    def log_message(self, format, *args):
        first_arg = args[0] if args else ''
        if any(ext in first_arg for ext in ['.png', '.svg', '.ico', '/api/']):
            return
        super().log_message(format, *args)

def print_banner():
    width = 72
    print("\n" + "=" * width)
    print(" 🐉  ZODIAC RACING 2D - PISTA RECTA MULTIJUGADOR 🏁 ".center(width))
    print("=" * width)
    print(f" * Web en PC (Windows):            {LOCAL_HTTP_URL}")
    print(f" * Web en Android (Mismo Wi-Fi):   {SERVER_HTTP_URL}")
    print(f" * Servidor WebSocket (Salas):     {SERVER_WS_URL} o {LOCAL_WS_URL}")
    print("=" * width)

    if QRCODE_AVAILABLE:
        print("\n [!] ESCANEA ESTE CÓDIGO QR CON LA CÁMARA DE TU CELULAR ANDROID:\n")
        try:
            qr = qrcode.QRCode(border=1)
            qr.add_data(SERVER_HTTP_URL)
            qr.print_ascii(invert=True)
        except Exception:
            pass
        print("")

    print(" MODOS DISPONIBLES:")
    print(" 1. Modo Local / Solo: Juega tú solo o contra 1 a 3 IAs sin conexión.")
    print(" 2. Modo Servidor en Red: 1 a 4 personas conectadas en tiempo real.")
    print(" 3. Se puede rellenar cualquier espacio vacío con IAs inteligentes.")
    print("=" * width)
    print(" Presiona Ctrl + C para detener los servidores.\n")

def start_websocket_server():
    """Inicia el servidor WebSocket en un hilo en segundo plano"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def run_server():
        async with ws_serve(handle_ws_client, "0.0.0.0", WS_PORT):
            await asyncio.Future()  # Corre indefinidamente

    try:
        loop.run_until_complete(run_server())
    except Exception as e:
        print(f"[Aviso WS] Error en servidor WebSocket: {e}")

def main():
    # 1. Iniciar hilo del servidor WebSocket si está disponible
    if WEBSOCKETS_AVAILABLE:
        ws_thread = threading.Thread(target=start_websocket_server, daemon=True)
        ws_thread.start()
    else:
        print("[Aviso] Módulo 'websockets' no disponible. El modo local/IA seguirá funcionando.")

    # 2. Iniciar servidor HTTP
    ThreadingTCPServer.allow_reuse_address = True
    with ThreadingTCPServer(('0.0.0.0', HTTP_PORT), ZodiacGameHandler) as httpd:
        print_banner()

        # Abrir automáticamente en el navegador de Windows tras 1 segundo
        def open_browser():
            try:
                webbrowser.open(LOCAL_HTTP_URL)
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
