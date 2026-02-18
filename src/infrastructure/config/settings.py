"""Application Settings using Pydantic Settings."""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Uses Pydantic Settings v2 for validation and type safety.
    """
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
    
    # Application
    app_name: str = "Metrics Processing System"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # Database
    database_path: str = "data/metrics.duckdb"
    
    # Data Processing
    data_directory: str = "data"
    file_pattern: str = "data/*.csv"
    max_workers: int = 4
    
    # CORS
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:8000", "http://localhost:5173"]
    
    @property
    def data_dir_path(self) -> Path:
        """Get data directory as Path object. Handles frozen state."""
        import sys
        import os
        if getattr(sys, 'frozen', False):
            # If frozen, data is relative to the executable
            base_path = os.path.dirname(sys.executable)
            return Path(base_path) / self.data_directory
        return Path(self.data_directory)
    
    @property
    def db_path(self) -> Path:
        """Get database path as Path object. Handles frozen state."""
        import sys
        import os
        if getattr(sys, 'frozen', False):
             # If frozen, DB is relative to the executable
            base_path = os.path.dirname(sys.executable)
            return Path(base_path) / self.database_path
        return Path(self.database_path)
