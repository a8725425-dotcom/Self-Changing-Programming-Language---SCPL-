# scpl_engine.py - SCPL Engine v2.0 (ПОЛНЫЙ ФИКС ПАРСЕРА)
import os
import random
import json
import time
from pathlib import Path
from typing import List, Any

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
    
    def play(self, name):
        print(f"[Sound] Playing: {name}")
        return f"Playing {name}"
    
    def stop(self, name):
        print(f"[Sound] Stopped: {name}")
    
    def set_volume(self, vol):
        self.volume = max(0, min(1, vol))

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
        i = 0
        lines = code.split('\n')
        
        for line in lines:
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
                    i += 1
                    s = ''
                    while i < len(stripped) and stripped[i] != quote:
                        if stripped[i] == '\\' and i + 1 < len(stripped):
                            i += 1
                        s += stripped[i]
                        i += 1
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
                        parts.append(token[1:-1])
                    elif isinstance(token, str) and token.startswith('"') and token.endswith('"'):
                        parts.append(token[1:-1])
                    else:
                        parts.append(token)
                    i += 1
        
        if i < len(tokens) and tokens[i] == ')':
            i += 1
        
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
                    args.append(token[1:-1])
                elif isinstance(token, str) and token.startswith('"') and token.endswith('"'):
                    args.append(token[1:-1])
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
        self.vars = {}
        self.funcs = {}
        self.log = []
        self.console_on = False
        self.return_value = None
        self.loop_control = None
        self.modules = {}
        self._if_active = False
        
        self.builtins = {
            # Консоль
            'import': self._import,
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
            'call': self._call_function,
            'return': self._return,
            
            # Списки
            'list': lambda *args: list(args),
            'append': self._append,
            'length': lambda x: len(x) if hasattr(x, '__len__') else 1,
            'nth': lambda lst, n: lst[n] if isinstance(lst, list) and 0 <= n < len(lst) else None,
            
            # Строки
            'concat': lambda *args: ''.join(str(a) for a in args),
            'upper': lambda s: str(s).upper(),
            'lower': lambda s: str(s).lower(),
            'split': lambda s, d=' ': str(s).split(d),
            'join': lambda d, *args: str(d).join(str(a) for a in args),
            
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
            
            # Триггеры
            'trigger': self._trigger,
            'on': self._on_event,
            
            # Типы
            'type': lambda x: type(x).__name__,
            
            # Мета
            'eval': self._eval,
        }
    
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
        if isinstance(ast, str):
            if ast in self.vars:
                return self.vars[ast]
            return ast
        if not isinstance(ast, list) or len(ast) == 0:
            return ast
        
        fn = ast[0]

        # Специальные формы получают часть аргументов как AST, без раннего вычисления.
        if fn in ('function',):
            return self.builtins[fn](ast[1], ast[2], *ast[3:])
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
            elif isinstance(a, str):
                if a in self.vars:
                    args.append(self.vars[a])
                else:
                    args.append(a)
            else:
                args.append(a)
        
        if fn in self.builtins:
            return self.builtins[fn](*args)
        elif fn in self.funcs:
            func_body = self.funcs[fn]
            old_vars = self.vars.copy()
            if 'params' in func_body:
                for i, param in enumerate(func_body['params']):
                    if i < len(args):
                        self.vars[param] = args[i]
            result = None
            for expr in func_body['body']:
                result = self.exec(expr)
                if self.return_value is not None:
                    result = self.return_value
                    self.return_value = None
                    break
            self.vars = old_vars
            return result
        else:
            print(f"[SCPL] Unknown: {fn}")
            return None
    
    # ── Модули ──
    def _import(self, name=None):
        if not name:
            return "Library name required"
        
        engine_dir = Path(__file__).parent
        lib_path = engine_dir / "libs" / name
        
        if lib_path.exists():
            init_scpl = lib_path / "__init__.scpl"
            if init_scpl.exists():
                code = init_scpl.read_text(encoding='utf-8')
                parser = SCPLParser()
                asts = parser.parse(code)
                for ast in asts:
                    self.exec(ast)
                self.modules[name] = True
                return f"Loaded library: {name}"
            else:
                return f"Library '{name}' has no __init__.scpl"
        
        self.modules[name] = True
        return f"Loaded {name}"
    
    # ── Консоль ──
    def _init_console(self):
        self.console_on = True
        self.log = []
        print("[SCPL Console] ON")
    
    def _print(self, *args):
        if not self.console_on:
            print("[SCPL Error] Console not initialized!")
            return
        msg = ' '.join(str(a) for a in args)
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
        self.vars[name] = value
        return value
    
    def _get(self, name):
        return self.vars.get(name, f"Error: {name} not found")
    
    def _delete(self, name):
        if name in self.vars:
            del self.vars[name]
    
    def _var_exists(self, name):
        return name in self.vars
    
    def _list_vars(self):
        return list(self.vars.keys())
    
    # ── Условия ──
    def _if(self, condition, *body):
        if condition:
            result = None
            for expr in body:
                result = self.exec(expr)
                if self.return_value is not None:
                    return result
            return result
        return None
    
    def _else(self, *args):
        pass  # Обрабатывается в _if
    
    # ── Циклы ──
    def _loop(self, count, *body):
        for _ in range(int(count)):
            for expr in body:
                self.exec(expr)
    
    def _for(self, var_name, start, end, *body):
        for i in range(int(start), int(end)):
            self.vars[var_name] = i
            for expr in body:
                self.exec(expr)
    
    def _while(self, condition, *body):
        while self.exec(condition):
            for expr in body:
                self.exec(expr)
    
    def _break(self):
        self.loop_control = 'break'
    
    def _continue(self):
        self.loop_control = 'continue'
    
    # ── Функции ──
    def _def_function(self, name, params, *body):
        """Определяет функцию: (function name (p1 p2) body...)"""
        param_list = params if isinstance(params, list) else [params]
        self.funcs[name] = {
            'params': [p for p in param_list if isinstance(p, str)],
            'body': list(body)
        }
        return f"Function {name} defined"
    
    def _call_function(self, name, *args):
        if name in self.funcs:
            func = self.funcs[name]
            old_vars = self.vars.copy()
            for i, param in enumerate(func['params']):
                if i < len(args):
                    self.vars[param] = args[i]
            result = None
            for expr in func['body']:
                result = self.exec(expr)
            self.vars = old_vars
            return result
        return f"Function {name} not found"
    
    def _return(self, value=None):
        self.return_value = value
        return value
    
    # ── Списки ──
    def _append(self, lst, value):
        if isinstance(lst, list):
            lst.append(value)
            return lst
    
    # ── Ввод ──
    def _input_wait(self, prompt=""):
        return input(str(prompt))
    
    def _input_last(self):
        return getattr(self, '_last_input', "")
    
    # ── Триггеры ──
    def _trigger(self, name, *actions):
        self.vars[f'trig_{name}'] = True
        for action in actions:
            self.exec(action)
    
    def _on_event(self, event, *actions):
        self.vars[f'event_{event}'] = actions
    
    # ── Мета ──
    def _eval(self, code):
        parser = SCPLParser()
        asts = parser.parse(str(code))
        for a in asts:
            self.exec(a)

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
    
    def run_file(self, path):
        p = Path(path)
        if not p.exists():
            print(f"[SCPL] File not found: {path}")
            return
        print(f"[SCPL] Running: {path}")
        code = p.read_text(encoding='utf-8')
        self.run_code(code)
    
    def run_code(self, code):
        asts = self.parser.parse(code)
        for ast in asts:
            self.env.exec(ast)
    
    def get_state(self):
        return {
            'version': self.VERSION,
            'variables': self.env.vars,
            'functions': list(self.env.funcs.keys()),
            '3d_objects': self.gl.list_objects(),
            'networks': list(self.ai.networks.keys()),
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
