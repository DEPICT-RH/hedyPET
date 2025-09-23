#%%
from hedypet.preprocessing.registration import register_rigid_ants
from hedypet.utils import load_splits
from hedypet.preprocessing.utils import get_head_center, get_voxmap_around_centerpoint, save_numpy_array
from tqdm import tqdm
from hedypet.preprocessing.bids import resample_and_save_bids
import numpy as np

def main(sub,
         raw_root,
         derivatives_root,
         size_mm = (179,230,205),
         isotropic_mm=0.8):
    
    isotropic_mm_str = str(isotropic_mm).replace(".","")

    default_args = {
        "pipeline_root":derivatives_root / f"pipeline-head{isotropic_mm_str}mm",
        "derivative_entities":f"_space-individual_res-{isotropic_mm_str}mm",
        "Resolution":f"{isotropic_mm}mm",
        "Space":f"Head space isometric FOV {size_mm}mm"
    }
    
    sub_root = raw_root / sub
    registration_matrix = derivatives_root / f"registration_matrices/{sub}/mr2petct_head.txt"
    center_head = derivatives_root / f"registration_matrices/{sub}/centerpoint_petct_head.txt"
    totalseg = next(derivatives_root.glob(f"totalsegmentator/{sub}/**/*total*dseg.nii.gz"))

    if not center_head.exists():
        center_head_arr = get_head_center(totalseg)
        save_numpy_array(center_head_arr,output_path=center_head)

    # Create target voxmap centered around brain
    center_head_arr = np.loadtxt(center_head)
    target = get_voxmap_around_centerpoint(center_head_arr,isotropic_mm,size_mm)

    #Resample CT
    ct = next(sub_root.glob("anat/*_ct.nii.gz"))
    ct_out = resample_and_save_bids(ct,target,ct, cval=-1024,order=3,**default_args)

    # Create MR-to-PET/CT rigid registration transform
    # The cropped CT is used as target
    if not registration_matrix.exists():

        mr = next(sub_root.glob("anat/*MPRAGE*_T1w.nii.gz"))

        aff = register_rigid_ants(moving_path=mr,fixed_path=ct_out)
        save_numpy_array(aff,registration_matrix)
    
    #Resample CT
    ct = next(sub_root.glob("anat/*_ct.nii.gz"))
    resample_and_save_bids(ct,target,ct,cval=-1024,order=3,**default_args)
    
    #Resample Topogram
    try:
        xray = next(sub_root.glob("anat/*Xray.nii.gz"))
        resample_and_save_bids(xray,target,ct,cval=-1024,order=3,is_2d_acquisition=True,**default_args)
    except StopIteration:
        pass
    
    #Resample PET
    for pet in sub_root.glob("pet/*stat*_pet.nii.gz"):
        resample_and_save_bids(pet,target,ct,cval=0,order=3,**default_args)
    
    #Rigid Move and Resample MRI and MRI-derivatives
    fastview = next(sub_root.glob("anat/*FASTVIEW*.nii.gz"))
    resample_and_save_bids(fastview,target,ct,cval=0,order=3,rigid_registration=registration_matrix,**default_args)
    
    mprage = next(sub_root.glob("anat/*MPRAGE*.nii.gz"))
    resample_and_save_bids(mprage,target,ct,cval=0,order=3,rigid_registration=registration_matrix,**default_args)
    
    for mr in sub_root.glob("anat/*DIXONhead*.nii.gz"):
        resample_and_save_bids(mr,target,ct,cval=0,order=3,rigid_registration=registration_matrix,**default_args)
    
    for seg in derivatives_root.glob(f"synthseg/{sub}/**/*.nii.gz"):
        resample_and_save_bids(seg,target,ct,cval=0,order=0,rigid_registration=registration_matrix, **default_args)  


if __name__ == "__main__":
    from hedypet.utils import RAW_ROOT, DERIVATIVES_ROOT

    subs = load_splits()["all"]
    for sub in tqdm(subs):
        main(sub,RAW_ROOT,DERIVATIVES_ROOT)
