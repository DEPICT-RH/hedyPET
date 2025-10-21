import nibabel as nib
import numpy as np
from hedypet.utils import load_splits, RAW_ROOT, DERIVATIVES_ROOT
from hedypet.preprocessing.tacs import extract_and_save_tac
from parse import parse

def main(sub, raw_root, derivatives_root, erosions=[0,1]):
    """Organ mean extraction for PET reconstrunctions"""

    rec = "ct"
    derivatives = derivatives_root / f"totalsegmentator/{sub}"
    pet_path = next((raw_root / sub).glob(f"anat/*br38f*_ct.nii.gz"))

    pipeline_root = Path("/depict/users/hinge/private/ct_organ_means_hedit3") / f"tacs"

    #Aorta derivatives are ignored for non-dynamic acquisitions
    for erosion in erosions:
        
        # Totalseg total
        totalseg_path = next(derivatives.glob("anat/*rec-br38f_seg-total*_dseg.nii.gz"))
        totalseg_organs_tacs_path = (pipeline_root / sub) / f"{rec}/ts_total/erosion-{erosion}"
        if not totalseg_organs_tacs_path.exists():
            extract_and_save_tac(pet_path, totalseg_path,totalseg_organs_tacs_path,erosion)

        # #Synthseg
        # synthseg_path = next(derivatives.glob("anat/*synthseg_*dseg.nii.gz"))
        # synthseg_tacs_path = (pipeline_root / sub) / f"{rec}/synthseg/erosion-{erosion}"
        # if not synthseg_tacs_path.exists():
        #     extract_and_save_tac(pet_path, synthseg_path,synthseg_tacs_path,erosion)

        # #Synthseg parc
        # synthsegparc_path = next(derivatives.glob("anat/*synthsegparc_*dseg.nii.gz"))
        # synthsegparc_tacs_path = (pipeline_root / sub) / f"{rec}/synthsegparc/erosion-{erosion}"
        # if not synthsegparc_tacs_path.exists():
        #     extract_and_save_tac(pet_path, synthsegparc_path,synthsegparc_tacs_path,erosion)

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


    # Whole body
    # whole_image_tacs_path = (pipeline_root / sub) / f"{rec}/totalimage/erosion-0"
    # if not whole_image_tacs_path.exists():
    #     seg = nib.load(totalseg_path).get_fdata()
    #     seg = np.ones_like(seg,dtype="bool")
    #     extract_and_save_tac(pet_path,seg,whole_image_tacs_path,erosion=0)

# if __name__ == "__main__":
#     from tqdm import tqdm
#     from pathlib import Path
#     subs = load_splits()["all"]
#     for sub in tqdm(subs):
#         main(sub,raw_root=RAW_ROOT,derivatives_root=DERIVATIVES_ROOT)



from tqdm import tqdm
from multiprocessing import Pool
from pathlib import Path

# Load your list of subjects
subs = load_splits()["all"]

# Define a wrapper so tqdm can track progress
def process_sub(sub):
    return main(sub, raw_root=RAW_ROOT, derivatives_root=DERIVATIVES_ROOT)

if __name__ == "__main__":
    # Use multiprocessing with 12 workers
    with Pool(processes=12) as pool:
        list(tqdm(pool.imap_unordered(process_sub, subs), total=len(subs)))