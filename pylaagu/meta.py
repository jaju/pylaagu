import ast
import importlib.util as iu
import sys
import typing


class FunctionSignature(dict):
    """Holds function signature information."""
    def __init__(self, name: str, args: list[object], vararg, kwarg, returns, docstring: str):
        super().__init__()
        self.name = name
        self.args = args or []
        self.vararg = vararg or False
        self.kwarg = kwarg or False
        self.returns = returns or None
        self.docstring = docstring or None

    def __doc(self):
        return f"\nDoc: ''':{self.docstring}'''" if self.docstring else ""

    def __repr__(self):
        args = ", ".join(s['name'] for s in self.args)
        if self.vararg:
            args += ", *" + self.vararg["name"]
        if self.kwarg:
            args += ", **" + self.kwarg["name"]
        return f"def {self.name}({args}) -> {self.returns}" + self.__doc()

    def __encode__(self):
        return {"name": self.name,
                "args": [arg for arg in self.args if arg is not None and arg["name"] != "self"],
                "varargs": self.vararg,
                "kwargs": self.kwarg,
                "returns": self.returns,
                "docstring": self.docstring}

    def encode(self):
        return {k:v for k, v in self.__encode__().items() if v is not None}


class ClassSignature(dict):
    """Holds class functions signature information."""
    def __init__(self, name: str, docstring: str, functions: list[FunctionSignature]):
        super().__init__()
        self.name: str = name
        self.docstring: str = docstring
        self.functions: list[FunctionSignature] = functions

    def __doc(self):
        return f"''': Doc:: {self.docstring}'''\n" if self.docstring else ""

    def __str__(self):
        return f"class {self.name}:\n" + self.__doc() + "\n" + "\n".join(map(str, self.functions))

    def __encode__(self):
        return {"name": self.name,
                "docstring": self.docstring,
                "functions": [f.encode() for f in self.functions]}

    def encode(self):
        return {k:v for k, v in self.__encode__().items() if v}


# Private helpers

def __encode_function_arg(arg: ast.arg):
    retval = {"name": arg.arg}
    if arg.annotation:
        retval["type"] = ast.unparse(arg.annotation).strip()
    return retval


def __encode_function_args(f: ast.FunctionDef):
    return [__encode_function_arg(arg) for arg in f.args.args]


def __encode_function_vararg(f: ast.FunctionDef) -> dict | None:
    if f.args.vararg:
        return {"name": f.args.vararg.arg}
    else:
        return None


def __encode_function_kwarg(f: ast.FunctionDef) -> str | None:
    if f.args.kwarg:
        return {"name": f.args.kwarg.arg}
    else:
        return None

def __encode_function(f: ast.FunctionDef) -> FunctionSignature:
    return FunctionSignature(f.name, __encode_function_args(f), __encode_function_vararg(f), __encode_function_kwarg(f),
                             ast.unparse(f.returns) if f.returns else None, ast.get_docstring(f))


def __functions_at_node(node: ast.AST,
                        name_filter: typing.Callable =
                        lambda x: True) -> typing.List[ast.FunctionDef]:
    return [n for n in node.body
            if isinstance(n, ast.FunctionDef) and name_filter(n.name)]


def __classes_at_node(node: ast.AST) -> typing.List[ast.ClassDef]:
    return [n for n in node.body if isinstance(n, ast.ClassDef)]


def __encode_class(c: ast.ClassDef, name_filter=lambda x: True):
    class_functions = __functions_at_node(c, name_filter)
    return ClassSignature(c.name, ast.get_docstring(c), [__encode_function(f) for f in class_functions])


# Public API

def function_signatures(filepath: str,
                        name_filter: typing.Callable = lambda x: True) -> list[FunctionSignature]:
    """Extracts function signatures from a python file.
    Args:
        filepath (str): Path to the python file.
        name_filter (typing.Callable, optional): Function to filter function names. Default is to accept all names.
    """
    signatures = []
    with open(filepath, "r") as f:
        node = ast.parse(f.read(), filename=filepath)
    for f in __functions_at_node(node, name_filter):
        signatures.append(__encode_function(f))
    return signatures


def class_signatures(filepath: str,
                     name_filter: typing.Callable = lambda x: True) -> list[ClassSignature]:
    """Extracts all class signatures from the python file.
    Args:
        filepath (str): Path to the python file.
        name_filter (typing.Callable, optional): Function to filter class names. Default is to accept all names.
    """
    signatures = []
    with open(filepath, "r") as f:
        node = ast.parse(f.read(), filename=filepath)
    for c in __classes_at_node(node):
        signatures.append(__encode_class(c, name_filter))
    return signatures


def __load_module_from_spec(spec):
    mod = iu.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def load_module(module_name: str, file: str = None, fail_on_error=True):
    """Loads a module by name or file path. Returns the module and the file path discovered from the loaded spec."""
    if file is None:
        spec = iu.find_spec(module_name)
    else:
        spec = iu.spec_from_file_location(module_name, file)
    if spec is None:
        if fail_on_error:
            raise ImportError(f"Could not find module {module_name}")
        else:
            return None, None
    try:
        mod = __load_module_from_spec(spec)
    except FileNotFoundError as e:
        if fail_on_error:
            raise e
        else:
            return None, None
    return mod, spec.origin

# CLI

def example_function(arg1=True, arg2=False, *args, **kwargs) -> int:
    """This exists only to understand, track and demonstrate how more exotic function signatures are handled."""
    print("First argument:", arg1)
    print("Second argument:", arg2)
    print("Positional arguments (*args):", args)
    print("Keyword arguments (**kwargs):", kwargs)
    return 1

def _main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <filepath>")
        sys.exit(1)
    filepath = sys.argv[1]

    function_sigs = function_signatures(filepath)
    if len(function_sigs) > 0:
        print("Function signatures:")
        print("--------------------")
        for sig in function_sigs:
            print(sig)
        print("\n")

    class_sigs = class_signatures(filepath)
    if len(class_sigs) > 0:
        print("Class signatures:")
        print("-----------------")
        for sig in class_sigs:
            print("<BEGIN>")
            print(sig)
            print("<END>")
        print("\n")


if __name__ == "__main__":
    _main()
