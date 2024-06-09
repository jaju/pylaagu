import sys
import json
import importlib.util as iu
from .meta import extract_function_signatures
from .utils import is_public


class Namespace:
    def __init__(self, namespace, signatures, module=None):
        self.namespace = namespace
        self.signatures = signatures
        self.module = module

    def __str__(self):
        return f"Namespace: {self.namespace}, {self.signatures}"


def __split_var(var):
    return var.split("/")


def load_module(file, module):
    spec = iu.spec_from_file_location(module, file)
    mod = iu.module_from_spec(spec)
    sys.modules[module] = mod
    spec.loader.exec_module(mod)
    return mod


def load_namespaces(files_namespaces_and_modules):
    namespaces = {}
    for file, namespace, module in files_namespaces_and_modules:
        mod = load_module(file, module)
        signatures = extract_function_signatures(file,
                                                 name_filter=is_public)
        ns = Namespace(namespace, signatures, mod)
        namespaces[namespace] = ns
    return namespaces


def dispatch(namespaces, var, args):
    ns, f = __split_var(var)
    module = namespaces[ns].module
    return getattr(module, f)(*args)


def to_pod_namespaced_format(namespace: str, signatures: list[object]) -> dict[object]:
    functions = [{"name": x["name"]}
                 for x in signatures if x["type"] == "function"]
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
