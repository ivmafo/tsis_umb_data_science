from dataclasses import dataclass
from typing import Optional

@dataclass
class FileInfo:
    filename: str
    size_bytes: int
    validation_status: bool
    error_message: Optional[str] = None
    db_status: Optional[str] = None
