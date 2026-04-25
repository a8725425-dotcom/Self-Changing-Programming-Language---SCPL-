#!/usr/bin/env python3
# scpl_cli.py - SCPL CLI with MLIS support
import sys
import os
from pathlib import Path

# Добавляем текущую директорию в путь для импорта модулей SCPL
sys.path.insert(0, str(Path(__file__).parent))

sys.path.insert(0, str(Path.home()))

from scpl_engine import SCPLEngine

def main():
    engine = SCPLEngine()
    
    if len(sys.argv) < 2:
        print(f"SCPL v{engine.VERSION} - Self-Changing Programming Language")
        print("Usage:")
        print("  scpl run <file.scpl>     Run a .scpl file")
        print("  scpl repl                Start interactive REPL")
        print("  scpl new <name>          Create new .scpl file")
        print("  scpl version             Show version")
        print("  scpl state               Show engine state")
        print("  scpl mlis <cmd> [lib]    Library manager (install/uninstall/info/list)")
        return
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: scpl run <file.scpl>")
            return
        engine.run_file(sys.argv[2])
    
    elif cmd == "repl":
        print(f"SCPL REPL v{engine.VERSION} (type 'exit' to quit)")
        print("Commands: .mlis <install|uninstall|info|list> [lib] - Library manager")
        engine.env._init_console()
        while True:
            try:
                code = input("scpl> ")
                if code.lower() == 'exit':
                    break
                if code.strip():
                    # Специальные команды REPL
                    if code.startswith('.mlis'):
                        _handle_mlis_in_repl(code[5:].strip())
                    else:
                        engine.run_code(code)
            except KeyboardInterrupt:
                print()
                break
            except Exception as e:
                print(f"[Error] {e}")
        engine.env._close_console()
    
    elif cmd == "new":
        name = sys.argv[2] if len(sys.argv) > 2 else "untitled"
        if not name.endswith('.scpl'):
            name += '.scpl'
        Path(name).write_text("""import os
Initialize-console
Console-print: 'Hello from SCPL v2.0!'
Close-console""")
        print(f"[SCPL] Created: {name}")
    
    elif cmd == "version":
        print(f"SCPL v{engine.VERSION}")
        print("Features: Variables, Math, If/Else, Loops, Functions, 3D, AI, Sound, Files, Input, MLIS")
    
    elif cmd == "state":
        import json
        print(json.dumps(engine.get_state(), indent=2))
    
    elif cmd == "mlis":
        if len(sys.argv) < 3:
            print("Usage: scpl mlis <install|uninstall|info|list> [library]")
            return
        
        sub_cmd = sys.argv[2]
        lib_name = sys.argv[3] if len(sys.argv) > 3 else None
        
        # Импортируем MLIS
        try:
            import _MLIS_
        except ImportError:
            print("[SCPL] Error: _MLIS_.py not found. Make sure it's in the SCPL directory.")
            return
        
        mlis = _MLIS_.MLIS()
        
        if sub_cmd == "install":
            if not lib_name:
                print("Usage: scpl mlis install <library>")
                return
            mlis.install(lib_name)
        
        elif sub_cmd == "uninstall":
            if not lib_name:
                print("Usage: scpl mlis uninstall <library>")
                return
            mlis.uninstall(lib_name)
        
        elif sub_cmd == "info":
            if not lib_name:
                print("Usage: scpl mlis info <library>")
                return
            mlis.info(lib_name)
        
        elif sub_cmd == "list":
            mlis.list_installed()
        
        else:
            print(f"Unknown MLIS command: {sub_cmd}")
    
    else:
        print(f"Unknown: {cmd}")

def _handle_mlis_in_repl(args_str):
    """Обрабатывает команды MLIS внутри REPL."""
    try:
        import _MLIS_
    except ImportError:
        print("[SCPL] Error: _MLIS_.py not found.")
        return
    
    parts = args_str.split()
    if not parts:
        print("Usage: .mlis <install|uninstall|info|list> [library]")
        return
    
    mlis = _MLIS_.MLIS()
    cmd = parts[0].lower()
    name = parts[1] if len(parts) > 1 else None
    
    if cmd == "install":
        if not name:
            print("Usage: .mlis install <library>")
            return
        mlis.install(name)
    elif cmd == "uninstall":
        if not name:
            print("Usage: .mlis uninstall <library>")
            return
        mlis.uninstall(name)
    elif cmd == "info":
        if not name:
            print("Usage: .mlis info <library>")
            return
        mlis.info(name)
    elif cmd == "list":
        mlis.list_installed()
    else:
        print(f"Unknown MLIS command: {cmd}")

if __name__ == "__main__":
    main()
