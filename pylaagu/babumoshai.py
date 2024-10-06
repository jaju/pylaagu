import functools
import sys
from inspect import getmembers
from typing import Callable

from .meta import load_module
from .utils import is_public, to_snake, to_kebab, debug

import logging

logger = logging.getLogger(__name__)


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
                 ns_name: str = None,
                 export_meta: bool = True,
                 export_module_imports: bool = True,
                 fail_on_error: bool = True):
        self.module_name: str = module_name
        self.ns_name: str = ns_name if ns_name else to_kebab(module_name)
        self.export_meta: bool = export_meta
        self.export_module_imports = export_module_imports
        self.fail_on_error = fail_on_error


@functools.cache
def __split_var(var):
    ns, f = var.split("/")
    f = to_snake(f)
    return ns, f


def module_to_pod_format_functions(module,
                                   export_meta: bool = False,
                                   function_filter: Callable = lambda x: True):
    functions = getmembers(module, function_filter)
    retval = []
    for function_name, function_object in functions:
        kebab_case_name = to_kebab(function_name)
        export = {"name": kebab_case_name}
        if export_meta and function_object.__doc__:
            export["meta"] = '{{:doc "{doc_string}"}}'.format(doc_string=function_object.__doc__)  # "{:doc " + function_object.__doc__ + "}"
        retval.append(export)
    return retval


def __short_name(obj):
    if hasattr(obj, '__name__'):
        return(obj.__name__)  # For functions or modules
    elif hasattr(obj, '__class__'):
        return(obj.__class__.__name__)  # For objects
    else:
        return("Unknown type")


def load_as_namespace(nsexport_spec, function_name_filter=is_public):
    module, resolved_file = load_module(nsexport_spec.module_name,
                                        fail_on_error=nsexport_spec.fail_on_error)

    def function_filter(x):
        result = (callable(x) and
                  not isinstance(x, type) and
                  (nsexport_spec.export_module_imports or x.__module__ == module.__name__) and
                  hasattr(x, "__name__") and
                  function_name_filter(x.__name__))
        if not result and hasattr(x, '__module__') and x.__module__ == module.__name__:
            logger.debug(f" Not exporting --- {__short_name(x)}: callable? {callable(x)}, type? {type(x)}, module? {x.__module__ if hasattr(x, '__module__') else None}, name? {x.__name__ if hasattr(x, '__name__') else None}")
        return result

    if not nsexport_spec.fail_on_error and module is None:
        logger.error(f"Failed to load module {nsexport_spec.module_name}. Skipping...")
        return None

    vars = module_to_pod_format_functions(module,
                                          nsexport_spec.export_meta,
                                          function_filter)

    return Namespace(nsexport_spec.ns_name, vars, module)


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


def to_pod_export_format(ns: Namespace) -> dict[str, str | list[object]]:
    return {"name": ns.name,
            "vars": ns.vars}


# CLI
def _main():
    if len(sys.argv) < 2:
        print(f"Usage: python {sys.argv[0]} <module-name> [namespace]")
        sys.exit(1)
    module_name = sys.argv[1]
    namespace = sys.argv[2] if len(sys.argv) == 3 else None
    ns = load_as_namespace(NSExportSpec(module_name, namespace, True, True))
    export = to_pod_export_format(ns)
    print(export)


if __name__ == "__main__":
    _main()
