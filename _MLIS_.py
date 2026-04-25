# _MLIS_.py - Modular Library Installer for SCPL
import os
import sys
import json
import shutil
import subprocess
import requests
from pathlib import Path

# URL официального списка библиотек (ТВОЙ РЕПОЗИТОРИЙ)
OFFICIAL_LIST_URL = "https://raw.githubusercontent.com/a8725425-dotcom/Self-Changing-Programming-Language---SCPL-/refs/heads/main/libs_list.txt"

# Директория для библиотек (рядом с движком)
LIBS_DIR = Path(__file__).parent / "libs"
REGISTRY_FILE = LIBS_DIR / "list.lsli"

class MLIS:
    """Modular Library Installer for SCPL"""
    
    def __init__(self):
        LIBS_DIR.mkdir(exist_ok=True)
        if not REGISTRY_FILE.exists():
            self._save_registry({})
    
    def _load_registry(self):
        """Загружает реестр установленных библиотек."""
        try:
            return json.loads(REGISTRY_FILE.read_text(encoding='utf-8'))
        except:
            return {}
    
    def _save_registry(self, data):
        """Сохраняет реестр установленных библиотек."""
        REGISTRY_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding='utf-8')
    
    def _fetch_official_list(self):
        """Загружает официальный список библиотек из GitHub."""
        try:
            print(f"[MLIS] Fetching official list...")
            resp = requests.get(OFFICIAL_LIST_URL, timeout=10)
            resp.raise_for_status()
            libs = {}
            for line in resp.text.splitlines():
                line = line.strip()
                # Пропускаем пустые строки и комментарии
                if not line or line.startswith('#'):
                    continue
                # Пропускаем явно невалидные строки (без знака =, или None XD)
                if '=' not in line:
                    continue
                name, url = line.split('=', 1)
                name = name.strip()
                url = url.strip()
                # Валидируем URL (должен содержать github.com)
                if name and url and ('github.com' in url or 'gitlab.com' in url):
                    libs[name] = url
                else:
                    print(f"[MLIS] Skipping invalid entry: {line}")
            print(f"[MLIS] Found {len(libs)} libraries in official list")
            return libs
        except Exception as e:
            print(f"[MLIS] Error fetching official list: {e}")
            return {}
    
    def _get_lib_url(self, name):
        """Получает URL библиотеки из официального списка."""
        official = self._fetch_official_list()
        return official.get(name)
    
    def _clone_repo(self, url, dest):
        """Клонирует Git-репозиторий."""
        try:
            print(f"[MLIS] Cloning {url}...")
            subprocess.run(["git", "clone", url, str(dest)], check=True, capture_output=True)
            return True
        except subprocess.CalledProcessError as e:
            print(f"[MLIS] Git clone failed: {e}")
            return False
        except FileNotFoundError:
            print("[MLIS] Error: Git is not installed. Please install Git first.")
            return False
    
    def _install_dependencies(self, lib_path):
        """Рекурсивно устанавливает зависимости библиотеки."""
        dep_file = Path(lib_path) / "dependencies.json"
        if not dep_file.exists():
            return
        
        try:
            deps = json.loads(dep_file.read_text(encoding='utf-8'))
            for dep_name, dep_version in deps.items():
                if not self._is_installed(dep_name):
                    print(f"[MLIS] Installing dependency: {dep_name} ({dep_version})")
                    self.install(dep_name)
        except Exception as e:
            print(f"[MLIS] Error reading dependencies: {e}")
    
    def _is_installed(self, name):
        """Проверяет, установлена ли библиотека."""
        registry = self._load_registry()
        return name in registry
    
    def install(self, name):
        """Устанавливает библиотеку."""
        if self._is_installed(name):
            print(f"[MLIS] '{name}' is already installed")
            return
        
        url = self._get_lib_url(name)
        if not url:
            print(f"[MLIS] Library '{name}' not found in official list")
            return
        
        lib_path = LIBS_DIR / name
        
        # Если папка существует, удаляем старую версию
        if lib_path.exists():
            shutil.rmtree(lib_path)
        
        print(f"[MLIS] Installing {name}...")
        
        if not self._clone_repo(url, lib_path):
            # Если git clone не сработал, пробуем скачать как ZIP
            print(f"[MLIS] Trying ZIP download...")
            if not self._download_zip(url, lib_path):
                print(f"[MLIS] Failed to install {name}")
                return
        
        # Устанавливаем зависимости
        self._install_dependencies(lib_path)
        
        # Обновляем реестр
        registry = self._load_registry()
        registry[name] = {
            "version": "latest",
            "path": str(lib_path),
            "url": url,
            "dependencies": self._read_dependencies(lib_path)
        }
        self._save_registry(registry)
        print(f"[MLIS] Successfully installed {name}")
    
    def _download_zip(self, url, dest):
        """Скачивает репозиторий как ZIP (fallback)."""
        try:
            zip_url = url.rstrip('/').replace('.git', '/archive/refs/heads/main.zip')
            print(f"[MLIS] Downloading {zip_url}...")
            response = requests.get(zip_url, timeout=30)
            response.raise_for_status()
            
            import tempfile
            import zipfile
            
            with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            
            with zipfile.ZipFile(tmp_path, 'r') as zip_ref:
                temp_dir = Path(tempfile.mkdtemp())
                zip_ref.extractall(temp_dir)
                
                extracted = list(temp_dir.iterdir())
                if len(extracted) == 1 and extracted[0].is_dir():
                    shutil.move(str(extracted[0]), str(dest))
                else:
                    shutil.move(str(temp_dir), str(dest))
            
            os.unlink(tmp_path)
            return True
        except Exception as e:
            print(f"[MLIS] ZIP download failed: {e}")
            return False
    
    def uninstall(self, name):
        """Удаляет библиотеку."""
        registry = self._load_registry()
        if name not in registry:
            print(f"[MLIS] '{name}' is not installed")
            return
        
        lib_path = Path(registry[name]["path"])
        if lib_path.exists():
            shutil.rmtree(lib_path)
            print(f"[MLIS] Removed directory: {lib_path}")
        
        del registry[name]
        self._save_registry(registry)
        print(f"[MLIS] Uninstalled {name}")
    
    def info(self, name):
        """Показывает информацию о библиотеке."""
        registry = self._load_registry()
        if name not in registry:
            print(f"[MLIS] '{name}' is not installed")
            
            url = self._get_lib_url(name)
            if url:
                print(f"[MLIS] Available in official list: {url}")
            else:
                print(f"[MLIS] Not found in official list")
            return
        
        info = registry[name]
        print(f"\nLibrary: {name}")
        print(f"Version: {info['version']}")
        print(f"Path: {info['path']}")
        print(f"Source: {info['url']}")
        print(f"Dependencies: {info.get('dependencies', [])}")
        
        lib_path = Path(info['path'])
        if lib_path.exists():
            files = list(lib_path.glob("*"))
            print(f"Files: {len(files)}")
            for f in files[:10]:
                print(f"  - {f.name}")
    
    def list_installed(self):
        """Выводит список установленных библиотек."""
        registry = self._load_registry()
        if not registry:
            print("[MLIS] No libraries installed")
            return
        
        print(f"\nInstalled libraries ({len(registry)}):")
        for name, info in registry.items():
            deps = info.get('dependencies', [])
            deps_str = f" (deps: {', '.join(deps)})" if deps else ""
            print(f"  - {name} ({info['version']}){deps_str}")
    
    def _read_dependencies(self, lib_path):
        """Читает зависимости из dependencies.json."""
        dep_file = Path(lib_path) / "dependencies.json"
        if dep_file.exists():
            try:
                deps = json.loads(dep_file.read_text(encoding='utf-8'))
                return list(deps.keys())
            except:
                pass
        return []

def main():
    """Точка входа для прямого запуска _MLIS_.py"""
    if len(sys.argv) < 2:
        print("MLIS - Modular Library Installer for SCPL")
        print("Usage: python _MLIS_.py <install|uninstall|info|list> [library]")
        return
    
    mlis = MLIS()
    cmd = sys.argv[1].lower()
    name = sys.argv[2] if len(sys.argv) > 2 else None
    
    if cmd == "install":
        if not name:
            print("Usage: python _MLIS_.py install <library>")
            return
        mlis.install(name)
    elif cmd == "uninstall":
        if not name:
            print("Usage: python _MLIS_.py uninstall <library>")
            return
        mlis.uninstall(name)
    elif cmd == "info":
        if not name:
            print("Usage: python _MLIS_.py info <library>")
            return
        mlis.info(name)
    elif cmd == "list":
        mlis.list_installed()
    else:
        print(f"Unknown command: {cmd}")

if __name__ == "__main__":
    main()
