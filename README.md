# Py.Laagu


## Sketch the functional landscape of a Python module

See the `main` function in `pylaagu/meta.py` for an example of how to use the `pylaagu.meta` module to extract the function signatures from a Python module.

```bash
python pylaagu/meta.py pylaagu/meta.py
```

Outputs:
```json
[
  {
    "name": "extract_function_signatures",
    "type": "function",
    "args": [
      {
        "name": "filepath",
        "type": "str"
      },
      {
        "name": "name_filter",
        "type": "typing.Callable"
      }
    ],
    "returns": null
  }
]
```


```yaml
- name: extract_function_signatures
  type: function
  args:
  - name: filepath
    type: str
  - name: name_filter
    type: typing.Callable
  returns: null
```

A use of this functionality can be seen in (pylaagu/babumoshai.py)[pylaagu/babumoshai.py] to generate output in the [babashka](https://babashka.org/) pod communication format.

### Babashka

You can use the `pylaagu.babumoshai` module to generate output in the [babashka](https://babashka.org/) pod communication format, plus basic code to extract instructions from the messages, *run* the code and return the response back to the calling babashka process. It's all handled for you - the input and output need to be simple enough to be serialized to JSON and back.

Here's a sample usage. The code imports the `mlexplore.hf` module which has some basic huggingface hub functions. There's a small quirk to be aware of - the `mlexplore.hf` module depends on the `mlexplore` module, so you need to import the `mlexplore` module first.


*Note*: This file is referred to as `mlexplore/pod.py` in the babashka-session code below.

```python
#!/usr/bin/env python
import sys
import json
from pylaagu.babumoshai import to_pod_namespaced_format, load_namespaces, dispatch, Namespace
from bcoding import bencode, bdecode


def debug(*args):
    print(*args, file=sys.stderr)


def read():
    return dict(bdecode(sys.stdin.buffer))


def write(obj):
    sys.stdout.buffer.write(bencode(obj))
    sys.stdout.buffer.flush()


namespaces_and_files = [
    ("mlexplore/__init__.py", "mlexplore", "mlexplore"),
    ("mlexplore/hf.py", "mlexplore.hf", "mlexplore.hf"),
]


def main():
    namespaces = load_namespaces(namespaces_and_files)
    exports = [to_pod_namespaced_format(namepace.namespace, namepace.signatures)
               for namepace in namespaces.values()]
    print(namespaces)
    while True:
        try:
            msg = read()
            op = msg.get("op")
            if op == "describe":
                write({
                    "format": "json",
                    "namespaces": exports
                })
            elif op == "invoke":
                var = msg.get("var")
                id = msg.get("id")
                args = json.loads(msg.get("args"))
                value = dispatch(namespaces, var, args)
                write({"status": ["done"], "id": id, "value": json.dumps(value)})
        except EOFError:
            print("EOF")
            break


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    else:
        filename = sys.argv[1]
        namespace = sys.argv[2]
        print(to_pod_namespaced_format(filename, namespace))
        sys.exit(0)
```

Here's a simple babashka session that uses the above script. Notice that there is no code required to dispatch to the appropriate python functions as that is automatically handled.

```bash
Babashka v1.3.190 REPL.
Use :repl/quit or :repl/exit to quit the REPL.
Clojure rocks, Bash reaches.

user=> (babashka.pods/load-pod ["./mlexplore/pod.py"])
#:pod{:id "mlexplore"}
user=> (mlexplore.hf/model_info "facebook/bart-large")
[".gitattributes" "README.md" "config.json" "flax_model.msgpack" "merges.txt" "pytorch_model.bin" "rust_model.ot" "tf_model.h5" "tokenizer.json" "tokenizer_config.json" "vocab.json"]
user=> (mlexplore.hf/url_of "foo" "bar")
"https://huggingface.co/foo/resolve/main/bar"
```

## Caching
See [pylaagu/cache.py](pylaagu/cache.py). Two annotations exist
- `@cache` to persistently cache (using sqlite3) the return value of a function. This requires calling the `init_app` function with an appname.
- `@memoize` to, well, memoize in memory the return value of a function.
