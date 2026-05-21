FROM debian:bookworm-slim

# Prevent interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive

# Install Python 3, PyQt6, QtWebEngine, Xvfb, VNC, noVNC, and all graphic library dependencies
RUN apt-get -o Acquire::Check-Valid-Until=false -o Acquire::Check-Date=false update && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-pyqt6 \
    python3-pyqt6.qtwebengine \
    python3-pyqt6.qtsvg \
    xvfb \
    x11vnc \
    novnc \
    python3-websockify \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install python requirements (excluding PyQt6 packages since they are handled natively by Debian)
COPY requirements.txt .
RUN sed -i '/[Pp]y[Qq]t6/d' requirements.txt && \
    pip3 install --no-cache-dir --break-system-packages -r requirements.txt

# Copy application source code
COPY . .

# Expose VNC and Web GUI port
EXPOSE 5900 6080

# Set environment variables for virtual framebuffer, Qt, and Chromium sandbox
ENV DISPLAY=:99
ENV QT_DEBUG_PLUGINS=1
ENV QTWEBENGINE_DISABLE_SANDBOX=1
ENV QTWEBENGINE_CHROMIUM_FLAGS="--no-sandbox --disable-gpu"
ENV LIBGL_ALWAYS_SOFTWARE=1
ENV QT_XCB_GL_INTEGRATION=none
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh
CMD ["sh","/app/entrypoint.sh"]
