import os
import sys
import uvicorn
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from src.infrastructure.config.settings import Settings

# Adjust path for frozen app
if getattr(sys, 'frozen', False):
    # Running as compiled exe
    base_path = sys._MEIPASS
else:
    # Running as script
    base_path = os.path.dirname(os.path.abspath(__file__))

# Import app after path setup might be needed, but here we just import it
from src.main import app

# Mount static files
static_dir = os.path.join(base_path, "web", "dist")
if not os.path.exists(static_dir):
    print(f"Warning: Static directory not found at {static_dir}")
    # Fallback for dev mode if run.py is run directly without build
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web", "dist")

app.mount("/assets", StaticFiles(directory=os.path.join(static_dir, "assets")), name="assets")

@app.get("/")
async def serve_spa():
    return FileResponse(os.path.join(static_dir, "index.html"))

# Catch-all for SPA routes
@app.exception_handler(404)
async def custom_404_handler(_, __):
    return FileResponse(os.path.join(static_dir, "index.html"))

if __name__ == "__main__":
    # Ensure data directory exists next to executable
    if getattr(sys, 'frozen', False):
        exe_dir = os.path.dirname(sys.executable)
        os.chdir(exe_dir)
    
    settings = Settings()
    import webbrowser
    webbrowser.open("http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=settings.api_port, log_level="info")
