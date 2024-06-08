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


def split_var(var):
    return var.split("/")


def load_namespaces(files_namespaces_and_modules):
    namespaces = {}
    for file, namespace, module in files_namespaces_and_modules:
        spec = iu.spec_from_file_location(module, file)
        mod = iu.module_from_spec(spec)
        sys.modules[module] = mod
        spec.loader.exec_module(mod)
        ns = Namespace(namespace, extract_function_signatures(file, name_filter=is_public), mod)
        namespaces[namespace] = ns
    return namespaces


def dispatch(namespaces, var, args):
    ns, f = split_var(var)
    module = namespaces[ns].module
    return getattr(module, f)(*args)


def to_pod_namespaced_format(namespace: str, signatures: object):
    functions = [{"name": x["name"]}
                 for x in signatures if x["type"] == "function"]
    return {"name": namespace,
            "vars": functions}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <path> <namespace>")
        sys.exit(1)
    namespace = sys.argv[1]
    filepath = sys.argv[2]
    functions = extract_function_signatures(filepath,
                                            name_filter=is_public)
    outstring = json.dumps(to_pod_namespaced_format(namespace, functions),
                           indent=2)
    print(outstring)
