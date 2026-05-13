
from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import TYPE_CHECKING
import warnings

from atomate2.common.jobs.utils import remove_workflow_files
from atomate2.forcefields.jobs import ForceFieldRelaxMaker
from atomate2.vasp.jobs.mp import MP24RelaxMaker, MP24StaticMaker
from atomate2.vasp.jobs.core import HSEBSMaker
from atomate2.vasp.powerups import update_user_incar_settings
from atomate2.vasp.sets.core import HSEBSSetGenerator

from jobflow import Flow, run_locally
from jobflow.managers.fireworks import flow_to_workflow
from pymatgen.core import Structure
from pymatgen.io.vasp.sets import MP24StaticSet

from utils import get_job_store, chdir_ctx

if TYPE_CHECKING:
    from collections.abc import Sequence
    from typing import Any, Literal

    from fireworks import Workflow
    from jobflow import Response

BANDSTRUCTURE_CONFIG = deepcopy(MP24StaticSet()._config_dict)
BANDSTRUCTURE_CONFIG["INCAR"].pop("KSPACING")

kpoints_override = {
    "kpath_kwargs": {"path_type": "latimer_munro"},
    "reciprocal_density": HSEBSSetGenerator.reciprocal_density,
    "zero_weighted_line_density": HSEBSSetGenerator.line_density,
}

DEFAULT_FILES_TO_REMOVE = ["WAVECAR"]

WORKING_DIR = Path("./2-mp-workflow").resolve()

def mp_workflow(
    structure : Structure,
    pre_relax : bool = False,
    get_bandstructure : bool = False,
    clean_files : Sequence[str] | None = None,
) -> Flow:

    jobs = []
    if pre_relax:
        pre_relax_job = ForceFieldRelaxMaker(
            name = "MatPES-r2SCAN MLIP relax",
            force_field_name = "MATPES_R2SCAN",
            fix_symmetry = True,
        ).make(structure)
        jobs += [pre_relax_job]
        structure = pre_relax_job.output.structure

    relax_job = MP24RelaxMaker().make(structure,prev_dir=None)
    static_job  = MP24StaticMaker(
        copy_vasp_kwargs={"additional_vasp_files": ("WAVECAR", "CHGCAR")},
    ).make(relax_job.output.structure, prev_dir=relax_job.output.dir_name)

    jobs += [relax_job,static_job]

    if get_bandstructure:
        bandstructure_job = HSEBSMaker(
            name = "r2SCAN band structure",
            input_set_generator = HSEBSSetGenerator(
                config_dict=BS_CONFIG,
                user_incar_settings={
                    "GGA": None,
                    "METAGGA": "R2SCAN",
                    "HFSCREEN": None,
                    "LAECHG": False,
                    "LVTOT": False,
                    "PRECFOCK": None,
                    "LHFCALC": None,
                },
                user_kpoints_settings = kpoints_override,
                mode="line",
            ),
        ).make(
            static_job.output.structure,
            prev_dir = static_job.output.dir_name,
            mode = "line"
        )
        jobs.append(bandstructure_job)

    files_to_rm = clean_files if clean_files is not None else DEFAULT_FILES_TO_REMOVE
    if len(files_to_rm) > 0:
        cleanup = remove_workflow_files(
            directories=[job.output.dir_name for job in jobs],
            file_names=files_to_rm,
            allow_zpath=True,
        )
        jobs += [cleanup]

    return Flow(jobs)
   
def get_resource_updates(
    hpc : Literal["perlmutter","kestrel","lawrencium-lr6","lawrencium-lr7"],
    node_type : Literal["cpu","gpu"],
    num_nodes : int | None = None
) -> dict[str,Any]:
    """Assign reasonable starting guesses for HPC resources commonly available to those in the Materials Project.

    Also these can be refined to account for memory usage as needed.
    Larger structures may require lowering KPAR significantly.

    Are you reading this from somewhere outside the US or just don't have DOE funding?
    Adapt this how you see fit to your specific HPC setup.
    """

    if node_type not in {"cpu","gpu"}:
        raise ValueError(f"Unknown node type {node_type}")

    nnodes = num_nodes or 1

    flow_updates = {"LELF": False}
    if hpc == "perlmutter":
        if node_type == "cpu":
            flow_updates |= {"NCORE": 16, "KPAR": 2*nnodes }
        elif node_type == "gpu":
            flow_updates |= {"NCORE": 1, "KPAR": 4*nnodes, "NSIM": 16, }
    elif hpc == "kestrel":
        if node_type == "cpu":
            flow_updates |= {"NCORE": 8, "KPAR": nnodes}
        elif node_type == "gpu":
            flow_updates |= {"NCORE": 1, "KPAR": 4*nnodes, "NSIM": 16, }
    elif hpc in {"lawrencium-lr6","lawrencium-lr7"}:
        if node_type == "cpu":
            flow_updates |= {"NCORE": 8, "KPAR": nnodes}
        elif node_type == "gpu":
            warnings.warn(
                "Too much variance in lawrencium GPU node types - specify manually."
            )
    else:
        raise ValueError(f"Unknown {resource=}")
    return flow_updates

