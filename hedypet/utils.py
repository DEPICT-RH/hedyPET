from pathlib import Path
from dotenv import load_dotenv
import os 
import json
import re 
import nibabel as nib
import numpy as np

load_dotenv()

RAW_ROOT = Path(os.environ["RAW_ROOT"])
DERIVATIVES_ROOT = Path(os.environ["DERIVATIVES_ROOT"])

def load_splits():
    with open(RAW_ROOT / "code/data_splits.json","r") as handle:
        return json.load(handle)
    
def load_sidecar(image_path):
    with open(str(image_path).replace(".nii.gz",".json"),"r") as handle:
        return json.load(handle)
    
def save_numpy_array(
    array: np.ndarray,
    output_path: Path,
) -> None:
    """Save array to file."""
    output_path.parent.mkdir(exist_ok=True, parents=True)
    np.savetxt(output_path, array)


def get_head_center(totalseg_img_path):
    """Returns world-coordinates of brain center"""
    seg = nib.load(totalseg_img_path)
    ixs = np.where(seg.get_fdata() == 90)
    center_vox = np.array([(np.min(x)+np.max(x))/2 for x in ixs]+[1])
    center_world = seg.affine@center_vox
    return center_world[:3]


def get_voxmap_around_centerpoint(center_point,isotropic_mm,size_mm):
    """Creates (shape, affine) isotropic voxmap of world-space-size `size_mm` around `center_point`"""
    shape = tuple(round(x/isotropic_mm) for x in size_mm)
    affine = np.diag([-isotropic_mm,isotropic_mm,isotropic_mm,1])
    offset = np.array(size_mm)/2
    offset[0] = -offset[0]
    affine[:3,-1] = center_point-offset
    return shape, affine
