# scpl_engine.py - SCPL Engine v2.0 (ПОЛНЫЙ ФИКС ПАРСЕРА)
import os
import random
import json
import time
import uuid
import shutil
import subprocess
from pathlib import Path
from typing import List, Any
from urllib import error as urllib_error
from urllib import request as urllib_request


class SCPLString(str):
    """Строковый литерал в AST, чтобы не путать его с идентификатором."""


class TailCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args


class SCPLParseError(Exception):
    def __init__(self, message, line=None, column=None):
        super().__init__(message)
        self.message = str(message)
        self.line = line
        self.column = column

# ═══════════════════════════════
# AI-CREATOR
# ═══════════════════════════════
class AICreator:
    def __init__(self):
        self.networks = {}
    
    def create_network(self, name, input_size, output_size, hidden_layers=0):
        if isinstance(hidden_layers, int):
            hidden = [input_size // 2] * hidden_layers if hidden_layers > 0 else []
        elif isinstance(hidden_layers, list):
            hidden = hidden_layers
        else:
            hidden = []
        layers = [input_size] + hidden + [output_size]
        network = {'weights': [], 'biases': [], 'arch': layers}
        for i in range(len(layers) - 1):
            w = [[random.uniform(-1, 1) for _ in range(layers[i])] for _ in range(layers[i+1])]
            b = [random.uniform(-1, 1) for _ in range(layers[i+1])]
            network['weights'].append(w)
            network['biases'].append(b)
        self.networks[name] = network
        return f"Network {name}: {layers}"
    
    def predict(self, name, inputs):
        net = self.networks.get(name)
        if not net: return f"Error: {name} not found"
        current = list(inputs)[:net['arch'][0]]
        current += [0] * (net['arch'][0] - len(current))
        for w, b in zip(net['weights'], net['biases']):
            next_layer = []
            for wrow, bval in zip(w, b):
                val = sum(i * wgt for i, wgt in zip(current, wrow)) + bval
                next_layer.append(max(0, val))
            current = next_layer
        return current
    
    def mutate(self, name, rate=0.1):
        net = self.networks.get(name)
        if net:
            for wmat in net['weights']:
                for row in wmat:
                    for i in range(len(row)):
                        if random.random() < rate:
                            row[i] += random.uniform(-0.5, 0.5)
    
    def save(self, name, filename):
        net = self.networks.get(name)
        if net:
            with open(filename, 'w') as f:
                json.dump(net, f)
            return f"Network saved to {filename}"
    
    def load(self, filename, name):
        with open(filename, 'r') as f:
            self.networks[name] = json.load(f)
        return f"Network {name} loaded"

# ═══════════════════════════════
# 3D MODULE
# ═══════════════════════════════
class SCPLGL:
    def __init__(self):
        self.objects = {}
    
    def create_cube(self, name, size=1.0):
        self.objects[name] = {'type': 'cube', 'size': size, 'pos': [0,0,0], 'rot': [0,0,0], 'color': [1,1,1], 'visible': True}
        return f"Cube {name} created"
    
    def create_sphere(self, name, radius=1.0):
        self.objects[name] = {'type': 'sphere', 'radius': radius, 'pos': [0,0,0], 'rot': [0,0,0], 'color': [1,1,1], 'visible': True}
        return f"Sphere {name} created"
    
    def delete_object(self, name):
        if name in self.objects:
            del self.objects[name]
            return f"Deleted {name}"
        return f"Object {name} not found"
    
    def move_object(self, name, x, y, z):
        if name in self.objects:
            self.objects[name]['pos'] = [x, y, z]
            return f"{name} moved to [{x}, {y}, {z}]"
        return f"Object {name} not found"
    
    def rotate_object(self, name, x, y, z):
        if name in self.objects:
            self.objects[name]['rot'] = [x, y, z]
    
    def set_color(self, name, r, g, b):
        if name in self.objects:
            self.objects[name]['color'] = [r, g, b]
    
    def get_position(self, name):
        if name in self.objects:
            return self.objects[name]['pos']
        return [0,0,0]
    
    def check_collision(self, obj1, obj2):
        if obj1 in self.objects and obj2 in self.objects:
            p1 = self.objects[obj1]['pos']
            p2 = self.objects[obj2]['pos']
            dist = sum((a-b)**2 for a,b in zip(p1, p2)) ** 0.5
            return dist < 2.0
        return False
    
    def list_objects(self):
        return list(self.objects.keys())
    
    def count_objects(self):
        return len(self.objects)

# ═══════════════════════════════
# FILE SYSTEM
# ═══════════════════════════════
class SCPLFileSystem:
    @staticmethod
    def read(filename):
        try:
            return Path(filename).read_text()
        except:
            return f"Error: Cannot read {filename}"
    
    @staticmethod
    def write(filename, content):
        Path(filename).write_text(str(content))
        return f"Written to {filename}"
    
    @staticmethod
    def append(filename, content):
        with open(filename, 'a') as f:
            f.write(str(content) + '\n')
    
    @staticmethod
    def delete(filename):
        Path(filename).unlink(missing_ok=True)
        return f"Deleted {filename}"
    
    @staticmethod
    def exists(filename):
        return Path(filename).exists()
    
    @staticmethod
    def list_dir(path="."):
        return [str(p) for p in Path(path).iterdir()]

# ═══════════════════════════════
# INPUT HANDLER
# ═══════════════════════════════
class SCPLInput:
    def __init__(self):
        self.last_input = ""
    
    def wait_input(self, prompt=""):
        if prompt:
            print(prompt, end='', flush=True)
        self.last_input = input()
        return self.last_input
    
    def get_last(self):
        return self.last_input

# ═══════════════════════════════
# SOUND MODULE
# ═══════════════════════════════
class SCPLSound:
    def __init__(self):
        self.volume = 1.0
        self.current_source = None
        self.current_mode = None
        self.backend = self._detect_backend()

    def _detect_backend(self):
        if shutil.which("termux-media-player"):
            return "termux-media-player"
        return "console"

    def _candidate_paths(self, name):
        raw = Path(str(name)).expanduser()
        if raw.is_absolute():
            yield raw
        else:
            yield Path.cwd() / raw
            yield Path(__file__).parent / raw
            yield Path(__file__).parent / "sounds" / raw
            yield raw

    def _resolve_source(self, name):
        if name is None:
            return None

        value = str(name).strip()
        if not value:
            return None

        base_candidates = list(self._candidate_paths(value))
        extensions = ("", ".mp3", ".wav", ".ogg", ".m4a", ".flac")

        seen = set()
        for candidate in base_candidates:
            for ext in extensions:
                path = candidate if not ext else candidate.with_suffix(ext)
                normalized = str(path.resolve()) if path.exists() else str(path)
                if normalized in seen:
                    continue
                seen.add(normalized)
                if path.exists() and path.is_file():
                    return path
        return None

    def _run_termux_media_player(self, *args):
        try:
            completed = subprocess.run(
                ["termux-media-player", *args],
                check=False,
                capture_output=True,
                text=True,
            )
            if completed.returncode == 0:
                return True, (completed.stdout or "").strip()
            message = (completed.stderr or completed.stdout or "").strip()
            return False, message or "termux-media-player failed"
        except Exception as exc:
            return False, str(exc)
    
    def play(self, name):
        source = self._resolve_source(name)
        if self.backend == "termux-media-player" and source is not None:
            ok, message = self._run_termux_media_player("play", str(source))
            if ok:
                self.current_source = str(source)
                self.current_mode = "termux-media-player"
                return f"Playing {source.name}"
            return f"Error: {message}"

        print(f"[Sound] Playing: {name}")
        self.current_source = str(name)
        self.current_mode = "console"
        return f"Playing {name}"
    
    def stop(self, name=None):
        if self.current_mode == "termux-media-player":
            ok, message = self._run_termux_media_player("stop")
            if ok:
                stopped = self.current_source or name or "sound"
                self.current_source = None
                self.current_mode = None
                return f"Stopped {Path(str(stopped)).name}"
            print(f"[Sound] Stop error: {message}")

        print(f"[Sound] Stopped: {name}")
        self.current_source = None
        self.current_mode = None
        return f"Stopped {name}"
    
    def set_volume(self, vol):
        self.volume = max(0, min(1, vol))
        return self.volume

    def info(self):
        return {
            'backend': self.backend,
            'volume': self.volume,
            'current_source': self.current_source,
            'current_mode': self.current_mode,
        }

# ═══════════════════════════════
# PARSER (ПОЛНОСТЬЮ ПЕРЕПИСАН)
# ═══════════════════════════════
class SCPLParser:
    def parse(self, code: str) -> List:
        """Парсит код в AST-дерево."""
        if not code or not code.strip():
            return []
        
        tokens = self._tokenize(code)
        asts = []
        i = 0
        
        while i < len(tokens):
            if tokens[i] == '\n':
                i += 1
                continue
            if tokens[i] == '(':
                ast, i = self._parse_s_expr(tokens, i)
                asts.append(ast)
            else:
                ast, i = self._parse_m_expr(tokens, i)
                asts.append(ast)
        
        return asts
    
    def _tokenize(self, code: str) -> List:
        """Разбивает код на токены."""
        tokens = []
        lines = code.split('\n')
        
        for line_no, line in enumerate(lines, start=1):
            stripped = line.strip()
            if not stripped or stripped.startswith('--'):
                continue
            
            i = 0
            while i < len(stripped):
                c = stripped[i]
                
                # Пробелы
                if c in ' \t':
                    i += 1
                    continue
                
                # Скобки
                if c in '()':
                    tokens.append(c)
                    i += 1
                    continue
                
                # Двоеточие (для M-выражений)
                if c == ':':
                    tokens.append(':')
                    i += 1
                    continue
                
                # Строки
                if c in '\'"':
                    quote = c
                    start_col = i + 1
                    i += 1
                    s = ''
                    while i < len(stripped) and stripped[i] != quote:
                        if stripped[i] == '\\' and i + 1 < len(stripped):
                            i += 1
                        s += stripped[i]
                        i += 1
                    if i >= len(stripped):
                        raise SCPLParseError(
                            f"unterminated string starting with {quote}",
                            line=line_no,
                            column=start_col,
                        )
                    i += 1  # Пропускаем закрывающую кавычку
                    tokens.append(f'{quote}{s}{quote}')
                    continue
                
                # Атомы (числа, идентификаторы)
                atom = ''
                while i < len(stripped) and stripped[i] not in ' \t():':
                    atom += stripped[i]
                    i += 1
                
                # Пробуем парсить как число
                try:
                    tokens.append(int(atom))
                except ValueError:
                    try:
                        tokens.append(float(atom))
                    except ValueError:
                        literal = atom.lower()
                        if literal == 'true':
                            tokens.append(True)
                        elif literal == 'false':
                            tokens.append(False)
                        elif literal in ('nil', 'null'):
                            tokens.append(None)
                        else:
                            tokens.append(atom)
            tokens.append('\n')
        
        return tokens
    
    def _parse_s_expr(self, tokens: List, i: int):
        """Парсит S-выражение: (func arg1 arg2 ...)"""
        i += 1  # Пропускаем '('
        parts = []
        
        while i < len(tokens) and tokens[i] != ')':
            if tokens[i] == '\n':
                i += 1
                continue
            if tokens[i] == '(':
                sub_ast, i = self._parse_s_expr(tokens, i)
                parts.append(sub_ast)
            else:
                # Это может быть началом M-выражения
                if isinstance(tokens[i], str) and i + 1 < len(tokens) and tokens[i + 1] == ':':
                    ast, i = self._parse_m_expr(tokens, i)
                    parts.append(ast)
                else:
                    token = tokens[i]
                    # Распаковка строк
                    if isinstance(token, str) and token.startswith("'") and token.endswith("'"):
                        parts.append(SCPLString(token[1:-1]))
                    elif isinstance(token, str) and token.startswith('"') and token.endswith('"'):
                        parts.append(SCPLString(token[1:-1]))
                    else:
                        parts.append(token)
                    i += 1
        
        if i < len(tokens) and tokens[i] == ')':
            i += 1
        else:
            raise SCPLParseError("unterminated s-expression")
        
        return parts, i
    
    def _parse_m_expr(self, tokens: List, i: int):
        """Парсит M-выражение: func: arg1 arg2 ..."""
        func_name = tokens[i]
        i += 1
        
        # Пропускаем ':'
        if i < len(tokens) and tokens[i] == ':':
            i += 1
        
        args = []
        while i < len(tokens) and tokens[i] != '\n' and tokens[i] != ')':
            if tokens[i] == '(':
                sub_ast, i = self._parse_s_expr(tokens, i)
                args.append(sub_ast)
            elif isinstance(tokens[i], str) and tokens[i] == ':':
                break
            else:
                token = tokens[i]
                if isinstance(token, str) and token.startswith("'") and token.endswith("'"):
                    args.append(SCPLString(token[1:-1]))
                elif isinstance(token, str) and token.startswith('"') and token.endswith('"'):
                    args.append(SCPLString(token[1:-1]))
                else:
                    args.append(token)
                i += 1
        
        if i < len(tokens) and tokens[i] == '\n':
            i += 1
        
        return [func_name] + args, i

# ═══════════════════════════════
# ENVIRONMENT
# ═══════════════════════════════
class SCPLEnvironment:
    def __init__(self):
        self.scopes = [{}]
        self.vars = self.scopes[0]
        self.funcs = {}
        self.macros = {}
        self.log = []
        self.console_on = False
        self.return_value = None
        self.loop_control = None
        self.modules = {}
        self._if_active = False
        self._call_stack = []
        
        self.builtins = {
            # Консоль
            'import': self._import,
            'from': self._from_import,
            'Initialize-console': self._init_console,
            'Console-print': self._print,
            'Close-console': self._close_console,
            'Save-log': self._save_log,
            
            # Переменные
            'set': self._set,
            'get': self._get,
            'delete': self._delete,
            'var-exists': self._var_exists,
            'list-vars': self._list_vars,
            
            # Математика
            '+': self._add,
            '-': self._sub,
            '*': self._mul,
            '/': self._div,
            '%': lambda a, b: a % b,
            '^': lambda a, b: a ** b,
            'sqrt': lambda a: a ** 0.5,
            'abs': lambda a: abs(a),
            'random': lambda a=1, b=None: random.uniform(a, b) if b else random.uniform(0, a),
            'random-int': lambda a, b: random.randint(a, b),
            
            # Логика
            'if': self._if,
            'when': self._if,
            'else': self._else,
            '==': lambda a, b: a == b,
            '!=': lambda a, b: a != b,
            '>': lambda a, b: a > b,
            '<': lambda a, b: a < b,
            '>=': lambda a, b: a >= b,
            '<=': lambda a, b: a <= b,
            'and': lambda a, b: a and b,
            'or': lambda a, b: a or b,
            'not': lambda a: not a,
            
            # Циклы
            'loop': self._loop,
            'repeat': self._loop,
            'for': self._for,
            'while': self._while,
            'break': self._break,
            'continue': self._continue,
            
            # Функции
            'function': self._def_function,
            'lambda': self._lambda,
            'macro': self._def_macro,
            'call': self._call_function,
            'return': self._return,
            'do': self._do,
            'quote': self._quote,
            'quasiquote': self._quasiquote,
            'unquote': self._unquote,
            
            # Списки
            'list': lambda *args: list(args),
            'append': self._append,
            'length': lambda x: len(x) if hasattr(x, '__len__') else 1,
            'nth': lambda lst, n: lst[n] if isinstance(lst, list) and 0 <= n < len(lst) else None,
            'range': self._range,
            'slice': self._slice,
            'take': self._take,
            'drop': self._drop,
            'reverse': self._reverse,
            'contains?': self._contains,
            'sort': self._sort,
            'map': self._map,
            'flat-map': self._flat_map,
            'filter': self._filter,
            'reduce': self._reduce,

            # Словари
            'dict': self._dict,
            'dict-set': self._dict_set,
            'dict-get': self._dict_get,
            'dict-has': self._dict_has,
            'dict-delete': self._dict_delete,
            'dict-keys': self._dict_keys,
            'dict-values': self._dict_values,
            'dict-items': self._dict_items,

            # Строки
            'concat': lambda *args: ''.join(str(a) for a in args),
            'upper': lambda s: str(s).upper(),
            'lower': lambda s: str(s).lower(),
            'split': lambda s, d=' ': str(s).split(d),
            'join': lambda d, *args: str(d).join(str(a) for a in args),
            'trim': lambda s: str(s).strip(),
            'replace': lambda s, old, new: str(s).replace(str(old), str(new)),
            'starts-with?': lambda s, prefix: str(s).startswith(str(prefix)),
            'ends-with?': lambda s, suffix: str(s).endswith(str(suffix)),
            'substring': self._substring,
            'index-of': self._index_of,

            # Файлы
            'File-read': SCPLFileSystem.read,
            'File-write': SCPLFileSystem.write,
            'File-append': SCPLFileSystem.append,
            'File-delete': SCPLFileSystem.delete,
            'File-exists': SCPLFileSystem.exists,
            'List-dir': SCPLFileSystem.list_dir,
            
            # Ввод
            'Input-wait': self._input_wait,
            'Input-last': self._input_last,
            
            # Время
            'Time-now': lambda: time.time(),
            'Time-sleep': lambda s: time.sleep(s),
            'Time-stamp': lambda: time.strftime("%Y-%m-%d %H:%M:%S"),

            # JSON и пути
            'JSON-parse': self._json_parse,
            'JSON-stringify': self._json_stringify,
            'Path-join': lambda *parts: str(Path(*[str(part) for part in parts])),
            'Path-dirname': lambda path: str(Path(path).parent),
            'Path-basename': lambda path: Path(path).name,
            'Path-extname': lambda path: Path(path).suffix,
            'Path-normalize': lambda path: os.path.normpath(str(path)),

            # HTTP
            'HTTP-request': self._http_request,
            'HTTP-get': self._http_get,
            'HTTP-post': self._http_post,

            # Триггеры
            'trigger': self._trigger,
            'on': self._on_event,

            # Типы
            'type': self._type_name,

            # Результаты и ошибки
            'ok': self._ok,
            'error': self._error,
            'ok?': self._is_ok,
            'error?': self._is_error,
            'unwrap': self._unwrap,
            'error-message': self._error_message,
            
            # Мета
            'eval': self._eval,
            'try': self._try_eval,
        }

    def _current_scope(self):
        return self.scopes[-1]

    def _push_scope(self, initial=None):
        scope = {}
        if initial:
            scope.update(initial)
        self.scopes.append(scope)
        return scope

    def _pop_scope(self):
        if len(self.scopes) > 1:
            self.scopes.pop()

    def _find_scope(self, name):
        for scope in reversed(self.scopes):
            if name in scope:
                return scope
        return None

    def _resolve_var(self, name, default=None):
        scope = self._find_scope(name)
        if scope is None:
            return default
        return scope[name]

    def _visible_vars(self):
        merged = {}
        for scope in self.scopes:
            merged.update(scope)
        return merged

    def _expr_preview(self, value):
        if value is None:
            return 'nil'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, SCPLString):
            return repr(str(value))
        if isinstance(value, str):
            return value
        if isinstance(value, list):
            return '(' + ' '.join(self._expr_preview(item) for item in value) + ')'
        if self._is_function_value(value):
            return value.get('name') or '<lambda>'
        return str(value)

    def _make_function(self, params, body, name=None):
        param_list = params if isinstance(params, list) else [params]
        return {
            '__scpl_function__': True,
            'name': name,
            'params': [p for p in param_list if isinstance(p, str)],
            'body': list(body),
            'closure_scopes': [scope.copy() for scope in self.scopes],
        }

    def _is_function_value(self, value):
        return isinstance(value, dict) and value.get('__scpl_function__') is True
    
    def _add(self, *args):
        return sum(args)
    
    def _sub(self, a, b=0):
        return a - b
    
    def _mul(self, *args):
        if not args:
            return 1
        result = 1
        for a in args:
            result *= a
        return result
    
    def _div(self, a, b):
        return a / b if b != 0 else "Error: division by zero"
    
    def exec(self, ast):
        """Исполняет AST-узел."""
        if ast is None:
            return None
        if isinstance(ast, (int, float, bool)):
            return ast
        if isinstance(ast, SCPLString):
            return str(ast)
        if isinstance(ast, str):
            value = self._resolve_var(ast, None)
            if self._find_scope(ast) is not None:
                return value
            return ast
        if not isinstance(ast, list) or len(ast) == 0:
            return ast
        if len(ast) == 1 and isinstance(ast[0], list):
            return self.exec(ast[0])

        ast = self._expand_macros(ast)
        if not isinstance(ast, list) or len(ast) == 0:
            return self.exec(ast)
        if len(ast) == 1 and isinstance(ast[0], list):
            return self.exec(ast[0])

        fn = ast[0]

        # Специальные формы получают часть аргументов как AST, без раннего вычисления.
        if fn in ('import', 'from', 'try'):
            return self.builtins[fn](*ast[1:])
        if fn == 'set':
            name = ast[1] if len(ast) > 1 else None
            value = self.exec(ast[2]) if len(ast) > 2 else None
            return self.builtins[fn](name, value)
        if fn in ('get', 'delete', 'var-exists'):
            name = ast[1] if len(ast) > 1 else None
            return self.builtins[fn](name)
        if fn == 'function':
            return self.builtins[fn](ast[1], ast[2], *ast[3:])
        if fn == 'lambda':
            return self.builtins[fn](ast[1], *ast[2:])
        if fn == 'macro':
            return self.builtins[fn](ast[1], ast[2], *ast[3:])
        if fn == 'do':
            return self.builtins[fn](*ast[1:])
        if fn == 'quote':
            return self.builtins[fn](ast[1] if len(ast) > 1 else None)
        if fn == 'quasiquote':
            return self.builtins[fn](ast[1] if len(ast) > 1 else None)
        if fn == 'return':
            return self.builtins[fn](ast[1] if len(ast) > 1 else None)
        if fn in ('if', 'when'):
            condition = self.exec(ast[1]) if len(ast) > 1 else None
            return self.builtins[fn](condition, *ast[2:])
        if fn in ('loop', 'repeat'):
            count = self.exec(ast[1]) if len(ast) > 1 else 0
            return self.builtins[fn](count, *ast[2:])
        if fn == 'for':
            var_name = ast[1] if len(ast) > 1 else None
            start = self.exec(ast[2]) if len(ast) > 2 else 0
            end = self.exec(ast[3]) if len(ast) > 3 else 0
            return self.builtins[fn](var_name, start, end, *ast[4:])
        if fn == 'while':
            condition = ast[1] if len(ast) > 1 else None
            return self.builtins[fn](condition, *ast[2:])
        if fn in ('trigger', 'on'):
            name = self.exec(ast[1]) if len(ast) > 1 else None
            return self.builtins[fn](name, *ast[2:])

        args = []
        for a in ast[1:]:
            if isinstance(a, list):
                args.append(self.exec(a))
            elif isinstance(a, SCPLString):
                args.append(str(a))
            elif isinstance(a, str):
                if self._find_scope(a) is not None:
                    args.append(self._resolve_var(a))
                else:
                    args.append(a)
            else:
                args.append(a)
        
        head_value = None
        if isinstance(fn, str) and self._find_scope(fn) is not None:
            head_value = self._resolve_var(fn)

        if fn in self.builtins:
            return self.builtins[fn](*args)
        elif fn in self.funcs:
            return self._invoke_function(fn, args)
        elif self._is_function_value(head_value):
            return self._invoke_function_value(head_value, args)
        else:
            return self._error(
                f"unknown function: {fn}",
                {
                    'function': fn,
                    'expression': self._expr_preview(ast),
                },
            )

    def _clone_ast(self, node):
        if isinstance(node, list):
            return [self._clone_ast(item) for item in node]
        if isinstance(node, SCPLString):
            return SCPLString(str(node))
        return node

    def _expand_macros(self, ast, depth=0):
        if depth > 100:
            raise RecursionError("Macro expansion limit exceeded")
        if not isinstance(ast, list) or not ast:
            return ast

        fn = ast[0]
        if fn == 'quote':
            if len(ast) == 1:
                return ast
            return ['quote', self._clone_ast(ast[1])]
        if fn == 'quasiquote':
            return ast
        if isinstance(fn, str) and fn in self.macros:
            expanded = self._expand_macro_call(fn, ast[1:])
            return self._expand_macros(expanded, depth + 1)

        return [ast[0]] + [
            self._expand_macros(item, depth)
            if isinstance(item, list) else item
            for item in ast[1:]
        ]

    def _expand_macro_call(self, name, raw_args):
        macro = self.macros[name]
        bindings = {}
        for index, param in enumerate(macro['params']):
            bindings[param] = self._clone_ast(raw_args[index]) if index < len(raw_args) else None

        if len(macro['body']) == 1:
            template = macro['body'][0]
        else:
            template = ['do', *macro['body']]
        return self._expand_macro_template(template, bindings)

    def _expand_macro_template(self, node, bindings):
        if isinstance(node, list):
            if not node:
                return []
            head = node[0]
            if head == 'quote':
                if len(node) == 1:
                    return ['quote']
                return ['quote', self._clone_ast(node[1])]
            if head == 'quasiquote':
                if len(node) == 1:
                    return None
                return self._expand_quasiquote(node[1], bindings)
            return [self._expand_macro_template(item, bindings) for item in node]

        if isinstance(node, str) and node in bindings:
            return self._clone_ast(bindings[node])
        if isinstance(node, SCPLString):
            return SCPLString(str(node))
        return node

    def _expand_quasiquote(self, node, bindings):
        if isinstance(node, list):
            if node and node[0] == 'unquote':
                expr = node[1] if len(node) > 1 else None
                return self._expand_macro_template(expr, bindings)
            return [self._expand_quasiquote(item, bindings) for item in node]
        if isinstance(node, SCPLString):
            return SCPLString(str(node))
        return node

    def _is_self_tail_call(self, ast):
        return (
            isinstance(ast, list)
            and bool(ast)
            and bool(self._call_stack)
            and ast[0] == self._call_stack[-1]
        )

    def _invoke_function(self, name, args):
        func_body = self.funcs[name]
        return self._invoke_function_value(func_body, args, call_name=name)

    def _invoke_callable(self, fn, args):
        if self._is_function_value(fn):
            return self._invoke_function_value(fn, args)
        if isinstance(fn, str) and fn in self.funcs:
            return self._invoke_function(fn, args)
        if isinstance(fn, str) and fn in self.builtins:
            return self.builtins[fn](*args)
        return self._error(
            f"value is not callable: {fn}",
            {
                'value': fn,
                'callable': self._expr_preview(fn),
            },
        )

    def _invoke_function_value(self, func_body, args, call_name=None):
        params = func_body.get('params', [])
        expected = len(params)
        actual = len(args)
        function_name = call_name or func_body.get('name') or '<lambda>'

        if actual != expected:
            return self._error(
                f"arity mismatch for {function_name}: expected {expected}, got {actual}",
                {
                    'function': function_name,
                    'expected': expected,
                    'actual': actual,
                    'args': [self._expr_preview(arg) for arg in args],
                },
            )
        previous_scopes = self.scopes
        closure_scopes = list(func_body.get('closure_scopes', self.scopes))
        self._call_stack.append(function_name)
        next_args = list(args)
        local_scope = {}
        self.scopes = closure_scopes + [local_scope]

        try:
            while True:
                local_scope.clear()
                for i, param in enumerate(params):
                    if i < len(next_args):
                        local_scope[param] = next_args[i]

                result = None
                restart = False
                body = func_body.get('body', [])

                for index, expr in enumerate(body):
                    is_last = index == len(body) - 1
                    if is_last and self._is_self_tail_call(expr):
                        next_args = [self.exec(arg) for arg in expr[1:]]
                        restart = True
                        break

                    result = self.exec(expr)
                    if isinstance(self.return_value, TailCall):
                        next_args = self.return_value.args
                        self.return_value = None
                        restart = True
                        break
                    if self.return_value is not None:
                        result = self.return_value
                        self.return_value = None
                        return result

                if restart:
                    continue

                return result
        finally:
            self.scopes = previous_scopes
            self._call_stack.pop()
    
    # ── Модули ──
    def _load_library(self, name, alias=None):
        engine_dir = Path(__file__).parent
        lib_path = engine_dir / "libs" / name

        if not lib_path.exists():
            self.modules[name] = {
                'alias': alias,
                'exports': [],
            }
            return True, []

        init_scpl = lib_path / "__init__.scpl"
        if not init_scpl.exists():
            legacy_init = lib_path / "_init_.scpl"
            if legacy_init.exists():
                init_scpl = legacy_init
            else:
                return False, f"Library '{name}' has no __init__.scpl"

        code = init_scpl.read_text(encoding='utf-8')
        parser = SCPLParser()
        asts = parser.parse(code)
        funcs_before = set(self.funcs.keys())
        for ast in asts:
            self.exec(ast)

        new_funcs = sorted(set(self.funcs.keys()) - funcs_before)
        exported_names = list(new_funcs)

        if alias:
            alias = str(alias)
            exported_names = []
            for func_name in new_funcs:
                namespaced = f'{alias}/{func_name}'
                self.funcs[namespaced] = self.funcs[func_name]
                del self.funcs[func_name]
                exported_names.append(namespaced)

        self.modules[name] = {
            'alias': alias,
            'exports': exported_names,
        }
        return True, exported_names

    def _import(self, name=None, *options):
        if not name:
            return "Library name required"

        alias = None
        if len(options) >= 2 and options[0] == 'as':
            alias = options[1]

        ok, result = self._load_library(name, alias=alias)
        if not ok:
            return result
        if alias:
            return f"Loaded library: {name} as {alias}"
        return f"Loaded library: {name}"

    def _from_import(self, module_name=None, import_keyword=None, export_name=None, *options):
        if not module_name:
            return "Module name required"
        if import_keyword != 'import':
            return "Syntax: from <module> import <name> [as alias]"
        if not export_name:
            return "Export name required"

        target_name = export_name
        if len(options) >= 2 and options[0] == 'as':
            target_name = options[1]

        temp_alias = f'__scpl_tmp__{uuid.uuid4().hex[:8]}'
        ok, exports = self._load_library(module_name, alias=temp_alias)
        if not ok:
            return exports

        temp_export = f'{temp_alias}/{export_name}'
        if temp_export not in self.funcs:
            for temp_name in exports:
                self.funcs.pop(temp_name, None)
            return f"Export '{export_name}' not found in library '{module_name}'"

        self.funcs[str(target_name)] = self.funcs[temp_export]
        for temp_name in exports:
            self.funcs.pop(temp_name, None)
        self.modules[module_name] = {
            'alias': None,
            'exports': [str(target_name)],
        }
        return f"Imported {export_name} from {module_name} as {target_name}"
    
    # ── Консоль ──
    def _init_console(self):
        self.console_on = True
        self.log = []
        print("[SCPL Console] ON")

    def _format_value(self, value):
        if value is None:
            return 'nil'
        if isinstance(value, bool):
            return 'true' if value else 'false'
        if isinstance(value, list):
            return '[' + ', '.join(self._format_value(item) for item in value) + ']'
        if isinstance(value, dict):
            parts = [f"{key}: {self._format_value(val)}" for key, val in value.items()]
            return '{' + ', '.join(parts) + '}'
        return str(value)

    def _print(self, *args):
        if not self.console_on:
            print("[SCPL Error] Console not initialized!")
            return
        msg = ' '.join(self._format_value(a) for a in args)
        self.log.append(msg)
        print(msg)
    
    def _close_console(self):
        self.console_on = False
        print("[SCPL Console] OFF")
    
    def _save_log(self, filename, *opts):
        with open(filename, 'w') as f:
            f.write('\n'.join(self.log))
    
    # ── Переменные ──
    def _set(self, name, value):
        self._current_scope()[name] = value
        return value
    
    def _get(self, name):
        scope = self._find_scope(name)
        if scope is None:
            return f"Error: {name} not found"
        return scope[name]
    
    def _delete(self, name):
        scope = self._find_scope(name)
        if scope is not None:
            del scope[name]
    
    def _var_exists(self, name):
        return self._find_scope(name) is not None
    
    def _list_vars(self):
        return list(self._visible_vars().keys())
    
    # ── Условия ──
    def _if(self, condition, *body):
        then_body, else_body = self._split_if_branches(body)
        if condition:
            return self._exec_body(then_body)
        if else_body:
            return self._exec_body(else_body)
        return None
    
    def _else(self, *args):
        pass  # Обрабатывается в _if

    def _split_if_branches(self, body):
        then_body = []
        else_body = []
        target = then_body

        for expr in body:
            if isinstance(expr, list) and expr and expr[0] == 'else':
                target = else_body
                target.extend(expr[1:])
                continue
            target.append(expr)

        return then_body, else_body

    def _exec_body(self, exprs):
        result = None
        for expr in exprs:
            result = self.exec(expr)
            if self.return_value is not None:
                return result
        return result

    def _exec_loop_body(self, exprs):
        result = None
        self.loop_control = None

        for expr in exprs:
            result = self.exec(expr)

            if self.return_value is not None:
                self.loop_control = None
                return 'return', result

            if self.loop_control == 'break':
                self.loop_control = None
                return 'break', result

            if self.loop_control == 'continue':
                self.loop_control = None
                return 'continue', result

        return 'normal', result
    
    # ── Циклы ──
    def _loop(self, count, *body):
        result = None
        for _ in range(int(count)):
            status, result = self._exec_loop_body(body)
            if status == 'break':
                break
            if status == 'continue':
                continue
            if status == 'return':
                return result
        return result
    
    def _for(self, var_name, start, end, *body):
        result = None
        for i in range(int(start), int(end)):
            self._current_scope()[var_name] = i
            status, result = self._exec_loop_body(body)
            if status == 'break':
                break
            if status == 'continue':
                continue
            if status == 'return':
                return result
        return result
    
    def _while(self, condition, *body):
        result = None
        while self.exec(condition):
            status, result = self._exec_loop_body(body)
            if status == 'break':
                break
            if status == 'continue':
                continue
            if status == 'return':
                return result
        return result
    
    def _break(self):
        self.loop_control = 'break'
    
    def _continue(self):
        self.loop_control = 'continue'
    
    # ── Функции ──
    def _def_function(self, name, params, *body):
        """Определяет функцию: (function name (p1 p2) body...)"""
        self.funcs[name] = self._make_function(params, body, name=name)
        return f"Function {name} defined"

    def _lambda(self, params, *body):
        return self._make_function(params, body)

    def _def_macro(self, name, params, *body):
        param_list = params if isinstance(params, list) else [params]
        self.macros[name] = {
            'params': [p for p in param_list if isinstance(p, str)],
            'body': list(body),
        }
        return f"Macro {name} defined"

    def _call_function(self, name, *args):
        if self._is_function_value(name):
            return self._invoke_function_value(name, args)
        if name in self.funcs:
            return self._invoke_function(name, args)
        return self._error(
            f"value is not callable: {name}",
            {
                'value': name,
                'callable': self._expr_preview(name),
            },
        )

    def _return(self, value_ast=None):
        if self._is_self_tail_call(value_ast):
            args = [self.exec(arg) for arg in value_ast[1:]]
            self.return_value = TailCall(self._call_stack[-1], args)
            return None

        value = self.exec(value_ast) if isinstance(value_ast, list) else (
            str(value_ast) if isinstance(value_ast, SCPLString) else value_ast
        )
        if isinstance(value_ast, str) and not isinstance(value_ast, SCPLString):
            value = self._resolve_var(value_ast, value_ast)
        self.return_value = value
        return value

    def _do(self, *body):
        result = None
        for expr in body:
            result = self.exec(expr)
            if self.return_value is not None:
                return result
        return result

    def _quote(self, value):
        return self._clone_ast(value)

    def _quasiquote(self, value):
        return self._runtime_quasiquote(value)

    def _runtime_quasiquote(self, node):
        if isinstance(node, list):
            if node and node[0] == 'unquote':
                expr = node[1] if len(node) > 1 else None
                return self.exec(expr)
            return [self._runtime_quasiquote(item) for item in node]
        if isinstance(node, SCPLString):
            return str(node)
        return node

    def _unquote(self, value):
        return value
    
    # ── Списки ──
    def _append(self, lst, value):
        if isinstance(lst, list):
            lst.append(value)
            return lst

    def _range(self, start, end=None, step=1):
        if end is None:
            start_value = 0
            end_value = int(start)
        else:
            start_value = int(start)
            end_value = int(end)
        step_value = int(step)
        if step_value == 0:
            return self._error("range step cannot be zero")
        return list(range(start_value, end_value, step_value))

    def _slice(self, value, start=0, end=None):
        if hasattr(value, '__getitem__'):
            return value[int(start):None if end is None else int(end)]
        return None

    def _take(self, value, count):
        if not isinstance(value, list):
            return self._error("take expects a list")
        amount = max(0, int(count))
        return value[:amount]

    def _drop(self, value, count):
        if not isinstance(value, list):
            return self._error("drop expects a list")
        amount = max(0, int(count))
        return value[amount:]

    def _reverse(self, value):
        if isinstance(value, list):
            return list(reversed(value))
        return str(value)[::-1]

    def _contains(self, value, item):
        try:
            return item in value
        except TypeError:
            return False

    def _sort(self, value):
        if isinstance(value, list):
            try:
                return sorted(value)
            except TypeError:
                return "Error: list contains non-sortable values"
        return "Error: sort expects a list"

    def _map(self, fn, value):
        if not isinstance(value, list):
            return self._error("map expects a list")
        result = []
        for item in value:
            mapped = self._invoke_callable(fn, [item])
            if self._is_error(mapped):
                return mapped
            result.append(mapped)
        return result

    def _flat_map(self, fn, value):
        if not isinstance(value, list):
            return self._error("flat-map expects a list")
        result = []
        for item in value:
            mapped = self._invoke_callable(fn, [item])
            if self._is_error(mapped):
                return mapped
            if isinstance(mapped, list):
                result.extend(mapped)
            else:
                result.append(mapped)
        return result

    def _filter(self, fn, value):
        if not isinstance(value, list):
            return self._error("filter expects a list")
        result = []
        for item in value:
            keep = self._invoke_callable(fn, [item])
            if self._is_error(keep):
                return keep
            if keep:
                result.append(item)
        return result

    def _reduce(self, fn, value, initial=None):
        if not isinstance(value, list):
            return self._error("reduce expects a list")
        items = list(value)
        if initial is None:
            if not items:
                return self._error("reduce on empty list requires an initial value")
            acc = items.pop(0)
        else:
            acc = initial
        for item in items:
            acc = self._invoke_callable(fn, [acc, item])
            if self._is_error(acc):
                return acc
        return acc

    def _dict(self, *args):
        if len(args) % 2 != 0:
            return "Error: dict expects an even number of key/value arguments"
        result = {}
        for i in range(0, len(args), 2):
            result[str(args[i])] = args[i + 1]
        return result

    def _dict_set(self, data, key, value):
        if not isinstance(data, dict):
            return "Error: dict-set expects a dict"
        data[str(key)] = value
        return data

    def _dict_get(self, data, key, default=None):
        if not isinstance(data, dict):
            return default
        return data.get(str(key), default)

    def _dict_has(self, data, key):
        return isinstance(data, dict) and str(key) in data

    def _dict_delete(self, data, key):
        if not isinstance(data, dict):
            return "Error: dict-delete expects a dict"
        data.pop(str(key), None)
        return data

    def _dict_keys(self, data):
        if not isinstance(data, dict):
            return []
        return list(data.keys())

    def _dict_values(self, data):
        if not isinstance(data, dict):
            return []
        return list(data.values())

    def _dict_items(self, data):
        if not isinstance(data, dict):
            return []
        return [[key, value] for key, value in data.items()]
    
    # ── Ввод ──
    def _input_wait(self, prompt=""):
        return input(str(prompt))
    
    def _input_last(self):
        return getattr(self, '_last_input', "")

    def _json_parse(self, raw):
        try:
            return json.loads(str(raw))
        except json.JSONDecodeError as exc:
            return self._error(f"invalid JSON ({exc.msg})")

    def _json_stringify(self, value):
        try:
            return json.dumps(value, ensure_ascii=False)
        except TypeError as exc:
            return self._error(f"cannot encode to JSON ({exc})")

    def _normalize_http_headers(self, headers):
        if headers is None:
            return {}
        if isinstance(headers, dict):
            return {str(key): str(value) for key, value in headers.items()}
        return {}

    def _http_request(self, method, url, headers=None, body=None, timeout=10):
        method_name = str(method).upper()
        req_headers = self._normalize_http_headers(headers)
        data = None

        if body is not None:
            if isinstance(body, (dict, list)):
                data = json.dumps(body, ensure_ascii=False).encode('utf-8')
                req_headers.setdefault('Content-Type', 'application/json')
            elif isinstance(body, bytes):
                data = body
            else:
                data = str(body).encode('utf-8')

        try:
            req = urllib_request.Request(
                str(url),
                data=data,
                headers=req_headers,
                method=method_name,
            )
            with urllib_request.urlopen(req, timeout=float(timeout)) as resp:
                raw_body = resp.read()
                text_body = raw_body.decode('utf-8', errors='replace')
                status = getattr(resp, 'status', None)
                if status is None:
                    status = resp.getcode()
                if status is None:
                    status = 200
                return self._ok({
                    'status': status,
                    'url': resp.geturl(),
                    'headers': dict(resp.headers.items()),
                    'body': text_body,
                })
        except urllib_error.HTTPError as exc:
            error_body = exc.read().decode('utf-8', errors='replace')
            return self._error(
                f"http error {exc.code}",
                {
                    'status': exc.code,
                    'url': str(url),
                    'body': error_body,
                },
            )
        except urllib_error.URLError as exc:
            return self._error(
                f"request failed: {exc.reason}",
                {
                    'url': str(url),
                },
            )
        except Exception as exc:
            return self._error(
                str(exc),
                {
                    'url': str(url),
                },
            )

    def _http_get(self, url, headers=None, timeout=10):
        return self._http_request('GET', url, headers, None, timeout)

    def _http_post(self, url, body=None, headers=None, timeout=10):
        return self._http_request('POST', url, headers, body, timeout)

    def _substring(self, value, start, end=None):
        text = str(value)
        return text[int(start):None if end is None else int(end)]

    def _index_of(self, value, needle):
        text = str(value)
        return text.find(str(needle))

    def _type_name(self, value):
        if value is None:
            return 'nil'
        if isinstance(value, bool):
            return 'bool'
        if isinstance(value, (int, float)):
            return 'number'
        if isinstance(value, str):
            return 'string'
        if self._is_function_value(value):
            return 'function'
        if isinstance(value, list):
            return 'list'
        if isinstance(value, dict):
            if value.get('__scpl_result__') == 'ok':
                return 'ok'
            if value.get('__scpl_result__') == 'error':
                return 'error'
            return 'dict'
        return type(value).__name__

    def _ok(self, value=None):
        return {
            '__scpl_result__': 'ok',
            'value': value,
        }

    def _error(self, message, details=None):
        return {
            '__scpl_result__': 'error',
            'message': str(message),
            'details': details,
        }

    def _is_ok(self, value):
        return isinstance(value, dict) and value.get('__scpl_result__') == 'ok'

    def _is_error(self, value):
        return isinstance(value, dict) and value.get('__scpl_result__') == 'error'

    def _unwrap(self, value, default=None):
        if self._is_ok(value):
            return value.get('value')
        if self._is_error(value):
            return default
        return value

    def _error_message(self, value):
        if self._is_error(value):
            return value.get('message')
        return None

    def _try_eval(self, *body):
        try:
            result = None
            for expr in body:
                result = self.exec(expr)
                if self._is_error(result):
                    return result
            return self._ok(result)
        except Exception as exc:
            return self._error(str(exc))
    
    # ── Триггеры ──
    def _trigger(self, name, *actions):
        self._current_scope()[f'trig_{name}'] = True
        for action in actions:
            self.exec(action)
    
    def _on_event(self, event, *actions):
        self._current_scope()[f'event_{event}'] = actions
    
    # ── Мета ──
    def _eval(self, code):
        parser = SCPLParser()
        if isinstance(code, list):
            return self.exec(code)
        try:
            asts = parser.parse(str(code))
        except SCPLParseError as exc:
            return self._error(
                f"parse error: {exc.message}",
                {
                    'line': exc.line,
                    'column': exc.column,
                },
            )
        result = None
        for a in asts:
            result = self.exec(a)
        return result