def _set_up_flow_with_incar_updates(
    structure : Structure,
    pre_relax : bool = False,
    get_bandstructure : bool = False,
    clean_files : Sequence[str] | None = None,
    user_incar_updates : dict[str,Any] | None = None,
    resource_hpc : Literal["perlmutter","kestrel","lawrencium-lr6","lawrencium-lr7"] | None = None,
    resource_node_type : Literal["cpu","gpu"] | None = None,
    resource_num_nodes : int | None = None,
    metadata : dict[str,Any] | None = None,
) -> Flow:

    flow = mp_workflow(
        structure,
        pre_relax=pre_relax,
        get_bandstructure=get_bandstructure,
        clean_files=clean_files,
    )

    incar_updates = {
        **(user_incar_updates or {}),
    }
    if all(val is not None for val in (resource_hpc,resource_node_type,)):
        incar_updates |= get_resource_updates(resource_hpc,resource_node_type,num_nodes=resource_num_nodes)

    if incar_updates:
        flow = update_user_incar_settings(flow,incar_updates=incar_updates)

    if (user_metadata := metadata or {}):
        flow.update_metadata(user_metadata)

    return flow


def get_fireworks_workflow(
    structure : Structure,
    pre_relax : bool = False,
    get_bandstructure : bool = False,
    clean_files : Sequence[str] | None = None,
    user_incar_updates : dict[str,Any] | None = None,
    resource_hpc : Literal["perlmutter","kestrel","lawrencium-lr6","lawrencium-lr7"] | None = None,
    resource_node_type : Literal["cpu","gpu"] | None = None,
    resource_num_nodes : int | None = None,
    metadata : dict[str,Any] | None = None,
) -> Workflow:

    flow = _set_up_flow_with_incar_updates(
        structure,
        pre_relax=pre_relax,
        get_bandstructure=get_bandstructure,
        clean_files=clean_files,
        user_incar_updates=user_incar_updates,
        resource_hpc=resource_hpc,
        resource_node_type=resource_node_type,
        resource_num_nodes=resource_num_nodes,
        metadata = metadata,
    )
    fw_workflow = flow_to_workflow(flow)
    if user_metadata:
        fw_workflow.metadata = user_metadata.copy()
    return fw_workflow

def run_mp_workflow_locally(
    structure : Structure,
    working_dir : Path = WORKING_DIR,
    pre_relax : bool = False,
    get_bandstructure : bool = False,
    clean_files : Sequence[str] | None = None,
    user_incar_updates : dict[str,Any] | None = None,
    resource_hpc : Literal["perlmutter","kestrel","lawrencium-lr6","lawrencium-lr7"] | None = None,
    resource_node_type : Literal["cpu","gpu"] | None = None,
    resource_num_nodes : int | None = None,
    metadata : dict[str,Any] | None = None,
) -> Response:
    
    if not working_dir.exists():
        working_dir.mkdir(exist_ok=True)

    flow = _set_up_flow_with_incar_updates(
        structure,
        pre_relax=pre_relax,
        get_bandstructure=get_bandstructure,
        clean_files=clean_files,
        user_incar_updates=user_incar_updates,
        resource_hpc=resource_hpc,
        resource_node_type=resource_node_type,
        resource_num_nodes=resource_num_nodes,
        metadata = metadata,
    )

    cwd = Path.cwd()
    with chdir_ctx(working_dir):
        response = run_locally(
            mp_relax_job(structure,incar_updates=incar_updates),
            store=get_job_store(base_path=working_dir),
            create_folders=True,
        )
    return response


if __name__ == "__main__":

    POSCAR_Zn_S = """Example zincblende ZnS POSCAR
5.4
    0.0 0.5 0.5
    0.5 0.0 0.5
    0.5 0.5 0.0
Zn S
1 1
Direct
    0.0 0.0 0.0
    0.25 0.25 0.25
"""

    response = run_mp_workflow_locally(
        POSCAR_Zn_S,
        pre_relax=True,
        get_bandstructure=True,
        resource_hpc = "kestrel",
        resource_node_type = "cpu"
    )