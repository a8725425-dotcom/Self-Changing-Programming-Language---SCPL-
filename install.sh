#!/bin/bash
# install.sh — установка SCPL с опциональным добавлением в PATH

set -e

REPO="a8725425-dotcom/Self-Changing-Programming-Language---SCPL-"
INSTALL_DIR="$HOME/.local/share/scpl"
BIN_DIR="$HOME/.local/bin"
SCPL_CMD="$BIN_DIR/scpl"

echo "[SCPL] Installing files to $INSTALL_DIR ..."

# 1. Создаём директории
mkdir -p "$INSTALL_DIR"
mkdir -p "$BIN_DIR"

# 2. Скачиваем файлы
echo "[SCPL] Downloading from GitHub..."
if ! curl -L "https://github.com/$REPO/archive/refs/heads/main.tar.gz" | tar xz -C "$INSTALL_DIR" --strip-components=1; then
    echo "[SCPL] Error: Failed to download or extract files"
    exit 1
fi

# 3. Делаем cli исполняемым
chmod +x "$INSTALL_DIR/scpl_cli.py"

# 4. Проверяем, есть ли python3
if ! command -v python3 &> /dev/null; then
    echo "[SCPL] Error: python3 not found. Please install Python 3 first."
    exit 1
fi

# 5. Спрашиваем про PATH
echo ""
echo "Добавить CLI в PATH для быстрого доступа (команда 'scpl')?"
echo "  1) Да (рекомендуется)"
echo "  2) Нет, буду запускать через python3"
read -p "Выберите (1/2): " choice

case $choice in
    2)
        echo ""
        echo "[SCPL] Установка завершена без добавления в PATH."
        echo "Запуск: python3 $INSTALL_DIR/scpl_cli.py repl"
        echo ""
        echo "Алиас (временный, на сессию): alias scpl='python3 $INSTALL_DIR/scpl_cli.py'"
        ;;
    *)
        # Создаём скрипт-обёртку
        cat > "$SCPL_CMD" << EOF
#!/bin/bash
exec python3 "$INSTALL_DIR/scpl_cli.py" "\$@"
EOF
        chmod +x "$SCPL_CMD"
        
        # Добавляем .local/bin в PATH, если ещё не добавлен
        if [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.bashrc"
            echo 'export PATH="$HOME/.local/bin:$PATH"' >> "$HOME/.zshrc" 2>/dev/null || true
            export PATH="$HOME/.local/bin:$PATH"
        fi
        
        echo ""
        echo "[SCPL] Установка завершена! Команда 'scpl' добавлена в PATH."
        echo "Запуск: scpl repl"
        echo ""
        echo "Примечание: если 'scpl' не найден — перезапустите терминал или выполните:"
        echo "  source ~/.bashrc  (для bash)"
        echo "  source ~/.zshrc   (для zsh)"
        ;;
esac

echo ""
echo "Установленные файлы: $INSTALL_DIR"
