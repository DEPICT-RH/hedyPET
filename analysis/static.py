## VIGTIGT: installer pip install indexed_gzip = langt hurtigere! 
#%%
from scipy.ndimage import binary_erosion
from nifti_dynamic.patlak import voxel_patlak, roi_patlak
from nifti_dynamic.utils import extract_tac, extract_multiple_tacs
from nifti_dynamic.aorta_rois import extract_aorta_vois, AortaSegment
import nibabel as nib
import numpy as np
from hedypet.utils import load_splits, load_sidecar, RAW_ROOT, DERIVATIVES_ROOT
from pathlib import Path
from matplotlib import pyplot as plt
import os 
import json
from utils import TS_CLASS_TO_LABEL, plot_patplak

WORKING_DIR = Path("/depict/users/hinge/private/hedypet/dynamic")
CYLINDER_VOLUME_ML = 1
CYLINDER_WIDTH_PX = 3

def run_save_patlak(tac,if_tac,frame_time_middle, out_dir, region_name, n_frames_regression=4,save_img=False):
    slope, intercept, X, Y = roi_patlak(tac,if_tac,frame_time_middle,n_frames_regression)
    ki_path = os.path.join(out_dir,f"{region_name}_Ki.txt")
    os.makedirs(out_dir,exist_ok=True)
    np.savetxt(ki_path,np.array([slope]))

    if save_img:
        plt.figure(figsize=(4,3))
        plot_patplak(X,Y,slope,intercept,n_frames_regression)
        plt.title(region_name)
        plt.legend()
        plt.savefig(ki_path.replace(".txt",".jpg"))

def extract_vois_and_if(
        dpet_path,
        totalseg_path,
        aorta_voi=AortaSegment.DESCENDING_BOTTOM,
        t_threshold = 40,
        volume_ml = 1,
        cylinder_width = 3
        ):
    
    sidecar = load_sidecar(dpet_path)
    frame_time_start = np.array(sidecar['FrameTimesStart'])
    frame_time_duration = np.array(sidecar['FrameDuration'])
    frame_time_middle = frame_time_start + frame_time_duration/2

    totalseg = nib.load(totalseg_path)
    aorta_seg = totalseg.get_fdata()==52
    aorta_vois, aorta_segments = extract_aorta_vois(aorta_seg, totalseg.affine, dpet_path, frame_time_start, t_threshold=t_threshold, volume_ml=volume_ml,cylinder_width=cylinder_width)
    
    if isinstance(aorta_voi,AortaSegment):
        aorta_voi = aorta_voi.value

    if_tac = extract_tac(dpet_path, aorta_vois==aorta_voi)
    
    return aorta_vois, aorta_segments, if_tac, frame_time_middle

def main(sub):
    DYN_DERIVATIVES = DERIVATIVES_ROOT / f"pipeline-bodydyn/{sub}"

    #input_files
    dpet_path = next((RAW_ROOT / sub).glob("pet/*acdyn*_pet.nii.gz"))
    totalseg_path = next(DYN_DERIVATIVES.glob("anat/*total*_dseg.nii.gz"))

    #output_files
    aorta_segments_path = (WORKING_DIR / sub) / "aorta_segments.nii.gz"
    aorta_vois_path = (WORKING_DIR / sub) / "aorta_vois.nii.gz"
    if_tac_path = (WORKING_DIR / sub) / "if_tac.txt"
    t_path = (WORKING_DIR / sub) / "t_tac.txt"
    patlak_f10_path = (WORKING_DIR / sub) / "patlak_f10.nii.gz"
    organs_tacs_path = (WORKING_DIR / sub) / "tacs_no_erosion.json"
    
    # Extract and save aorta_desc tac, vois, and frametimes
    if not if_tac_path.exists():
        print("Extracting aorta tacs")
        dpet = nib.load(dpet_path)
        totalseg = nib.load(totalseg_path)

        aorta_vois, aorta_segments, if_tac, frame_time_middle = extract_vois_and_if(dpet_path,totalseg_path)
        os.makedirs((WORKING_DIR / sub),exist_ok=True)
        np.savetxt(if_tac_path, if_tac)
        np.savetxt(t_path,frame_time_middle)
        nib.save(nib.Nifti1Image(aorta_vois,totalseg.affine),aorta_vois_path)
        nib.save(nib.Nifti1Image(aorta_segments,totalseg.affine), aorta_segments_path)

    # Run voxel patlak
    if not patlak_f10_path.exists():
        out, _ = voxel_patlak(dpet_path,if_tac,frame_time_middle,n_frames_linear_regression=10,axial_chunk_size=32)
        nib.save(nib.Nifti1Image(out, totalseg.affine),patlak_f10_path)
    
    return
    #regions = [90,1,2,3,4,5,6,7,15,16,20,22,52]
    regions = [90]
    
    # Extract organ vois
    if not organs_tacs_path.exists():
        seg = nib.load(totalseg_path).get_fdata()
        
        seg[~np.isin(seg,regions)] = 0
        tacs = extract_multiple_tacs(dpet, seg)

        with open(organs_tacs_path,"w") as handle:
            json.dump(tacs,handle,indent=4,sort_keys=True)

    if_tac = np.loadtxt(if_tac_path)
    frame_time_middle = np.loadtxt(t_path)

    # Run patlak for each organ
    with open(organs_tacs_path,"r") as handle:
        tacs = json.load(handle)

    for reg in regions:
        tac = np.array(tacs[str(reg)])
        out_dir = (WORKING_DIR / sub) / "organs"
        run_save_patlak(
            tac,
            if_tac = if_tac,
            frame_time_middle=frame_time_middle,
            out_dir = out_dir,
            region_name = TS_CLASS_TO_LABEL[str(reg)],
            n_frames_regression=6,
            save_img=True
        )

subs = load_splits()["all"]
for sub in subs:
    try:
        main(sub=sub)
    except:
        continue
