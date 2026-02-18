from typing import List, BinaryIO, Union
from src.domain.entities.file_info import FileInfo
from src.domain.ports.file_repository import FileRepository

class ManageFiles:
    def __init__(self, repository: FileRepository):
        self.repository = repository

    def list_files(self) -> List[FileInfo]:
        files = self.repository.list_files()
        
        # Enrich with DB status
        import duckdb
        try:
            conn = duckdb.connect("data/metrics.duckdb", read_only=True)
            # Check if table exists
            try:
                # Get all statuses in one go
                rows = conn.execute("SELECT file_name, status FROM file_processing_control").fetchall()
                status_map = {r[0]: r[1] for r in rows}
                
                for f in files:
                    # Default is None, but if in map use that
                    f.db_status = status_map.get(f.filename)
            except:
                # Table might not exist yet
                pass
            finally:
                conn.close()
        except Exception as e:
            print(f"Error checking DB status: {e}")
            
        return files

    def upload_file(self, filename: str, content: Union[BinaryIO, bytes]) -> FileInfo:
        return self.repository.save_file(filename, content)
