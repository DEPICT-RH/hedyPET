
from nifti_dynamic.utils import extract_multiple_tacs, save_tac
import nibabel as nib
import numpy as np
from hedypet.utils import load_splits, RAW_ROOT, DERIVATIVES_ROOT
from multiprocessing import Pool
from functools import partial
from hedypet.preprocessing.bids import create_derivatives_sidecar
from hedypet.utils import binary_erode
from parse import parse

def extract_and_save_tac(dpet_path,seg_path,tac_save_folder,erosion):
    if isinstance(seg_path, np.ndarray):
        seg = seg_path
        sources = [dpet_path]
    else:
        seg = nib.load(seg_path).get_fdata()
        seg = binary_erode(seg,erosion)
        sources = [dpet_path,seg_path]

    create_derivatives_sidecar(tac_save_folder.parent,reference=None,sources=sources)
    tacs_mean, tacs_std, tacs_n = extract_multiple_tacs(dpet_path, seg,return_std_n=True)
    for k in tacs_mean:
        save_tac(
            tac_save_folder/f"tac_{k}",
                tacs_mean[k],
                tacs_std[k],
                tacs_n[k],
            )


def extract_all_organ_tacs(sub, raw_root, derivatives_root, rec="acstatPSF", erosions=[0,1]):
    """Organ mean extraction for static PET reconstructions (pipelinye-bodystat)"""

    assert rec in  ["acstatPSF","acdynPSF"]

    if "acstat" in rec:
        derivatives = derivatives_root / f"pipeline-bodystat/{sub}"
        pet_path = next((raw_root / sub).glob(f"pet/*rec-{rec}_pet.nii.gz"))
    else:
        derivatives = derivatives_root / f"pipeline-bodydyn/{sub}"
        pet_path = next((raw_root / sub).glob("pet/*acdyn*_pet.nii.gz"))

    pipeline_root = derivatives_root / f"tacs"

    #Aorta derivatives are ignored for non-dynamic acquisitions
    derivatives_root_aorta = derivatives_root / f"aorta/{sub}"

    for erosion in erosions:
        
        # Totalseg total
        totalseg_path = next(derivatives.glob("anat/*rec-br38f_seg-total*_dseg.nii.gz"))
        totalseg_organs_tacs_path = (pipeline_root / sub) / f"{rec}/ts_total/erosion-{erosion}"
        if not totalseg_organs_tacs_path.exists():
            extract_and_save_tac(pet_path, totalseg_path,totalseg_organs_tacs_path,erosion)

        #Synthseg
        synthseg_path = next(derivatives.glob("anat/*synthseg_*dseg.nii.gz"))
        synthseg_tacs_path = (pipeline_root / sub) / f"{rec}/synthseg/erosion-{erosion}"
        if not synthseg_tacs_path.exists():
            extract_and_save_tac(pet_path, synthseg_path,synthseg_tacs_path,erosion)

        #Synthseg parc
        synthsegparc_path = next(derivatives.glob("anat/*synthsegparc_*dseg.nii.gz"))
        synthsegparc_tacs_path = (pipeline_root / sub) / f"{rec}/synthsegparc/erosion-{erosion}"
        if not synthsegparc_tacs_path.exists():
            extract_and_save_tac(pet_path, synthsegparc_path,synthsegparc_tacs_path,erosion)

        # Totalseg tissue
        tissue_path = next(derivatives.glob("anat/*rec-br38f_seg-tissue*_dseg.nii.gz"))
        tissue_tacs_path = (pipeline_root / sub) / f"{rec}/ts_tissue/erosion-{erosion}"
        if not tissue_tacs_path.exists():
            extract_and_save_tac(pet_path,tissue_path,tissue_tacs_path,erosion)

        # Totalseg body
        body_path = next(derivatives.glob("anat/*rec-br38f_seg-body*_dseg.nii.gz"))
        body_tacs_path = (pipeline_root / sub) / f"{rec}/ts_body/erosion-{erosion}"
        if not body_tacs_path.exists():
            extract_and_save_tac(pet_path,body_path,body_tacs_path,erosion)

        # Aorta segments (only for dynamic acquisition)
        aortasegments_path = next((derivatives_root_aorta).glob("*aortasegments*.nii.gz"))
        aortasegments_tacs_path = (pipeline_root / sub) / f"{rec}/aortasegments/erosion-{erosion}"
        if not aortasegments_tacs_path.exists() and rec == "acdynPSF":
            extract_and_save_tac(pet_path,aortasegments_path,aortasegments_tacs_path,erosion)

    # Aorta VOIS (only for dynamic acquisition)
    for aortvois_path in (derivatives_root_aorta).glob("*aortavois*.nii.gz"):
        voi_name = parse("{}seg-{voi_name}_dseg.nii.gz", aortvois_path.name).named["voi_name"]
        aortavois_tacs_path = (pipeline_root / sub) / f"{rec}/{voi_name}/erosion-{0}"
        if not aortavois_tacs_path.exists() and rec == "acdynPSF":
            extract_and_save_tac(pet_path,aortvois_path,aortavois_tacs_path,erosion=0)

    # Whole body
    whole_image_tacs_path = (pipeline_root / sub) / f"{rec}/totalimage/erosion-0"
    if not whole_image_tacs_path.exists():
        seg = nib.load(totalseg_path).get_fdata()
        seg = np.ones_like(seg,dtype="bool")
        extract_and_save_tac(pet_path,seg,whole_image_tacs_path,erosion=0)

if __name__ == "__main__":
    subs = load_splits()["all"]
    subs.remove("sub-017")
    for rec in ["acdynPSF","acstatPSF"]:
        for sub in subs:
            extract_all_organ_tacs(sub,raw_root=RAW_ROOT,derivatives_root=DERIVATIVES_ROOT,rec=rec)
        