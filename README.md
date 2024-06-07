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

A use of this functionality can be seen in (pylaagu/babumoshai.py)[pylaagu/babumoshai.py] to generate output in the (https://babashka.org)[babashka] pod communication format.
```bash

### Babashka
TBD.

## Caching
See (pylaagu/cache.py)[pylaagu/cache.py]. Two annotations exist
- `@cache` to persistently cache (using sqlite3) the return value of a function. This requires calling the `init_app` function with an appname.
- `@memoize` to, well, memoize in memory the return value of a function.
