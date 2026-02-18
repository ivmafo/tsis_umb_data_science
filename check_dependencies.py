import ast
import os
import sys
import importlib.metadata

def get_imports(path):
    with open(path, 'r', encoding='utf-8') as f:
        try:
            tree = ast.parse(f.read())
        except Exception as e:
            print(f"Error parsing {path}: {e}")
            return set()

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split('.')[0])
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                imports.add(node.module.split('.')[0])
    return imports

def main():
    root_dir = 'src'
    all_imports = set()
    
    print(f"Scanning {root_dir}...")
    for root, dirs, files in os.walk(root_dir):
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                all_imports.update(get_imports(path))

    # libraries = stdlib_list.stdlib_list("3.10") 
    # Use a simple heuristic for now or sys.stdlib_module_names if available (Python 3.10+)
    try:
        std_libs = sys.stdlib_module_names
    except AttributeError:
        # Fallback for older python if needed, but user has 3.12
        std_libs = set(sys.builtin_module_names) 

    third_party = []
    for imp in all_imports:
        if imp not in std_libs and imp not in ['src', 'run', 'main']: # Exclude local project packages
             # Filter out some common local modules if they match project structure
             if not os.path.exists(os.path.join('src', imp)) and not os.path.exists(imp + '.py'):
                third_party.append(imp)

    print("\nPotential Third-Party Imports found:")
    third_party = sorted(list(set(third_party)))
    
    missing_site_packages = []
    installed_packages = {dist.metadata['Name'].lower().replace('-', '_') for dist in importlib.metadata.distributions()}
    # Add mapping for packages where import name != install name
    # e.g. PIL -> Pillow, yaml -> PyYAML
    
    # We can just check if we can import them
    
    not_installed = []
    
    for lib in third_party:
        print(f"Checking {lib}...", end=" ")
        try:
            importlib.import_module(lib)
            print("OK (Imported)")
        except ImportError:
            print("MISSING!")
            not_installed.append(lib)

    print("\n--- Summary ---")
    print("Found Standard/Local/Other imports:", all_imports)
    print("\nIdentified Third-Party Candidates:", third_party)
    print("\nMissing/Uninstalled Candidates:", not_installed)

if __name__ == '__main__':
    main()
