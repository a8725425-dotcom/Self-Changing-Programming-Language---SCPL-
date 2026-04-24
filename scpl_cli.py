#!/usr/bin/env python3
import sys
from pathlib import Path
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
        return
    
    cmd = sys.argv[1]
    
    if cmd == "run":
        if len(sys.argv) < 3:
            print("Usage: scpl run <file.scpl>")
            return
        engine.run_file(sys.argv[2])
    
    elif cmd == "repl":
        print(f"SCPL REPL v{engine.VERSION} (type 'exit' to quit)")
        engine.env._init_console()
        while True:
            try:
                code = input("scpl> ")
                if code.lower() == 'exit':
                    break
                if code.strip():
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
        print("Features: Variables, Math, If/Else, Loops, Functions, 3D, AI, Sound, Files, Input")
    
    elif cmd == "state":
        import json
        print(json.dumps(engine.get_state(), indent=2))
    
    else:
        print(f"Unknown: {cmd}")

if __name__ == "__main__":
    main()
