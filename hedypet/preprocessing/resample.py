
import nibabel as nib
import numpy as np
from pathlib import Path
from typing import Optional
from nibabel.processing import resample_from_to
from hedypet.utils import *

def resample_series(
    input_path: Path,
    reference: Path,
    output_path: Path,
    isotropic_mm: Optional[float] = None,
    order: int = 3,
    mode: str = 'constant',
    cval: str = 0,
    pre_affine: Optional[Path] = None,
    is_2d_acquisition = False,
) -> None:
    
    """Resample a single image series to reference space."""
    img = nib.load(str(input_path))
    if isinstance(reference,tuple):
        target_shape, target_affine = reference
    else:
        ref = nib.load(str(reference))
        target_affine = ref.affine
        target_shape = ref.shape

    target_shape = list(target_shape)
    
    # Handle registration 3D->4D (dynamic PET)
    if len(target_shape) == 4:
        target_shape = target_shape[:3]

    # Handle registration from 2D->3D acquisition (XRay)
    if is_2d_acquisition:
        if pre_affine is not None:
            raise Exception("Cannot resample 2D acquisition with affine matrix") 
        
        target_shape[1] = 1
    
    if pre_affine is not None:
        pre_aff = np.loadtxt(pre_affine)
        img = nib.Nifti1Image(img.get_fdata(), pre_aff @ img.affine, img.header)
    
    # Option to change voxelsize while keeping the same world-space FOV 
    if isotropic_mm is not None:
        scaling = isotropic_mm / np.abs(np.diag(target_affine)[:3])
        target_affine = target_affine @ np.diag(list(scaling)+[1])
        target_shape = tuple(int(s / scale) for s, scale in zip(target_shape, scaling))

    resampled = resample_from_to(
        img,
        (target_shape, target_affine),
        order=order,
        mode=mode,
        cval=cval
    )
    output_path.parent.mkdir(parents=True, exist_ok=True)
    nib.save(resampled, str(output_path))

