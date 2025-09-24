## VIGTIGT: installer pip install indexed_gzip = langt hurtigere! 
from nifti_dynamic.aorta_rois import extract_aorta_vois, extract_aorta_segments, average_early_pet_frames
import nibabel as nib
import numpy as np
from hedypet.utils import load_splits, load_sidecar, RAW_ROOT, DERIVATIVES_ROOT
from pathlib import Path
import os 
from nifti_dynamic.visualizations import plot_aorta_visualizations
from hedypet.utils import draw_cylinder
from tqdm import tqdm 
from hedypet.preprocessing.bids import create_derivatives_sidecar

def fix_aorta_sub_77(aorta):
    p1 = (440-223,199,345)
    p2 = (440-226,201,372)
    cyl = draw_cylinder(p1,p2,5, aorta.shape)
    return aorta | cyl


def main(sub, ml,px,derivative_root,raw_root):
    dyn_derivatives = derivative_root / f"pipeline-bodydyn/{sub}"
    seg_derivatives = derivative_root / f"aorta/{sub}"
    dpet_path = next((raw_root / sub).glob("pet/*acdyn*_pet.nii.gz"))
    totalseg_path = next(dyn_derivatives.glob("anat/*total*_dseg.nii.gz"))
    aorta_segments_path = seg_derivatives / f"{sub}_seg-aortasegments_dseg.nii.gz"
    aorta_vois_path = seg_derivatives / f"{sub}_seg-aortavois_ml-{ml}_width-{px}_dseg.nii.gz"
    output_visualization_path =  Path(str(aorta_vois_path).replace(".nii.gz",".jpg"))
    
    sidecar = load_sidecar(dpet_path)
    frame_time_start = np.array(sidecar['FrameTimesStart'])

    if aorta_segments_path.exists() and aorta_vois_path.exists():
        return

    os.makedirs(aorta_segments_path.parent,exist_ok=True)
    pet = average_early_pet_frames(dpet_path,frame_time_start,t_threshold=40)

    if not aorta_segments_path.exists():        
        ## Prepare aorta mask from totalseg
        totalseg = nib.load(totalseg_path)
        aorta_mask = totalseg.get_fdata()==52
        if sub == "sub-077":
            aorta_mask = fix_aorta_sub_77(aorta_mask)
        aorta_mask = nib.Nifti1Image(aorta_mask.astype(np.int16),affine=totalseg.affine)

        #Extract mask
        aorta_segments = extract_aorta_segments(aorta_mask,pet)
        nib.save(aorta_segments,aorta_segments_path)
        create_derivatives_sidecar(
            aorta_segments_path, 
            reference=dpet_path,
            sources=[dpet_path,totalseg_path],
            Description="Aorta segments version 1.0"
        )


    if not aorta_vois_path.exists():
        aorta_segments = nib.load(aorta_segments_path)
        aorta_vois = extract_aorta_vois(aorta_segments, pet, volume_ml=ml,cylinder_width=px)
        nib.save(aorta_vois,aorta_vois_path)
        create_derivatives_sidecar(
            aorta_vois_path, 
            reference=dpet_path,
            sources=[dpet_path,totalseg_path],
            Description=f"Aorta vois version 1.0, volume: {ml}ml, cylinder width: {px}pixels."
        )
        plot_aorta_visualizations(
            pet,
            aorta_segments,
            aorta_vois,
            output_visualization_path)


if __name__ == "__main__":
    subs = load_splits()["all"]
    subs.remove("sub-017")
    param_sets = [
        {
            "ml":1,
            "px":3,
        },
        {
            "ml":1.5,
            "px":5,
        },
        {
            "ml":2,
            "px":5,
        }
    ]
    for param in param_sets:
        for sub in tqdm(subs):
            print(DERIVATIVES_ROOT,RAW_ROOT)
            main(sub,**param,derivative_root=DERIVATIVES_ROOT, raw_root=RAW_ROOT)

# %%
