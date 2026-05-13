
from __future__ import annotations

import os
from pathlib import Path

from jobflow import JobStore

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

def chdir(new_dir : Path):
    cwd = Path.cwd()
    os.chdir(new_dir)
    yield
    os.chdir(cwd)