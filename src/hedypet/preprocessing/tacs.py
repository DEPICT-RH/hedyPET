
from nifti_dynamic.utils import extract_multiple_tacs, save_tac
import nibabel as nib
import numpy as np
from hedypet.preprocessing.bids import create_derivatives_sidecar
from hedypet.preprocessing.utils import binary_erode


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
