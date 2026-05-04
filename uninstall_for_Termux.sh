#!/bin/bash
# uninstall_for_Termux.sh — полное удаление SCPL для Termux

set -e

INSTALL_DIR="$HOME/.local/share/scpl"
BIN_DIR="$HOME/.local/bin"
SCPL_CMD="$BIN_DIR/scpl"
LIBS_DIR="$INSTALL_DIR/libs"

echo "[SCPL] Termux uninstallation"

# Удаляем главную директорию SCPL
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
else
    echo "✗ Executable not found"
fi

# Опционально: удаляем пустую директорию bin
if [ -d "$BIN_DIR" ] && [ -z "$(ls -A "$BIN_DIR")" ]; then
    echo "Removing empty $BIN_DIR ..."
    rmdir "$BIN_DIR" 2>/dev/null || true
fi

# Удаляем из PATH в .bashrc
if [ -f "$HOME/.bashrc" ]; then
    # Создаём бэкап
    cp "$HOME/.bashrc" "$HOME/.bashrc.scpl.bak"
    # Удаляем строки с .local/bin
    sed -i '/export PATH="$HOME\/.local\/bin:$PATH"/d' "$HOME/.bashrc"
    echo "✓ PATH entries removed from .bashrc (backup saved as .bashrc.scpl.bak)"
fi

echo ""
echo "[SCPL] Uninstallation complete!"
echo ""
echo "Removed:"
echo "  - $INSTALL_DIR"
echo "  - $SCPL_CMD"
echo ""
echo "If you installed libraries via MLIS, they were in:"
echo "  $LIBS_DIR (removed with main directory)"
echo ""
echo "To completely clean up, you may also want to:"
echo "  source ~/.bashrc  # Reload shell configuration"
echo "  rm -rf ~/.cache/scpl  # Remove cache if exists"
