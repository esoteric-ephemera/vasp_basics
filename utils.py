
from jobflow import JobStore
from pathlib import Path

def get_job_store(base_path : Path = Path(".")) -> JobStore:
    bp = Path(base_path).expanduser().resolve()
    return JobStore.from_dict_spec(
        {
            "docs_store": {
                "type": "JSONStore",
                "paths": str(bp / "output.json"),
                "read_only": False,
                "key": "uuid",
            },                
            "additional_stores": {
                "data": {
                    "type": "JSONStore",
                    "paths": str(bp / "output_blobs.json"),
                    "read_only": False,
                    "key": "uuid",
                }
            }  
        }
    )
