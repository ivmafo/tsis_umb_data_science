import os
import shutil
from src.core.ports.file_system_repository import FileSystemRepository
from typing import List

class LocalFileSystemRepository(FileSystemRepository):
    def __init__(self, base_path: str):
        self.base_path = base_path
        self.processing_dir = os.path.join(base_path, 'data', 'raw')

    def copy_files_to_processing_directory(self, source_dir: str, file_types: tuple) -> List[str]:
        source_path = os.path.normpath(source_dir)
        target_path = os.path.join(self.processing_dir, os.path.basename(source_dir))
        
        if not os.path.exists(target_path):
            os.makedirs(target_path)

        copied_files = []
        for filename in os.listdir(source_path):
            if filename.endswith(file_types):
                source_file = os.path.join(source_path, filename)
                target_file = os.path.join(target_path, filename)
                shutil.copy2(source_file, target_file)
                copied_files.append(target_file)
        
        return copied_files

    def get_processing_directory(self) -> str:
        return self.processing_dir