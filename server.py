from pathlib import Path
import zipfile, json

base = Path("/mnt/data/zodiac_racing_multiplayer")
html_path = base / "public" / "index.html"
server_path = base / "server.js"

html = html_path.read_text(encoding="utf-8")
html = html.replace(
    '<input id="roomPassword" type="password" maxlength="64" placeholder="Contraseña">',
    '<input id="roomPassword" type="password" value="1998" readonly aria-label="Contraseña fija de la sala">'
)
html = html.replace(
    'Escribe tu nombre y una contraseña para la sala.',
    'Escribe tu nombre. La contraseña de la sala es 1998.'
)
html_path.write_text(html, encoding="utf-8")

server = server_path.read_text(encoding="utf-8")
server = server.replace('const MAX_PLAYERS = 5;', 'const MAX_PLAYERS = 5;\nconst ROOM_PASSWORD = "1998";')
server = server.replace(
'''    if (typeof nickname !== "string" || !nickname.trim() ||
        typeof password !== "string" || password.length < 4 || password.length > 64) {
      return socket.emit("room:error", "Nombre requerido y contraseña de 4 a 64 caracteres.");
    }
    const code = makeCode();
    const salt = crypto.randomBytes(16);
    const room = { code, salt, passwordHash: passwordHash(password, salt), players: new Set() };''',
'''    if (typeof nickname !== "string" || !nickname.trim()) {
      return socket.emit("room:error", "Escribe un nombre para tu corredor.");
    }
    if (password !== ROOM_PASSWORD) {
      return socket.emit("room:error", "La contraseña fija de las salas es incorrecta.");
    }
    const code = makeCode();
    const salt = crypto.randomBytes(16);
    const room = { code, salt, passwordHash: passwordHash(ROOM_PASSWORD, salt), players: new Set() };'''
)
server = server.replace(
'''    if (typeof nickname !== "string" || !nickname.trim() ||
        typeof password !== "string" || password.length < 4 || password.length > 64) {
      return socket.emit("room:error", "Nombre requerido y contraseña de 4 a 64 caracteres.");
    }
    const supplied = passwordHash(password, room.salt);''',
'''    if (typeof nickname !== "string" || !nickname.trim()) {
      return socket.emit("room:error", "Escribe un nombre para tu corredor.");
    }
    const supplied = passwordHash(typeof password === "string" ? password : "", room.salt);'''
)
server_path.write_text(server, encoding="utf-8")

readme_path = base / "README.md"
readme = readme_path.read_text(encoding="utf-8")
readme = readme.replace(
    'salas privadas con código de 6 caracteres y contraseña.',
    'salas privadas con código de 6 caracteres y contraseña fija `1998`.'
)
readme = readme.replace(
    'Escribe tu nombre y una contraseña de al menos 4 caracteres y pulsa **CREAR SALA**.',
    'Escribe tu nombre (la contraseña fija es `1998`) y pulsa **CREAR SALA**.'
)
readme = readme.replace(
    'Los demás abren la dirección del servidor, crean su personaje, escriben el mismo código y contraseña y pulsan **UNIRSE A SALA**.',
    'Los demás abren la dirección del servidor, crean su personaje, escriben el mismo código (la contraseña ya está configurada como `1998`) y pulsan **UNIRSE A SALA**.'
)
readme += "\n\n**Contraseña compartida configurada:** `1998`. Cámbiala en `server.js` si más adelante quieres otra.\n"
readme_path.write_text(readme, encoding="utf-8")

