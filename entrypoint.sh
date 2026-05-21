#!/bin/sh
# -------------------------------------------------
# Nova Browser Docker entrypoint
# -------------------------------------------------
rm -f /tmp/.X99-lock

# 1️⃣ Xvfb
Xvfb :99 -screen 0 1280x1024x24 &
XVFB_PID=$!
while [ ! -S /tmp/.X11-unix/X99 ]; do sleep 0.1; done

# 2️⃣ VNC
x11vnc -display :99 -nopw -forever -listen 0.0.0.0 -noxdamage &
XVNC_PID=$!

# 3️⃣ Websockify (noVNC)
export LIBGL_ALWAYS_SOFTWARE=1
websockify --web /usr/share/novnc 0.0.0.0:6080 localhost:5900 &
WEBSOCKIFY_PID=$!

# 4️⃣ Qt software rendering (critical!)
export QT_QUICK_BACKEND=software
export QT_OPENGL=software   # disables GLX/EGL completely

# 5️⃣ Run the app
python3 /app/main.py