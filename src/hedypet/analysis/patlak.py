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
from collections import defaultdict

WORKING_DIR = Path("/depict/users/hinge/private/hedypet/dynamic")

def run_save_patlak(tac,if_tac,frame_time_middle, out_dir, region_name, n_frames_regression=4,save_img=False):
    slope, intercept, X, Y = roi_patlak(tac,if_tac,frame_time_middle,n_frames_regression)
    ki_path = os.path.join(out_dir,f"{region_name}_Ki.txt")
    os.makedirs(out_dir,exist_ok=True)

    if save_img:
        plt.figure(figsize=(4,3))
        plot_patplak(X,Y,slope,intercept,n_frames_regression)
        plt.title(region_name)
        plt.ylim(np.nanmin(Y),np.nanmax(Y[-n_frames_regression:])*1.1)
        plt.legend()
        plt.savefig(ki_path.replace(".txt",".jpg"))

def main(sub,segment,aorta_if_erode,full):

    tag = f"{segment}_errode-{aorta_if_erode}_full-{full}"

    #output_files
    if_tac_path = (WORKING_DIR / sub) / f"if_tac_{tag}.txt"
    t_path = (WORKING_DIR / sub) / "t_tac.txt"
    
    frame_time_middle = np.loadtxt(t_path)
    if_tac = np.loadtxt(if_tac_path)
    for erosion in [0,1,2,3]:

        organs_tacs_path = (WORKING_DIR / sub) / f"tacs_erosion_{erosion}.json"

        # Run patlak for each organ
        with open(organs_tacs_path,"r") as handle:
            tacs = json.load(handle)
        
        frames = [2,3,4,5,6,7,8,9,10,11,12]
        kis = {
            "frames": frames,
            "organ_ki": defaultdict(list) 
        }
        
        out_dir = (WORKING_DIR / sub) / f"run-{tag}"
        os.makedirs(out_dir,exist_ok=True)
        out_file = out_dir/f"Ki_erosion{erosion}.json"
        if not out_file.exists():
            for reg in tacs:
                for n_frames in frames:
                    tac = np.array(tacs[reg])
                    
                    slope, intercept, X, Y = roi_patlak(tac,if_tac,frame_time_middle,n_frames)
                    kis["organ_ki"][TS_CLASS_TO_LABEL[str(reg)]].append(float(slope))

                    if n_frames == 6 and erosion == 0:
                        run_save_patlak(
                            tac,
                            if_tac = if_tac,
                            frame_time_middle=frame_time_middle,
                            out_dir = out_dir,
                            region_name = TS_CLASS_TO_LABEL[str(reg)]+f"_erosion_{erosion}_nframes_{n_frames}",
                            n_frames_regression=n_frames,
                            save_img= True,
                        )

            with open(out_file,"w") as handle:
                json.dump(kis,handle,indent=4,sort_keys=True)
        else:
            print(out_dir)

subs = load_splits()["all"]
for sub in subs:

    try:
        main(
            sub=sub,
            segment=AortaSegment.DESCENDING_BOTTOM,
            aorta_if_erode=1,
            full=True)

        main(
            sub=sub,
            segment=AortaSegment.DESCENDING,
            aorta_if_erode=1,
            full=True)
        
        main(
            sub=sub,
            segment=AortaSegment.DESCENDING_BOTTOM,
            aorta_if_erode=0,
            full=True)

        main(
            sub=sub,
            segment=AortaSegment.DESCENDING,
            aorta_if_erode=0,
            full=True)

        main(
            sub=sub,
            segment=AortaSegment.DESCENDING_BOTTOM,
            aorta_if_erode=2,
            full=True)

        main(
            sub=sub,
            segment=AortaSegment.DESCENDING,
            aorta_if_erode=2,
            full=True)
        
        main(
            sub=sub,
            segment=AortaSegment.DESCENDING_BOTTOM,
            aorta_if_erode=0,
            full=False)

        main(
            sub=sub,
            segment=AortaSegment.DESCENDING,
            aorta_if_erode=0,
            full=False)
        
    except FileNotFoundError:
        pass

# %%
