#!/usr/bin/env python3
"""
Quick test to validate that G6K extensions can be imported after installation.
This helps debug ModuleNotFoundError issues.
"""

import sys
import os

def test_imports():
    print("Testing G6K imports...")
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    errors = []
    
    try:
        import g6k
        print("✅ g6k package imported successfully")
        print(f"   Location: {g6k.__file__}")
        
        # List contents of g6k directory
        g6k_dir = os.path.dirname(g6k.__file__)
        print(f"   Contents of {g6k_dir}:")
        for item in sorted(os.listdir(g6k_dir)):
            if item.endswith('.so') or item.endswith('.pyx') or item.endswith('.py'):
                print(f"     {item}")
        
    except ImportError as e:
        print(f"❌ Failed to import g6k: {e}")
        errors.append(f"g6k: {e}")
        return errors
    
    # Test individual modules
    modules_to_test = [
        ('g6k.siever_params', 'SieverParams'),
        ('g6k.siever', 'Siever'),
    ]
    
    for module_name, class_name in modules_to_test:
        try:
            module = __import__(module_name, fromlist=[class_name])
            cls = getattr(module, class_name)
            print(f"✅ {module_name}.{class_name} imported successfully")
        except ImportError as e:
            print(f"❌ Failed to import {module_name}: {e}")
            errors.append(f"{module_name}: {e}")
        except AttributeError as e:
            print(f"⚠️  {module_name} imported but {class_name} not found: {e}")
            errors.append(f"{module_name}.{class_name}: {e}")
    
    # Test high-level imports from __init__.py
    try:
        from g6k import SieverParams
        print("✅ SieverParams imported from g6k")
    except ImportError as e:
        print(f"❌ Failed to import SieverParams from g6k: {e}")
        errors.append(f"g6k.SieverParams: {e}")
    
    try:
        from g6k import Siever
        print("✅ Siever imported from g6k")
    except ImportError as e:
        print(f"❌ Failed to import Siever from g6k: {e}")
        errors.append(f"g6k.Siever: {e}")
    
    return errors

if __name__ == "__main__":
    errors = test_imports()
    
    if errors:
        print(f"\n❌ {len(errors)} import errors found:")
        for error in errors:
            print(f"  - {error}")
        sys.exit(1)
    else:
        print("\n✅ All imports successful!")
        sys.exit(0)