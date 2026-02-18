
from src.main import app

print("Inspecting registered routes:")
for route in app.routes:
    if hasattr(route, "path"):
        print(f"{route.methods} {route.path}")
    else:
        print(route)
