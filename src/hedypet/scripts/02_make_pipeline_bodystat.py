#%%
from hedypet.preprocessing.registration import register_rigid_ants
from hedypet.utils import load_splits
from hedypet.preprocessing.utils import save_numpy_array
from tqdm import tqdm
from hedypet.preprocessing.resampling import resample_and_save_bids

def main(sub,static_root):

    derivatives_root = static_root / "derivatives"

    default_args = {
        "pipeline_root":derivatives_root / "pipeline-bodystat",
        "derivative_entities":"_space-individual",
        "Space": "Static PET space"
    }
        
    sub_root = static_root / sub
    registration_matrix = derivatives_root / f"registration_matrices/{sub}/mr2petct_body.txt"
    registration_matrix_head = derivatives_root / f"registration_matrices/{sub}/mr2petct_head.txt"

    assert registration_matrix_head.exists()

    # Create MR-to-PET/CT rigid registration transform
    if not registration_matrix.exists():

        mr = next(sub_root.glob("ses-vida/anat/*DIXONbodyIN_T1w.nii.gz"))
        ct = next(sub_root.glob("ses-quadra/ct/*br38f_ct.nii.gz"))

        aff = register_rigid_ants(moving_path=mr,fixed_path=ct)
        save_numpy_array(aff,registration_matrix)
    
    target = next(sub_root.glob("ses-quadra/pet/*acstatPSF_pet.nii.gz"))
    
    #Resample CT
    for ct in sub_root.glob("ses-quadra/ct/*_ct.nii.gz"):
        resample_and_save_bids(ct,target,target,cval=-1024,order=3,**default_args)
    
    #Resample Topogram
    try:
        xray = next(sub_root.glob("ses-quadra/ct/*Xray.nii.gz"))
        resample_and_save_bids(xray,target,target,cval=-1024,order=3,is_2d_acquisition=True,**default_args)
    except StopIteration:
        # One participant does not have Xray acq.
        pass

    #Rigid Move and Resample MRI
    fastview = next(sub_root.glob("ses-vida/anat/*FASTVIEW*.nii.gz"))
    resample_and_save_bids(fastview,target,target,cval=0,order=3,rigid_registration=registration_matrix,**default_args)

    mprage = next(sub_root.glob("ses-vida/anat/*MPRAGE*.nii.gz"))
    resample_and_save_bids(mprage,target,ct,cval=0,order=3,rigid_registration=registration_matrix_head,**default_args)
    
    for mr in sub_root.glob("ses-vida/anat/*DIXONhead*.nii.gz"):
        resample_and_save_bids(mr,target,ct,cval=0,order=3,rigid_registration=registration_matrix_head,**default_args)
    
    for mr in sub_root.glob("ses-vida/anat/*DIXONbody*.nii.gz"):
        resample_and_save_bids(mr,target,target,cval=0,order=3,rigid_registration=registration_matrix,**default_args)
    
    #Resample derivatives
    for seg in derivatives_root.glob(f"totalsegmentator/{sub}/**/*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,**default_args)    

    for seg in derivatives_root.glob(f"synthseg/{sub}/**/*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,rigid_registration=registration_matrix_head,**default_args)  

if __name__ == "__main__":
    from hedypet.utils import STATIC_ROOT
    from multiprocessing import Pool
    
    subs = load_splits()["all"]
    
    def worker(sub):
        return main(sub, STATIC_ROOT)
    
    with Pool(12) as pool:
        list(tqdm(pool.imap(worker, subs), total=len(subs)))
    
# %%
