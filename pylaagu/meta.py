import sys
import ast
import typing


# Private helpers

def __toobj_function_arg(arg: ast.arg):
    retval = {"name": arg.arg}
    if arg.annotation:
        retval["type"] = ast.unparse(arg.annotation).strip()
    return retval


def __toobj_function_args(f: ast.FunctionDef):
    return [__toobj_function_arg(arg) for arg in f.args.args]


def __toobj_function(f: ast.FunctionDef):
    return {
        "name": f.name,
        "type": "function",
        "args": __toobj_function_args(f),
        "returns": ast.unparse(f.returns) if f.returns else None
    }


def __functions_at_node(node: ast.AST,
                        name_filter: typing.Callable =
                        lambda x: True) -> typing.List[ast.FunctionDef]:
    return [n for n in node.body
            if isinstance(n, ast.FunctionDef) and name_filter(n.name)]


def __classes_at_node(node: ast.AST) -> typing.List[ast.ClassDef]:
    return [n for n in node.body if isinstance(n, ast.ClassDef)]


def __toobj_class_functions(c: ast.ClassDef, name_filter=lambda x: True):
    class_functions = __functions_at_node(c, name_filter)
    return {"name": c.name,
            "type": "class",
            "functions": [__toobj_function(f) for f in class_functions]}


# Public API

def extract_function_signatures(filepath: str,
                                name_filter: typing.Callable = lambda x: True):
    signatures = []
    with open(filepath, "r") as f:
        node = ast.parse(f.read(), filename=filepath)
    for c in __classes_at_node(node):
        signatures.append(__toobj_class_functions(c, name_filter))
    for f in __functions_at_node(node, name_filter):
        signatures.append(__toobj_function(f))
    return signatures


# CLI

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path>")
        sys.exit(1)
    from .utils import is_public
    output = extract_function_signatures(sys.argv[1],
                                         name_filter=is_public)
    # JSON
    import json
    print("JSON:")
    print(json.dumps(output, indent=2))
    # YAML
    import yaml
    print("\nYAML:")
    print(yaml.dump(output, sort_keys=False))
