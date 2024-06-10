import sys
from .meta import extract_function_signatures, load_module, FunctionSignature
from .utils import is_public, to_snake, to_kebab, debug
from inspect import getmembers, isfunction
import functools
from os.path import abspath


class Namespace:
    def __init__(self, name, vars, module):
        self.name = name
        self.vars = vars
        self.module = module

    def __repr__(self):
        return f"Namespace: {self.name}, {self.vars}"


class NSExportSpec:
    def __init__(self, module_name, file=None, ns_name=None):
        self.module_name = module_name
        self.ns_name = ns_name if ns_name else to_kebab(module_name)
        self.file = file


@functools.cache
def __split_var(var):
    ns, f = var.split("/")
    f = to_snake(f)
    return ns, f


def function_signatures_to_pod_format_functions(signatures: list[FunctionSignature]):
    retval = []
    for signature in signatures:
        if type(signature) is FunctionSignature:
            export = {"name": to_kebab(signature.name)}
            if signature.docstring:
                export["meta"] = f"{{:doc \"{signature.docstring}\"}}"
            retval.append(export)
    return retval


def module_to_pod_format_functions(modules):
    def function_filter(x):
        return isfunction(x) and is_public(x.__name__)
    functions = getmembers(modules, function_filter)
    retval = []
    for function in functions:
        export = {"name": to_kebab(function[0])}
        if function.__doc__:
            export["meta"] = f"{{:doc \"{function.__doc__}\"}}"
        retval.append(export)
    return retval


def load_namespace(nsexport_spec):
    if nsexport_spec.file:
        mod, resolved_file = load_module(nsexport_spec.module_name,
                                         nsexport_spec.file)
        assert abspath(nsexport_spec.file) == resolved_file
        signatures = extract_function_signatures(resolved_file,
                                                 name_filter=is_public)
        debug(signatures)
        vars = function_signatures_to_pod_format_functions(signatures)
    else:
        mod, resolved_file = load_module(nsexport_spec.module_name)
        vars = module_to_pod_format_functions(mod)
    return Namespace(nsexport_spec.ns_name, vars, mod)


def load_namespaces(nsexport_specs):
    namespaces = {}
    for nsexport_spec in nsexport_specs:
        ns = load_namespace(nsexport_spec)
        namespaces[nsexport_spec.ns_name] = ns
    return namespaces


def dispatch(namespaces, var, args):
    ns, f = __split_var(var)
    module = namespaces[ns].module
    return getattr(module, f)(*args)


def to_pod_namespaced_format(ns: Namespace) -> dict[object]:
    return {"name": ns.name,
            "vars": ns.vars}


# CLI
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <module-name> "
              "[filepath] [namespace]")
        sys.exit(1)
    module_name = sys.argv[1]
    filepath = sys.argv[2] if len(sys.argv) > 2 else None
    namespace = sys.argv[3] if len(sys.argv) == 4 else None
    ns = load_namespace(NSExportSpec(module_name, filepath, namespace))
    export = to_pod_namespaced_format(ns)
    import pprint
    pprint.pp(export)
