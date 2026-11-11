# 🐉 ZODIAC RACING 2D - GUÍA PARA ANDROID Y WINDOWS 🏁

¡Tu juego **Zodiac Racing 2D** ya está 100% optimizado para ejecutarse en **Windows** y **Android**!

---

## 🎮 1. CÓMO JUGAR EN WINDOWS (PC)

Tienes 3 formas muy sencillas de jugarlo:

### Opción A (Recomendada - Modo Aplicación de Escritorio):
* Haz doble clic en el archivo **`JUGAR_WINDOWS.bat`**.
* Se abrirá automáticamente en una ventana de aplicación dedicada e independiente (sin barras de navegador ni pestañas molestas).

### Opción B (Directo en tu Navegador):
* Haz doble clic directamente en **`index.html`** o **`Zodiac_Racing_2D_calendario_animales.html`**.

### Opción C (Servidor Local con Conexión a Celular):
* Haz doble clic en **`INICIAR_SERVIDOR_LOCAL.bat`** (o ejecuta `python server.py`).
* Se abrirá en tu PC y te mostrará el Código QR para conectar tu celular.

---

## 📱 2. CÓMO JUGAR EN ANDROID

### Método 1: Conexión Instantánea por Wi-Fi con Código QR (¡El más rápido!)
1. Conecta tu celular Android a la **misma red Wi-Fi** que tu PC.
2. En tu PC, haz doble clic en **`INICIAR_SERVIDOR_LOCAL.bat`** (o ejecuta `python server.py`).
3. En la terminal de tu PC aparecerá un **Código QR**.
4. Abre la app de **Cámara** en tu celular Android y apunta al código QR en la pantalla de la PC (o abre Chrome en tu celular y escribe la dirección IP que te muestra, por ejemplo: `http://192.168.100.66:8000`).
5. ¡Listo! Ya estás jugando en Android con los controles táctiles en pantalla.

---

### Método 2: Instalarlo como App Nativa en Android (Funciona 100% Sin Internet)
El juego cuenta con tecnología **PWA (Progressive Web App)** con Service Worker:
1. Abre el juego en **Google Chrome** en tu Android (usando el Método 1).
2. Toca el menú de los **3 puntos (⋮)** en la esquina superior derecha de Chrome.
3. Elige la opción **"Instalar aplicación"** o **"Agregar a la pantalla principal"**.
4. Se creará un icono con el dragón de Zodiac Racing en el cajón de aplicaciones de tu celular.
5. Al abrirlo, se ejecuta a **pantalla completa**, sin barra de direcciones y **funciona incluso en modo avión (sin internet)**.

---

### Método 3: Generar un archivo instalador `.APK` (Opcional)
Si deseas generar un archivo instalador `.apk` para compartir:
* **Con PWABuilder (Sin programar):**
  1. Si subes la carpeta a un hosting gratuito (como GitHub Pages o Netlify).
  2. Ingresas en [pwabuilder.com](https://www.pwabuilder.com), colocas la URL y descargas el `.apk` listo para Android.
* **Con Capacitor (En tu PC):**
  Hemos dejado listos los archivos `package.json` y `capacitor.config.json`. En la terminal puedes ejecutar:
  ```bash
  npx @capacitor/cli add android
  npx @capacitor/cli open android
  ```
  Y compilar el `.apk` desde Android Studio.

---

## 🕹️ 3. CONTROLES DEL JUEGO

### En Windows (Teclado):
* **W** o **Flecha Arriba (↑):** Acelerar (Gas).
* **S** o **Flecha Abajo (↓):** Frenar / Marcha atrás.
* **A** o **Flecha Izquierda (←):** Girar hacia el carril interior.
* **D** o **Flecha Derecha (→):** Girar hacia el carril exterior.
* **Barra Espaciadora (Espacio):** Activar Poder Especial.

### En Android (Controles Táctiles Multi-touch):
Aparecen automáticamente en la parte inferior de la pantalla:
* **Cluster Izquierdo:**
  * Botón **◀ IZQ:** Cambia al carril interior.
  * Botón **DER ▶:** Cambia al carril exterior.
* **Centro:**
  * Botón **🔮 PODER:** Pulsa para activar el turbo zodiacal (muestra el contador de poderes disponibles).
* **Cluster Derecho:**
  * Botón **⚡ GAS:** Mantén presionado para acelerar a fondo.
  * Botón **🛑 FRENO:** Mantén presionado para desacelerar o frenar.

> **Multitáctil:** Puedes mantener presionado el botón **⚡ GAS** con el pulgar derecho mientras giras con los botones **◀ / ▶** con el pulgar izquierdo al mismo tiempo.

---

## ✨ 4. NOVEDADES Y MEJORAS INCLUIDAS

1. **Físicas de Conducción Corregidas:**
   * Ahora al acelerar el corredor avanza automáticamente a lo largo de la pista en el sentido de la carrera.
   * El giro lateral permite navegar entre carriles para recoger los potenciadores.
   * Si te sales de la pista hacia el césped, la fricción te frenará y soltará partículas de hierba.
2. **Audio Sintetizado:**
   * Efectos de sonido integrados para aceleración, recolectar nitros, recoger poderes, activación de turbo y fanfarria de victoria (sin necesidad de archivos MP3 externos).
   * Botón para silenciar o activar sonido en cualquier momento.
3. **Respuesta Háptica (Vibración):**
   * En celulares Android, el dispositivo vibra al recoger poderes, al usar nitro y al ganar la carrera.
4. **Pantalla Completa:**
   * Botón `⛶ Pantalla Completa` para una inmersión total en celulares y laptops.
5. **Generador de QR Integrado:**
   * Botón `📲 Jugar en Android` en el juego para mostrar el código QR en la pantalla de la PC y escanearlo con el móvil.
