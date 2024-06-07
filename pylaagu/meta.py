import sys
import ast
import typing


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
        "returns": f.returns
    }


def extract_function_signatures(filepath: str,
                                name_filter: typing.Callable = lambda x: True):
    signatures = []
    with open(filepath, "r") as f:
        code = f.read()
    node = ast.parse(code, filename=filepath)
    functions = [n for n in node.body
                 if isinstance(n, ast.FunctionDef) and name_filter(n.name)]
    classes = [n for n in node.body if isinstance(n, ast.ClassDef)]
    for c in classes:
        class_functions = [n for n in c.body
                           if isinstance(n, ast.FunctionDef) and name_filter(n.name)]
        signatures.append({"name": c.name,
                           "type": "class",
                           "functions": [__toobj_function(f)
                                         for f in class_functions]})
    for f in functions:
        signatures.append(__toobj_function(f))
    return signatures


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <path>")
        sys.exit(1)
    import json
    import yaml
    output = extract_function_signatures(sys.argv[1],
                                         name_filter=lambda x:
                                         not x.startswith("_"))
    print(json.dumps(output, indent=2))
    print(yaml.dump(output, sort_keys=False))
