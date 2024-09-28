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
from pylaagu.meta import extract_function_signatures, extract_class_signatures
functions = extract_function_signatures(file, name_filter=is_public)
classes = extract_class_signatures(file, name_filter=is_public)

if output_format == "json":
    import json
    print(json.dumps([signature.__dict__ for signature in functions], indent=2))
    print(json.dumps([signature.__dict__ for signature in classes], indent=2))
elif output_format == "yaml":
    import yaml
    print(yaml.dump(functions, sort_keys=False))
    print(yaml.dump(classes, sort_keys=False))
else:
    print("Invalid output format. Choose either 'json' or 'yaml'")
    sys.exit(1)
