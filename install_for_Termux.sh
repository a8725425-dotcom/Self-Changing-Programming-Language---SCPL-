#!/bin/bash
# install_for_Termux.sh — установка SCPL для Termux (Android)

set -e

REPO="a8725425-dotcom/Self-Changing-Programming-Language---SCPL-"
INSTALL_DIR="$HOME/.local/share/scpl"
BIN_DIR="$HOME/.local/bin"
SCPL_CMD="$BIN_DIR/scpl"

echo "[SCPL] Termux installation"

# Проверяем/устанавливаем Python
if ! command -v python3 &> /dev/null; then
    echo "[SCPL] Python3 not found. Installing..."
    pkg update -y && pkg install python -y
fi

echo "[SCPL] Installing files to $INSTALL_DIR ..."

mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

echo "[SCPL] Downloading from GitHub..."
curl -L "https://github.com/$REPO/archive/refs/heads/main.tar.gz" | tar xz -C "$INSTALL_DIR" --strip-components=1

chmod +x "$INSTALL_DIR/scpl_cli.py"

# Создаём скрипт-обёртку
cat > "$SCPL_CMD" << EOF
#!/bin/bash
exec python3 "$INSTALL_DIR/scpl_cli.py" "\$@"
EOF

chmod +x "$SCPL_CMD"

# Добавляем .local/bin в PATH для Termux (если ещё не добавлено)
if ! grep -q ".local/bin" "$HOME/.bashrc"; then
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
fi

# Добавляем в текущую сессию
export PATH="$HOME/.local/bin:$PATH"

echo ""
echo "[SCPL] Установка завершена!"
echo "Запуск: scpl repl"
echo ""
echo "Если команда не найдена — перезапустите Termux или выполните:"
echo "  source ~/.bashrc"
