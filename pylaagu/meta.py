import sys
import ast
import typing
import importlib.util as iu


class FunctionSignature(dict):
    def __init__(self, name: str, args: list[object], docstring: str, returns):
        self.name = name
        self.args = args
        self.docstring = docstring
        self.returns = returns

    def __repr__(self):
        return f"FunctionSignature: {self.name}, {self.args}, "
        "{self.docstring}, {self.returns}"


class ClassSignature(dict):
    def __init__(self, name: str,
                 functions: list[FunctionSignature], docstring: str):
        self.name: str = name
        self.functions: list[FunctionSignature] = functions
        self.docstring: str = docstring

    def __str__(self):
        return f"ClassSignature: {self.name}, {self.functions}"


# Private helpers

def __encode_function_arg(arg: ast.arg):
    retval = {"name": arg.arg}
    if arg.annotation:
        retval["type"] = ast.unparse(arg.annotation).strip()
    return retval


def __encode_function_args(f: ast.FunctionDef):
    return [__encode_function_arg(arg) for arg in f.args.args]


def __encode_function(f: ast.FunctionDef):
    return FunctionSignature(f.name,
                             __encode_function_args(f),
                             ast.get_docstring(f),
                             ast.unparse(f.returns)
                             if f.returns else None)


def __functions_at_node(node: ast.AST,
                        name_filter: typing.Callable =
                        lambda x: True) -> typing.List[ast.FunctionDef]:
    return [n for n in node.body
            if isinstance(n, ast.FunctionDef) and name_filter(n.name)]


def __classes_at_node(node: ast.AST) -> typing.List[ast.ClassDef]:
    return [n for n in node.body if isinstance(n, ast.ClassDef)]


def __encode_class_functions(c: ast.ClassDef, name_filter=lambda x: True):
    class_functions = __functions_at_node(c, name_filter)
    return ClassSignature(c.name, [__encode_function(f) for f in class_functions],
                          ast.get_docstring(c))


# Public API

def extract_function_signatures(filepath: str,
                                name_filter: typing.Callable = lambda x: True):
    signatures = []
    with open(filepath, "r") as f:
        node = ast.parse(f.read(), filename=filepath)
    for f in __functions_at_node(node, name_filter):
        signatures.append(__encode_function(f))
    return signatures


def extract_class_signatures(filepath: str,
                             name_filter: typing.Callable = lambda x: True):
    signatures = []
    with open(filepath, "r") as f:
        node = ast.parse(f.read(), filename=filepath)
    for c in __classes_at_node(node):
        signatures.append(__encode_class_functions(c, name_filter))
    return signatures


def load_module_from_spec(spec):
    mod = iu.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_module(module, file=None):
    if file is None:
        spec = iu.find_spec(module)
    else:
        spec = iu.spec_from_file_location(module, file)
    return load_module_from_spec(spec), spec.origin


# CLI

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(f"Usage: python {sys.argv[0]} <path>")
        sys.exit(1)
    from .utils import is_public
    functions = extract_function_signatures(sys.argv[1],
                                            name_filter=is_public)
    classes = extract_class_signatures(sys.argv[1],
                                       name_filter=is_public)
    # JSON
    import json
    print("JSON:")
    print(json.dumps([signature for signature in functions], indent=2))
    print(json.dumps([signature for signature in classes], indent=2))
    # YAML
    import yaml
    print("\nYAML:")
    print(yaml.dump(functions, sort_keys=False))
    print(yaml.dump(classes, sort_keys=False))
