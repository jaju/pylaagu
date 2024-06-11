# Py.Laagu

Python utilities for building upon. No dependencies outside the standard library.
Quick inspection of Python code files, and helpful utilities for building babashka pods quickly which automatically inspects and exposes functions in Python modules to babashka/clojure via namespaces, and automatically dispatches to the appropriate python functions without having to write handlers for each function.

WIP - First cut, working version. Improvements 

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

A use of this functionality can be seen in [pylaagu/babumoshai.py](pylaagu/babumoshai.py) to generate output in the [babashka](https://babashka.org/) pod communication format.

## Babashka/Clojure Pods

You can use the `pylaagu.babumoshai` module to generate output in the [babashka](https://babashka.org/) pod communication format, plus basic code to extract instructions from the messages, *run* the code and return the response back to the calling babashka process. It's all handled for you - the input and output need to be simple enough to be serialized to JSON and back.

Here's a sample usage. The code imports the `mlexplore.hf` module which has some basic huggingface hub functions. There's a small quirk to be aware of - the `mlexplore.hf` module depends on the `mlexplore` module, so you need to import the `mlexplore` module first.

And in the tradition of Clojure, the function names are __kebab-cased__!


*Note*: This file is referred to as `mlexplore/pod.py` in the babashka-session code below.

```python
#!/usr/bin/env python
import sys
import json
from bcoding import bencode, bdecode
from pylaagu.babumoshai import (NSExportSpec,
                                to_pod_namespaced_format,
                                load_namespace, load_namespaces,
                                dispatch)
from pylaagu.utils import debug


def read():
    return dict(bdecode(sys.stdin.buffer))


def write(obj):
    sys.stdout.buffer.write(bencode(obj))
    sys.stdout.buffer.flush()


nsexport_specs = [
    NSExportSpec("mlexplore", "mlexplore/__init__.py"),
    NSExportSpec("mlexplore.hf", "mlexplore/hf.py", export_meta=True),
    NSExportSpec("huggingface_hub.hf_api", ns_name="hf-api"),]


def main(nsexport_specs: list[NSExportSpec] = nsexport_specs):
    namespaces = load_namespaces(nsexport_specs)
    exports = [to_pod_namespaced_format(ns)
               for ns in namespaces.values()]
    exports.append({"name": "pylaagu.babumoshai", "vars": [
        {"name": "load-namespace"}
    ]})
    debug(exports)
    while True:
        try:
            msg = read()
            op = msg.get("op")
            if op == "describe":
                write({
                    "format": "json",
                    "namespaces": exports,
                    "ops": {"shutdown": {}}
                })
            elif op == "invoke":
                var = msg.get("var")
                id = msg.get("id")
                args = json.loads(msg.get("args"))
                if var == "pylaagu.babumoshai/load-namespace":
                    ns = load_namespace(NSExportSpec(*args))
                    debug(ns)
                    exports.append(to_pod_namespaced_format(ns))
                    debug(exports)
                    write({"status": ["done"], "id": id, "format": "json", "namespaces": exports})
                else:
                    value = dispatch(namespaces, var, args)
                    write({"status": ["done"], "id": id,
                           "value": json.dumps(value)})
            elif op == "shutdown":
                debug("Shutting down pod.")
                break
        except EOFError:
            print("EOF")
            break
        except Exception as e:
            print("Error", e)
            write({"status": ["error"], "ex-message": str(e), "id": id})


if __name__ == "__main__":
    if len(sys.argv) == 1:
        main()
    else:
        module = sys.argv[1]
        print(load_namespace(NSExportSpec(module)))
        sys.exit(0)
```

Here's a simple babashka session that uses the above script. Notice that there is no code required to dispatch to the appropriate python functions as that is automatically handled.

```bash
Babashka v1.3.190 REPL.
Use :repl/quit or :repl/exit to quit the REPL.
Clojure rocks, Bash reaches.
```
```clojure
user=> (babashka.pods/load-pod ["./mlexplore/pod.py"])
#:pod{:id "mlexplore"}
user=> (require '[cheshire.core :as json])
nil
user=> (doc mlexplore.hf/model-info)
-------------------------
model-info
  Returns model metadata from huggingface.
nil
user=> (json/parse-string (mlexplore.hf/model-info "facebook/bart-large") keyword)
{:last_modified "2022-06-03T10:00:20+00:00", :tags ["transformers" "pytorch" "tf" "jax" "rust" "bart" "feature-extraction" "en" "arxiv:1910.13461" "license:apache-2.0" "endpoints_compatible" "region:us"], :_id "621ffdc136468d709f17adb9", :downloads 98176, :siblings [{:rfilename ".gitattributes", :size nil, :blob_id nil, :lfs nil} {:rfilename "README.md", :size nil, :blob_id nil, :lfs nil} {:rfilename "config.json", :size nil, :blob_id nil, :lfs nil} {:rfilename "flax_model.msgpack", :size nil, :blob_id nil, :lfs nil} {:rfilename "merges.txt", :size nil, :blob_id nil, :lfs nil} {:rfilename "pytorch_model.bin", :size nil, :blob_id nil, :lfs nil} {:rfilename "rust_model.ot", :size nil, :blob_id nil, :lfs nil} {:rfilename "tf_model.h5", :size nil, :blob_id nil, :lfs nil} {:rfilename "tokenizer.json", :size nil, :blob_id nil, :lfs nil} {:rfilename "tokenizer_config.json", :size nil, :blob_id nil, :lfs nil} {:rfilename "vocab.json", :size nil, :blob_id nil, :lfs nil}], :disabled false, :private false, :config {:architectures ["BartModel"], :model_type "bart", :tokenizer_config {}}, :transformersInfo {:auto_model "AutoModel", :custom_class nil, :pipeline_tag "feature-extraction", :processor "AutoTokenizer"}, :modelId "facebook/bart-large", :mask_token "<mask>", :gated false, :pipeline_tag "feature-extraction", :likes 159, :cardData {:tags nil, :datasets nil, :license "apache-2.0", :eval_results nil, :language "en", :model_name nil, :library_name nil, :base_model nil, :metrics nil}, :author "facebook", :lastModified "2022-06-03T10:00:20+00:00", :spaces ["enclap-team/enclap" "HaloMaster/chinesesummary" "webshop/amazon_shop" "eubinecto/idiomify" "MrVicente/RA-BART" "awacke1/HEDIS.Dash.Component.Top.Clinical.Terminology.Vocabulary" "andreslu/orion" "ka1kuk/litellm" "mikepastor11/PennwickFileAnalyzer" "theachyuttiwari/lfqa1" "Rschmaelzle/wikipedia-assistant" "adherent/Bart-gen-arg" "king007/wikipedia-assistant" "adumbrobot/facebook-bart-large" "asifmian/facebook-bart-large" "semaj83/ctmatch" "LMya/facebook-bart-large" "bagataway/facebook-bart-large" "ATForest/english" "sarat2hf/stock_information_app" "rtabrizi/RAG" "jfeng1115/marketing-analytics-bot" "vkthakur88/facebook-bart-large" "GuysTrans/MedChattRe" "GuysTrans/MedChattSumTran" "nonhuman/nnnn" "apekshik/bart-test" "Dhrumit1314/notivai-backend" "devvoi01/custom1" "rizkiduwinanto/challenge-NLP" "marcelomoreno26/Whatsapp-Chat-Summarizer-and-Analysis" "ieuniversity/Whatsapp_Analysis_Tool" "kenken999/litellm" "kenken999/litellmlope"], :id "facebook/bart-large", :safetensors nil, :library_name "transformers", :model_index nil, :card_data {:tags nil, :datasets nil, :license "apache-2.0", :eval_results nil, :language "en", :model_name nil, :library_name nil, :base_model nil, :metrics nil}, :transformers_info {:auto_model "AutoModel", :custom_class nil, :pipeline_tag "feature-extraction", :processor "AutoTokenizer"}, :sha "cb48c1365bd826bd521f650dc2e0940aee54720c", :widget_data nil, :created_at "2022-03-02T23:29:05+00:00"}
user=> (mlexplore.hf/url-of "facebook/bart-large" "config.json")
"https://huggingface.co/facebook/bart-large/resolve/main/config.json"
```

## Command-line helpers

### `pylaagu.meta`
```bash
python -m pylaagu.meta mlexplore/hf.py
JSON:
[
  {
    "name": "url_of",
    "args": [
      {
        "name": "model_name",
        "type": "str"
      },
      {
        "name": "filename",
        "type": "str"
      }
    ],
    "docstring": null,
    "returns": "str"
  },
  {
    "name": "model_info",
    "args": [
      {
        "name": "model_name",
        "type": "str"
      },
      {
        "name": "as_json"
      }
    ],
    "docstring": "Returns model metadata from huggingface.",
    "returns": "dict | str"
  },
  {
    "name": "model_files",
    "args": [
      {
        "name": "model_name",
        "type": "str"
      }
    ],
    "docstring": null,
    "returns": "list"
  }
]
[]

YAML:
- !!python/object:__main__.FunctionSignature
  name: url_of
  args:
  - name: model_name
    type: str
  - name: filename
    type: str
  docstring: null
  returns: str
- !!python/object:__main__.FunctionSignature
  name: model_info
  args:
  - name: model_name
    type: str
  - name: as_json
  docstring: Returns model metadata from huggingface.
  returns: dict | str
- !!python/object:__main__.FunctionSignature
  name: model_files
  args:
  - name: model_name
    type: str
  docstring: null
  returns: list

[]
```
### `pylaagu.babumoshai`
```bash
python -m pylaagu.babumoshai huggingface_hub.hf_api
{'name': 'huggingface-hub.hf-api',
 'vars': [{'name': 'asdict'},
          {'name': 'build-hf-headers'},
          {'name': 'dataclass'},
          {'name': 'deserialize-event'},
          {'name': 'experimental'},
          {'name': 'field'},
          {'name': 'filter-repo-objects'},
          {'name': 'fix-hf-endpoint-in-url'},
          {'name': 'future-compatible'},
          {'name': 'get-hf-file-metadata'},
          {'name': 'get-session'},
          {'name': 'hf-hub-url'},
          {'name': 'hf-raise-for-status'},
          {'name': 'multi-commit-create-pull-request'},
          {'name': 'multi-commit-generate-comment'},
          {'name': 'multi-commit-parse-pr-description'},
          {'name': 'overload'},
          {'name': 'paginate'},
          {'name': 'parse-datetime'},
          {'name': 'plan-multi-commits'},
          {'name': 'quote'},
          {'name': 'repo-type-and-id-from-hf-id'},
          {'name': 'thread-map'},
          {'name': 'validate-hf-hub-args'},
          {'name': 'wraps'}]}
```
