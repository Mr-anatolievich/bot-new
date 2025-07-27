# generate_structure.py
import os

EXCLUDE_DIRS = {'venv', '__pycache__', '.git', 'node_modules'}

def generate_structure(path='.', prefix=''):
    entries = sorted(os.listdir(path))
    for i, entry in enumerate(entries):
        full_path = os.path.join(path, entry)
        if entry in EXCLUDE_DIRS or entry.startswith('.'):
            continue
        connector = '└── ' if i == len(entries) - 1 else '├── '
        print(prefix + connector + entry)
        if os.path.isdir(full_path):
            new_prefix = prefix + ('    ' if i == len(entries) - 1 else '│   ')
            generate_structure(full_path, new_prefix)

with open("PROJECT-STRUCTURE.md", "w") as f:
    from contextlib import redirect_stdout
    with redirect_stdout(f):
        print("# Project Structure\n")
        generate_structure()
