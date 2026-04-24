# scpl_engine.py - SCPL Engine v2.0 (ПОЛНОСТЬЮ РАБОЧАЯ ВЕРСИЯ)
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
# PARSER (ПОЛНОСТЬЮ ИСПРАВЛЕН)
# ═══════════════════════════════
class SCPLParser:
    def parse(self, code: str) -> List:
        """Парсит код SCPL в AST с поддержкой вложенных отступов."""
        if not code or not code.strip():
            return []
        lines = code.split('\n')
        expressions, _ = self._parse_block(lines, 0, 0)
        return expressions
    
    def _indent_level(self, line: str) -> int:
        indent = 0
        for ch in line:
            if ch == ' ':
                indent += 1
            elif ch == '\t':
                indent += 4
            else:
                break
        return indent
    
    def _parse_block(self, lines, start_index, base_indent):
        expressions = []
        i = start_index
        
        while i < len(lines):
            line = lines[i]
            stripped = line.strip()
            
            if not stripped or stripped.startswith('--'):
                i += 1
                continue
            
            indent = self._indent_level(line)
            if indent < base_indent:
                break
            if indent > base_indent:
                i += 1
                continue
            
            expr = self._parse_expression(stripped)
            i += 1
            
            body, i = self._parse_child_block(lines, i, base_indent)
            if body and isinstance(expr, list):
                expr.append(body)
            
            expressions.append(expr)
        
        return expressions, i
    
    def _parse_child_block(self, lines, start_index, parent_indent):
        i = start_index
        
        while i < len(lines):
            stripped = lines[i].strip()
            if not stripped or stripped.startswith('--'):
                i += 1
                continue
            
            indent = self._indent_level(lines[i])
            if indent <= parent_indent:
                return [], start_index
            return self._parse_block(lines, start_index, indent)
        
        return [], start_index
    
    def _parse_expression(self, code: str):
        """Парсит одно выражение."""
        code = code.strip()
        if not code:
            return None
        
        # Определяем тип выражения
        i = 0
        
        # S-выражение: (func arg1 arg2)
        if code[i] == '(':
            result, _ = self._parse_s_expr(code, i)
            return result
        
        # Строка в кавычках
        if code[i] in '\'"':
            result, _ = self._parse_string(code, i)
            return result
        
        # M-выражение: func: arg1 arg2 или func arg1 arg2
        return self._parse_m_expr(code)
    
    def _parse_s_expr(self, code: str, i: int):
        """Парсит S-выражение: (func arg1 arg2)"""
        i += 1  # Пропускаем '('
        parts = []
        
        while i < len(code) and code[i] != ')':
            while i < len(code) and code[i] in ' \t':
                i += 1
            
            if i >= len(code) or code[i] == ')':
                break
            
            if code[i] == '(':
                sub_expr, i = self._parse_s_expr(code, i)
                parts.append(sub_expr)
            elif code[i] in '\'"':
                string, i = self._parse_string(code, i)
                parts.append(string)
            else:
                atom, i = self._parse_atom(code, i)
                parts.append(atom)
        
        if i < len(code) and code[i] == ')':
            i += 1
        
        return parts, i
    
    def _parse_m_expr(self, code: str):
        """Парсит M-выражение: func: arg1 arg2 или func(arg1 arg2)"""
        i = 0
        code = code.strip()
        
        # Парсим имя функции (может содержать дефисы, подчёркивания, буквы, цифры)
        func_name, i = self._parse_atom(code, i)
        
        # Пропускаем пробелы
        while i < len(code) and code[i] in ' \t':
            i += 1
        
        args = []
        
        # Если есть двоеточие
        if i < len(code) and code[i] == ':':
            i += 1  # Пропускаем ':'
            # Собираем аргументы до конца строки
            while i < len(code):
                while i < len(code) and code[i] in ' \t':
                    i += 1
                
                if i >= len(code):
                    break
                
                if code[i] == '(':
                    sub_expr, i = self._parse_s_expr(code, i)
                    args.append(sub_expr)
                elif code[i] in '\'"':
                    string, i = self._parse_string(code, i)
                    args.append(string)
                else:
                    atom, i = self._parse_atom(code, i)
                    args.append(atom)
        
        # Если скобки
        elif i < len(code) and code[i] == '(':
            i += 1  # Пропускаем '('
            while i < len(code) and code[i] != ')':
                while i < len(code) and code[i] in ' \t':
                    i += 1
                
                if i >= len(code) or code[i] == ')':
                    break
                
                if code[i] == '(':
                    sub_expr, i = self._parse_s_expr(code, i)
                    args.append(sub_expr)
                elif code[i] in '\'"':
                    string, i = self._parse_string(code, i)
                    args.append(string)
                else:
                    atom, i = self._parse_atom(code, i)
                    args.append(atom)
            
            if i < len(code) and code[i] == ')':
                i += 1
        
        return [func_name] + args
    
    def _parse_string(self, code: str, i: int):
        """Парсит строку в кавычках."""
        quote = code[i]
        i += 1
        result = ''
        
        while i < len(code) and code[i] != quote:
            if code[i] == '\\' and i + 1 < len(code):
                i += 1  # Пропускаем escape-символ
            result += code[i]
            i += 1
        
        if i < len(code) and code[i] == quote:
            i += 1
        
        return result, i
    
    def _parse_atom(self, code: str, i: int):
        """Парсит атом: число или идентификатор."""
        result = ''
        
        # Собираем символы, которые могут быть в идентификаторе
        while i < len(code) and code[i] not in ' \t():\'"\n\r':
            result += code[i]
            i += 1
        
        if not result:
            return None, i
        
        # Пробуем преобразовать в число
        try:
            return int(result), i
        except ValueError:
            try:
                return float(result), i
            except ValueError:
                return result, i

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
            '+': lambda *args: sum(args),
            '-': lambda a, b=0: a - b,
            '*': lambda *args: self._mul(args),
            '/': lambda a, b: a / b if b != 0 else "Error: division by zero",
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
            'int': lambda x: int(x),
            'float': lambda x: float(x),
            'str': lambda x: str(x),
            
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
            
            # Мета
            'eval': self._eval,
            'type': lambda x: type(x).__name__,
        }
    
    def _mul(self, args):
        """Умножение с обработкой списка."""
        if not args:
            return 1
        result = 1
        for a in args:
            result *= a
        return result
    
    def exec(self, ast):
        """Исполняет AST-узел."""
        if ast is None:
            return None
        if isinstance(ast, (int, float, bool)):
            return ast
        if isinstance(ast, str):
            # Резолвим переменные
            if ast in self.vars:
                return self.vars[ast]
            return ast
        if not isinstance(ast, list) or len(ast) == 0:
            return ast
        
        fn = ast[0]
        
        # Спецформы получают сырой AST, чтобы сами решать, что и когда вычислять.
        if fn == 'set' and len(ast) >= 3:
            return self._set(ast[1], self.exec(ast[2]))
        if fn in ('if', 'when'):
            condition = self.exec(ast[1]) if len(ast) > 1 else False
            return self._if(condition, *ast[2:])
        if fn == 'else':
            return self._else(*ast[1:])
        if fn in ('loop', 'repeat') and len(ast) >= 2:
            return self._loop(self.exec(ast[1]), *ast[2:])
        if fn == 'for' and len(ast) >= 4:
            return self._for(ast[1], self.exec(ast[2]), self.exec(ast[3]), *ast[4:])
        if fn == 'while' and len(ast) >= 2:
            return self._while(ast[1], *ast[2:])
        if fn == 'function' and len(ast) >= 2:
            return self._def_function(ast[1], *ast[2:])
        if fn == 'call' and len(ast) >= 2:
            eval_args = [self.exec(a) for a in ast[2:]]
            return self._call_function(ast[1], *eval_args)
        
        args = []
        for a in ast[1:]:
            if isinstance(a, list):
                # Проверяем, список ли это выражений (тело блока)
                if a and isinstance(a[0], list):
                    # Это тело блока — передаём как есть
                    args.append(a)
                else:
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
            return self._call_function(fn, *args)
        else:
            print(f"[SCPL] Unknown: {fn}")
            return None
    
    # ── Модули ──
    def _import(self, name=None):
        if name:
            self.modules[name] = True
            return f"Loaded {name}"
        return "Module name required"
    
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
        print(f"[SCPL] Log saved: {filename}")
    
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
            self._if_active = True
            result = None
            for expr in body:
                # Если это список выражений (блок), выполняем каждое
                if isinstance(expr, list) and expr and isinstance(expr[0], list):
                    for sub_expr in expr:
                        result = self.exec(sub_expr)
                else:
                    result = self.exec(expr)
            return result
        else:
            self._if_active = False
            return None
    
    def _else(self, *body):
        if not self._if_active:
            for expr in body:
                if isinstance(expr, list) and expr and isinstance(expr[0], list):
                    for sub_expr in expr:
                        self.exec(sub_expr)
                else:
                    self.exec(expr)
    
    # ── Циклы ──
    def _loop(self, count, *body):
        for _ in range(int(count)):
            self.loop_control = None
            for expr in body:
                self._exec_body_item(expr)
                if self.loop_control == 'break':
                    break
            if self.loop_control == 'break':
                break
        self.loop_control = None
    
    def _for(self, var_name, start, end, *body):
        for i in range(int(start), int(end)):
            self.vars[var_name] = i
            self.loop_control = None
            for expr in body:
                self._exec_body_item(expr)
                if self.loop_control == 'break':
                    break
            if self.loop_control == 'break':
                break
        self.loop_control = None
    
    def _while(self, condition_expr, *body):
        while self.exec(condition_expr):
            self.loop_control = None
            for expr in body:
                self._exec_body_item(expr)
                if self.loop_control == 'break':
                    break
                if self.loop_control == 'continue':
                    break
            if self.loop_control == 'break':
                break
        self.loop_control = None
    
    def _exec_body_item(self, expr):
        """Исполняет элемент тела — может быть одиночным выражением или блоком."""
        if isinstance(expr, list) and expr and isinstance(expr[0], list):
            for sub_expr in expr:
                self.exec(sub_expr)
                if self.loop_control:
                    break
        else:
            self.exec(expr)
    
    def _break(self):
        self.loop_control = 'break'
    
    def _continue(self):
        self.loop_control = 'continue'
    
    # ── Функции ──
    def _def_function(self, name, *params_and_body):
        params = []
        body = []
        
        for i, p in enumerate(params_and_body):
            if isinstance(p, list):
                # Это тело функции
                if p and isinstance(p[0], list):
                    body = p
                else:
                    body = [p]
                break
            else:
                params.append(str(p))
        
        self.funcs[name] = {'params': params, 'body': body}
        return f"Function {name} defined"
    
    def _call_function(self, name, *args):
        if name in self.funcs:
            func = self.funcs[name]
            old_param_values = {}
            missing_params = set()
            for i, param in enumerate(func['params']):
                if param in self.vars:
                    old_param_values[param] = self.vars[param]
                else:
                    missing_params.add(param)
                if i < len(args):
                    self.vars[param] = args[i]
            result = None
            for expr in func['body']:
                result = self.exec(expr)
                if self.return_value is not None:
                    result = self.return_value
                    self.return_value = None
                    break
            for param in func['params']:
                if param in old_param_values:
                    self.vars[param] = old_param_values[param]
                elif param in missing_params:
                    self.vars.pop(param, None)
            return result
        return f"Function {name} not found"
    
    def _return(self, value=None):
        self.return_value = value
    
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
        print(f"[SCPL] Trigger: {name}")
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
        self.input_handler = SCPLInput()
        self.parser = SCPLParser()
        
        # Регистрируем модули
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

# ═══════════════════════════════
# MAIN
# ═══════════════════════════════
if __name__ == "__main__":
    engine = SCPLEngine()
    print(f"[SCPL] Engine v{engine.VERSION} loaded")
    
    # Создаём тестовый файл если нет
    if not Path("hello.scpl").exists():
        Path("hello.scpl").write_text("""import os
Initialize-console
Console-print: 'Hello from SCPL v2.0!'
Close-console""")
    
    engine.run_file("hello.scpl")
    print("Ready!")
