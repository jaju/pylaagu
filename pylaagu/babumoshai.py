import sys
import json
from .meta import *
from .utils import *


def to_pod_namespaced_format(filepath: str, namespace: str):
    signatures = extract_function_signatures(filepath,
                                             name_filter=lambda x:
                                             not x.startswith("_"))
    standalone_functions = [x for x in signatures if x["type"] == "function"]
    return {"name": namespace,
            "vars": standalone_functions}


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} <path> <namespace>")
        sys.exit(1)
    outstring = json.dumps(to_pod_namespaced_format(sys.argv[1], sys.argv[2]), indent=2)
    print(outstring)
