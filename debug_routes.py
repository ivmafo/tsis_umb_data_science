import sys
import os

# Add current directory to path so we can import src
sys.path.append(os.getcwd())

try:
    from src.main import app
    print("Successfully imported app from src.main")
    
    print("\nRegistered Routes:")
    found = False
    for route in app.routes:
        if hasattr(route, "path"):
            print(f"- {route.path} [{','.join(route.methods)}]")
            if "/reports/origin/pdf" in route.path:
                found = True
    
    if found:
        print("\nSUCCESS: /reports/origin/pdf is registered.")
    else:
        print("\nFAILURE: /reports/origin/pdf is NOT registered.")

except Exception as e:
    print(f"\nCRITICAL ERROR importing app: {e}")
    import traceback
    traceback.print_exc()
