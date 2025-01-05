import ast

source_code = """
def example(a, b=42, c='hello', d=lambda x: x):
    pass
"""

# Parse the source code
tree = ast.parse(source_code)

# Find the function definition node
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name == 'example':
        func_def = node
        break

# Extract the argument names and defaults
arg_names = [arg.arg for arg in func_def.args.args]
defaults = func_def.args.defaults

# Map arguments with their default values
arg_defaults = {arg_names[-len(defaults) + i]: ast.literal_eval(default) 
                for i, default in enumerate(defaults)}

print(arg_defaults)
