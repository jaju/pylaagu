import sys
import json
from .meta import extract_function_signatures


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
                                            name_filter=lambda x: not x.startswith("_"))
    outstring = json.dumps(to_pod_namespaced_format(namespace, functions),
                           indent=2)
    print(outstring)
