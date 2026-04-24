# _MLIS_.py - Modular Library Installer for SCPL
import os
import sys
import json
import shutil
import subprocess
import requests
from pathlib import Path

OFFICIAL_LIST_URL = "https://raw.githubusercontent.com/your-org/scpl-libs/main/libs_list.txt"
LIBS_DIR = Path(__file__).parent / "libs"
REGISTRY_FILE = LIBS_DIR / "list.lsli"

class MLIS:
    def __init__(self):
        LIBS_DIR.mkdir(exist_ok=True)
        if not REGISTRY_FILE.exists():
            self._save_registry({})

    def _load_registry(self):
        return json.loads(REGISTRY_FILE.read_text())

    def _save_registry(self, data):
        REGISTRY_FILE.write_text(json.dumps(data, indent=2))

    def _fetch_official_list(self):
        try:
            resp = requests.get(OFFICIAL_LIST_URL)
            resp.raise_for_status()
            libs = {}
            for line in resp.text.splitlines():
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        name, url = line.split('=', 1)
                        libs[name.strip()] = url.strip()
            return libs
        except Exception as e:
            print(f"[MLIS] Error fetching official list: {e}")
            return {}

    def _get_lib_url(self, name):
        official = self._fetch_official_list()
        return official.get(name)

    def _clone_repo(self, url, dest):
        try:
            subprocess.run(["git", "clone", url, str(dest)], check=True)
            return True
        except subprocess.CalledProcessError:
            return False

    def _install_dependencies(self, lib_path):
        dep_file = Path(lib_path) / "dependencies.json"
        if not dep_file.exists():
            return
        try:
            deps = json.loads(dep_file.read_text())
            for dep_name in deps:
                if not self._is_installed(dep_name):
                    print(f"[MLIS] Installing dependency: {dep_name}")
                    self.install(dep_name)
        except Exception as e:
            print(f"[MLIS] Error reading dependencies: {e}")

    def _is_installed(self, name):
        registry = self._load_registry()
        return name in registry

    def install(self, name):
        if self._is_installed(name):
            print(f"[MLIS] {name} already installed")
            return
        url = self._get_lib_url(name)
        if not url:
            print(f"[MLIS] Library '{name}' not found in official list")
            return
        
        lib_path = LIBS_DIR / name
        print(f"[MLIS] Installing {name} from {url}...")
        if not self._clone_repo(url, lib_path):
            print(f"[MLIS] Failed to clone repository")
            return
        
        self._install_dependencies(lib_path)
        
        registry = self._load_registry()
        registry[name] = {
            "version": "latest",
            "path": str(lib_path),
            "url": url,
            "dependencies": self._read_dependencies(lib_path)
        }
        self._save_registry(registry)
        print(f"[MLIS] Successfully installed {name}")

    def uninstall(self, name):
        registry = self._load_registry()
        if name not in registry:
            print(f"[MLIS] {name} not installed")
            return
        lib_path = Path(registry[name]["path"])
        if lib_path.exists():
            shutil.rmtree(lib_path)
        del registry[name]
        self._save_registry(registry)
        print(f"[MLIS] Uninstalled {name}")

    def info(self, name):
        registry = self._load_registry()
        if name not in registry:
            print(f"[MLIS] {name} not installed")
            return
        info = registry[name]
        print(f"Name: {name}")
        print(f"Version: {info['version']}")
        print(f"Path: {info['path']}")
        print(f"Dependencies: {info.get('dependencies', [])}")

    def list_installed(self):
        registry = self._load_registry()
        if not registry:
            print("[MLIS] No libraries installed")
            return
        for name, info in registry.items():
            print(f"  {name} ({info['version']})")

    def _read_dependencies(self, lib_path):
        dep_file = Path(lib_path) / "dependencies.json"
        if dep_file.exists():
            try:
                return list(json.loads(dep_file.read_text()).keys())
            except:
                pass
        return []

def main():
    if len(sys.argv) < 2:
        print("MLIS - Modular Library Installer for SCPL")
        print("Usage: mlis <install|uninstall|info|list> [library]")
        return
    
    mlis = MLIS()
    cmd = sys.argv[1].lower()
    name = sys.argv[2] if len(sys.argv) > 2 else None
    
    if cmd == "install":
        if not name:
            print("Usage: mlis install <library>")
            return
        mlis.install(name)
    elif cmd == "uninstall":
        if not name:
            print("Usage: mlis uninstall <library>")
            return
        mlis.uninstall(name)
    elif cmd == "info":
        if not name:
            print("Usage: mlis info <library>")
            return
        mlis.info(name)
    elif cmd == "list":
        mlis.list_installed()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
