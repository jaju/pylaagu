import sys
import json
from .meta import extract_function_signatures, load_module
from .utils import is_public, to_snake, to_kebab
from types import ModuleType
from inspect import getmembers, isfunction
import functools


class Namespace:
    def __init__(self, namespace, signatures, module=None):
        self.namespace = namespace
        self.signatures = signatures
        self.module = module

    def __str__(self):
        return f"Namespace: {self.namespace}, {self.signatures}"


@functools.cache
def __split_var(var):
    ns, f = var.split("/")
    f = to_snake(f)
    return ns, f


def load_namespaces(namespaces_and_modules):
    namespaces = {}
    for namespace, module in namespaces_and_modules:
        mod, file = load_module(module)
        signatures = extract_function_signatures(file,
                                                 name_filter=is_public)
        ns = Namespace(namespace, signatures, mod)
        namespaces[namespace] = ns
    return namespaces


def load_namespaces_from_files(files_namespaces_and_modules):
    namespaces = {}
    for file, namespace, module in files_namespaces_and_modules:
        mod = load_module(module, file)
        signatures = extract_function_signatures(file,
                                                 name_filter=is_public)
        ns = Namespace(namespace, signatures, mod)
        namespaces[namespace] = ns
    return namespaces


def dispatch(namespaces, var, args):
    ns, f = __split_var(var)
    module = namespaces[ns].module
    return getattr(module, f)(*args)


def to_pod_namespaced_format(namespace: str,
                             signatures_or_module: list[object] | ModuleType) -> dict[object]:
    if isinstance(signatures_or_module, list):
        functions = [{"name": to_kebab(x["name"])}
                     for x in signatures_or_module if x["type"] == "function"]
    else:
        functions = [{"name": x[0]}
                     for x in getmembers(signatures_or_module, isfunction)]
    return {"name": namespace,
            "vars": functions}


# CLI
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print(f"Usage: python {sys.argv[0]} <namespace> <filepath>")
        sys.exit(1)
    namespace = sys.argv[1]
    filepath = sys.argv[2]
    functions = extract_function_signatures(filepath,
                                            name_filter=is_public)
    outstring = json.dumps(to_pod_namespaced_format(namespace, functions),
                           indent=2)
    print(outstring)
