#!/bin/bash
# uninstall.sh — полное удаление SCPL для Linux/macOS

set -e

INSTALL_DIR="$HOME/.local/share/scpl"
BIN_DIR="$HOME/.local/bin"
SCPL_CMD="$BIN_DIR/scpl"
CONFIG_DIR="$HOME/.config/scpl"
CACHE_DIR="$HOME/.cache/scpl"

echo "[SCPL] Uninstallation for Linux/macOS"

# Функция для удаления из shell конфигов
remove_from_shell_config() {
    local config_file="$1"
    if [ -f "$config_file" ]; then
        cp "$config_file" "${config_file}.scpl.bak"
        sed -i '/export PATH="$HOME\/.local\/bin:$PATH"/d' "$config_file"
        echo "✓ Cleaned $config_file (backup: ${config_file}.scpl.bak)"
    fi
}

# Удаляем основную директорию
if [ -d "$INSTALL_DIR" ]; then
    echo "Removing $INSTALL_DIR ..."
    rm -rf "$INSTALL_DIR"
    echo "✓ Main directory removed"
else
    echo "✗ Main directory not found"
fi

# Удаляем исполняемый файл
if [ -f "$SCPL_CMD" ]; then
    echo "Removing $SCPL_CMD ..."
    rm -f "$SCPL_CMD"
    echo "✓ Executable removed"
fi

# Удаляем конфиги
if [ -d "$CONFIG_DIR" ]; then
    echo "Removing $CONFIG_DIR ..."
    rm -rf "$CONFIG_DIR"
    echo "✓ Config directory removed"
fi

# Удаляем кэш
if [ -d "$CACHE_DIR" ]; then
    echo "Removing $CACHE_DIR ..."
    rm -rf "$CACHE_DIR"
    echo "✓ Cache directory removed"
fi

# Удаляем из shell конфигов
remove_from_shell_config "$HOME/.bashrc"
remove_from_shell_config "$HOME/.zshrc"
remove_from_shell_config "$HOME/.profile"
remove_from_shell_config "$HOME/.bash_profile"

# Удаляем пустую директорию bin
if [ -d "$BIN_DIR" ] && [ -z "$(ls -A "$BIN_DIR")" ]; then
    echo "Removing empty $BIN_DIR ..."
    rmdir "$BIN_DIR" 2>/dev/null || true
fi

echo ""
echo "[SCPL] Uninstallation complete!"
echo ""
echo "Removed:"
echo "  - $INSTALL_DIR"
echo "  - $SCPL_CMD"
echo "  - $CONFIG_DIR"
echo "  - $CACHE_DIR"
echo ""
echo "Backup files created:"
echo "  - ~/.bashrc.scpl.bak"
echo "  - ~/.zshrc.scpl.bak (if existed)"
echo ""
echo "To finish cleanup:"
echo "  source ~/.bashrc  # or restart terminal" 
