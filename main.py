import sys
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-o", "--output-format", dest="output_format", default="json")

(options, args) = parser.parse_args()
file = args[0]
output_format = options.output_format

if len(args) != 1:
    print(f"Usage: python {args[0]} <path>")
    sys.exit(1)

from pylaagu.utils import is_public
from pylaagu.meta import function_signatures, class_signatures
functions = function_signatures(file, name_filter=is_public)
classes = class_signatures(file, name_filter=is_public)

def underlined_string(s: str) -> str:
    return s + "\n" + "-" * len(s)

if output_format == "json":
    import json
    if functions:
        print(underlined_string("Functions"))
        print(json.dumps([signature.encode() for signature in functions], indent=2))
    if classes:
        print(underlined_string("Classes"))
        print(json.dumps([signature.encode() for signature in classes], indent=2))
elif output_format == "yaml":
    import yaml
    yaml.emitter.Emitter.prepare_tag = lambda self, tag: '' # https://github.com/yaml/pyyaml/issues/408#issuecomment-673067702
    print(underlined_string("Functions"))
    print(yaml.dump(functions, sort_keys=False))
    print(underlined_string("Classes"))
    print(yaml.dump(classes, sort_keys=False))
else:
    print("Invalid output format. Choose either 'json' or 'yaml'")
    sys.exit(1)