# ═══════════════════════════════
# ENGINE
# ═══════════════════════════════
class SCPLEngine:
    VERSION = "2.0.0"
    
    def __init__(self):
        self.env = SCPLEnvironment()
        self.ai = AICreator()
        self.gl = SCPLGL()
        self.sound = SCPLSound()
        self.parser = SCPLParser()
        
        self.env.builtins['ai-create'] = self.ai.create_network
        self.env.builtins['ai-predict'] = self.ai.predict
        self.env.builtins['ai-mutate'] = self.ai.mutate
        self.env.builtins['ai-save'] = self.ai.save
        self.env.builtins['ai-load'] = self.ai.load
        
        self.env.builtins['3d-cube'] = self.gl.create_cube
        self.env.builtins['3d-sphere'] = self.gl.create_sphere
        self.env.builtins['3d-delete'] = self.gl.delete_object
        self.env.builtins['3d-move'] = self.gl.move_object
        self.env.builtins['3d-rotate'] = self.gl.rotate_object
        self.env.builtins['3d-color'] = self.gl.set_color
        self.env.builtins['3d-position'] = self.gl.get_position
        self.env.builtins['3d-collision'] = self.gl.check_collision
        self.env.builtins['3d-list'] = self.gl.list_objects
        self.env.builtins['3d-count'] = self.gl.count_objects
        
        self.env.builtins['Sound-play'] = self.sound.play
        self.env.builtins['Sound-stop'] = self.sound.stop
        self.env.builtins['Sound-volume'] = self.sound.set_volume
        self.env.builtins['Sound-info'] = self.sound.info
    
    def run_file(self, path):
        p = Path(path)
        if not p.exists():
            print(f"[SCPL] File not found: {path}")
            return
        print(f"[SCPL] Running: {path}")
        code = p.read_text(encoding='utf-8')
        self.run_code(code)
    
    def run_code(self, code):
        try:
            asts = self.parser.parse(code)
        except SCPLParseError as exc:
            return self.env._error(
                f"parse error: {exc.message}",
                {
                    'line': exc.line,
                    'column': exc.column,
                },
            )
        for ast in asts:
            self.env.exec(ast)
        return None
    
    def get_state(self):
        return {
            'version': self.VERSION,
            'variables': self.env.vars,
            'functions': list(self.env.funcs.keys()),
            '3d_objects': self.gl.list_objects(),
            'networks': list(self.ai.networks.keys()),
            'sound': self.sound.info(),
        }

if __name__ == "__main__":
    engine = SCPLEngine()
    print(f"[SCPL] Engine v{engine.VERSION} loaded")
    
    if not Path("hello.scpl").exists():
        Path("hello.scpl").write_text("""Initialize-console
Console-print: 'Hello from SCPL v2.0!'
Close-console""")
    
    engine.run_file("hello.scpl")
    print("Ready!")
