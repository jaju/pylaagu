import functools
import sys
from inspect import getmembers, isfunction
from os.path import abspath
from typing import Callable

from .meta import function_signatures, load_module, FunctionSignature
from .utils import is_public, to_snake, to_kebab, debug


class Namespace:
    def __init__(self, name: str, vars: list[object], module):
        self.name: str = name
        self.vars: list[object] = vars
        self.module = module

    def __repr__(self):
        return f"%r(this={self.name}, vars={self.vars}, module={self.module})" % self.name

    def get(self, item):
        return next((x for x in self.vars if x["name"] == item), None)


class NSExportSpec:
    def __init__(self,
                 module_name: str,
                 file: str = None,
                 ns_name: str = None,
                 export_meta: bool = True,
                 export_module_imports: bool = True,
                 fail_on_error: bool = True):
        self.module_name: str = module_name
        self.ns_name: str = ns_name if ns_name else to_kebab(module_name)
        self.file: str = file
        self.export_meta: bool = export_meta
        self.export_module_imports = export_module_imports
        self.fail_on_error = fail_on_error


@functools.cache
def __split_var(var):
    ns, f = var.split("/")
    f = to_snake(f)
    return ns, f


def function_signatures_to_pod_format_functions(signatures:
                                                list[FunctionSignature],
                                                export_meta: bool = False):
    retval = []
    for signature in signatures:
        if type(signature) is FunctionSignature:
            export = {"name": to_kebab(signature.name)}
            if export_meta and signature.docstring:
                export["meta"] = f"{{:doc \"{signature.docstring}\"}}"
            retval.append(export)
    return retval


def module_to_pod_format_functions(module,
                                   export_meta: bool = False,
                                   export_module_imports: bool = False,
                                   function_name_filter: Callable = is_public):
    def function_filter(x):
        return (isfunction(x) and
                (export_module_imports or x.__module__ == module.__name__) and
                function_name_filter(x.__name__))
    functions = getmembers(module, function_filter)
    retval = []
    for function_name, function_object in functions:
        export = {"name": to_kebab(function_name)}
        if export_meta and function_object.__doc__:
            export["meta"] = f"{{:doc \"{function_object.__doc__}\"}}"
        retval.append(export)
    return retval


def load_as_namespace(nsexport_spec, function_name_filter=is_public):
    if nsexport_spec.file:
        mod, resolved_file = load_module(nsexport_spec.module_name,
                                         nsexport_spec.file,
                                         fail_on_error=nsexport_spec.fail_on_error)
        if not nsexport_spec.fail_on_error and mod is None:
            debug(f"Failed to load module {nsexport_spec.module_name}. Skipping...")
            return None
        assert abspath(nsexport_spec.file) == resolved_file
        signatures = function_signatures(resolved_file,
                                         name_filter=function_name_filter)
        debug(signatures)
        vars = function_signatures_to_pod_format_functions(signatures,
                                                           nsexport_spec.export_meta)
    else:
        mod, resolved_file = load_module(nsexport_spec.module_name)
        vars = module_to_pod_format_functions(mod,
                                              nsexport_spec.export_meta,
                                              nsexport_spec.export_module_imports,
                                              function_name_filter)
    return Namespace(nsexport_spec.ns_name, vars, mod)


def load_as_namespaces(nsexport_specs, function_name_filter=is_public):
    namespaces = {}
    for nsexport_spec in nsexport_specs:
        ns = load_as_namespace(nsexport_spec, function_name_filter)
        namespaces[nsexport_spec.ns_name] = ns
    return namespaces


def dispatch(namespaces, var, args):
    ns, f = __split_var(var)
    module = namespaces[ns].module
    if args:
        return getattr(module, f)(*args)
    else:
        return getattr(module, f)()


def to_pod_namespaced_format(ns: Namespace) -> dict[str, str | list[object]]:
    return {"name": ns.name,
            "vars": ns.vars}


# CLI

def _main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <module-name> "
              "[filepath] [namespace]")
        sys.exit(1)
    module_name = sys.argv[1]
    filepath = sys.argv[2] if len(sys.argv) > 2 else None
    namespace = sys.argv[3] if len(sys.argv) == 4 else None
    ns = load_as_namespace(NSExportSpec(module_name, filepath, namespace, False, True))
    export = to_pod_namespaced_format(ns)
    import pprint
    pprint.pp(export)


if __name__ == "__main__":
    _main()
