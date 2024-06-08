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

A use of this functionality can be seen in [pylaagu/babumoshai.py](pylaagu/babumoshai.py) to generate output in the [babashka](https://babashka.org/) pod communication format.

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
```
```clojure
user=> (babashka.pods/load-pod ["./mlexplore/pod.py"])
#:pod{:id "mlexplore"}
user=> (require '[cheshire.core :as json])
nil
user=> (json/parse-string (mlexplore.hf/model_info "facebook/bart-large") keyword)
{:last_modified "2022-06-03T10:00:20+00:00", :tags ["transformers" "pytorch" "tf" "jax" "rust" "bart" "feature-extraction" "en" "arxiv:1910.13461" "license:apache-2.0" "endpoints_compatible" "region:us"], :_id "621ffdc136468d709f17adb9", :downloads 99383, :siblings [{:rfilename ".gitattributes", :size nil, :blob_id nil, :lfs nil} {:rfilename "README.md", :size nil, :blob_id nil, :lfs nil} {:rfilename "config.json", :size nil, :blob_id nil, :lfs nil} {:rfilename "flax_model.msgpack", :size nil, :blob_id nil, :lfs nil} {:rfilename "merges.txt", :size nil, :blob_id nil, :lfs nil} {:rfilename "pytorch_model.bin", :size nil, :blob_id nil, :lfs nil} {:rfilename "rust_model.ot", :size nil, :blob_id nil, :lfs nil} {:rfilename "tf_model.h5", :size nil, :blob_id nil, :lfs nil} {:rfilename "tokenizer.json", :size nil, :blob_id nil, :lfs nil} {:rfilename "tokenizer_config.json", :size nil, :blob_id nil, :lfs nil} {:rfilename "vocab.json", :size nil, :blob_id nil, :lfs nil}], :disabled false, :private false, :config {:architectures ["BartModel"], :model_type "bart", :tokenizer_config {}}, :transformersInfo {:auto_model "AutoModel", :custom_class nil, :pipeline_tag "feature-extraction", :processor "AutoTokenizer"}, :modelId "facebook/bart-large", :mask_token "<mask>", :gated false, :pipeline_tag "feature-extraction", :likes 159, :cardData {:tags nil, :datasets nil, :license "apache-2.0", :eval_results nil, :language "en", :model_name nil, :library_name nil, :base_model nil, :metrics nil}, :author "facebook", :lastModified "2022-06-03T10:00:20+00:00", :spaces ["enclap-team/enclap" "HaloMaster/chinesesummary" "webshop/amazon_shop" "eubinecto/idiomify" "MrVicente/RA-BART" "awacke1/HEDIS.Dash.Component.Top.Clinical.Terminology.Vocabulary" "andreslu/orion" "ka1kuk/litellm" "mikepastor11/PennwickFileAnalyzer" "theachyuttiwari/lfqa1" "Rschmaelzle/wikipedia-assistant" "adherent/Bart-gen-arg" "king007/wikipedia-assistant" "adumbrobot/facebook-bart-large" "asifmian/facebook-bart-large" "semaj83/ctmatch" "LMya/facebook-bart-large" "bagataway/facebook-bart-large" "ATForest/english" "sarat2hf/stock_information_app" "rtabrizi/RAG" "jfeng1115/marketing-analytics-bot" "vkthakur88/facebook-bart-large" "GuysTrans/MedChattRe" "GuysTrans/MedChattSumTran" "nonhuman/nnnn" "apekshik/bart-test" "Dhrumit1314/notivai-backend" "devvoi01/custom1" "rizkiduwinanto/challenge-NLP" "marcelomoreno26/Whatsapp-Chat-Summarizer-and-Analysis" "ieuniversity/Whatsapp_Analysis_Tool" "kenken999/litellm" "kenken999/litellmlope"], :id "facebook/bart-large", :safetensors nil, :library_name "transformers", :model_index nil, :card_data {:tags nil, :datasets nil, :license "apache-2.0", :eval_results nil, :language "en", :model_name nil, :library_name nil, :base_model nil, :metrics nil}, :transformers_info {:auto_model "AutoModel", :custom_class nil, :pipeline_tag "feature-extraction", :processor "AutoTokenizer"}, :sha "cb48c1365bd826bd521f650dc2e0940aee54720c", :widget_data nil, :created_at "2022-03-02T23:29:05+00:00"}
user=> (mlexplore.hf/url_of "facebook/bart-large" "config.json")
"https://huggingface.co/facebook/bart-large/resolve/main/config.json"
user=>
```

## Caching
See [pylaagu/cache.py](pylaagu/cache.py). Two annotations exist
- `@cache` to persistently cache (using sqlite3) the return value of a function. This requires calling the `init_app` function with an appname.
- `@memoize` to, well, memoize in memory the return value of a function.
