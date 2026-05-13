"""Run a basic relaxation job to understand the inputs and outputs of VASP."""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING

from atomate2.vasp.jobs.mp import MP24RelaxMaker
from atomate2.vasp.powerups import update_user_incar_settings
from jobflow import run_locally
from pymatgen.core import Structure

from utils import get_job_store

if TYPE_CHECKING:
    from jobflow import Job, Response

WORKING_DIR = Path("./1-relax-output").resolve()

def mp_relax_job(structure : Structure, incar_updates : dict | None = None) -> Job:
    """Relax a structure using r2SCAN at the current MP input settings."""
    relax_job = MP24RelaxMaker().make(structure)
    if incar_updates:
        relax_job = update_user_incar_settings(relax_job,incar_updates=incar_updates)
    return relax_job

def run_relax(structure : Structure, working_dir : Path = WORKING_DIR, incar_updates : dict | None = None) -> Response:
    
    if not working_dir.exists():
        working_dir.mkdir(exist_ok=True)
    
    cwd = Path.cwd()
    os.chdir(working_dir)
    resp = run_locally(
        mp_relax_job(structure,incar_updates=incar_updates),
        store=get_job_store(base_path=working_dir),
        create_folders=True,
    )
    os.chdir(cwd)
    return resp

if __name__ == "__main__":

    POSCAR_Zn_S = """Example zincblende ZnS POSCAR
3.9
    0.0 0.5 0.5
    0.5 0.0 0.5
    0.5 0.5 0.0
Zn S
1 1
Direct
    0.0 0.0 0.0
    0.25 0.25 0.25
"""
    
    structure = Structure.from_str(POSCAR_Zn_S,fmt="poscar")
    job_output = run_relax(structure)