#%%
from preprocessing.registration import register_rigid_ants
from hedypet.utils import load_splits, save_numpy_array
from tqdm import tqdm
from bids import resample_and_save_bids

def main(subs,raw_root,derivatives_root,pipeline_name,derivatives_entities):

    default_args = {
        "pipeline_root":derivatives_root / pipeline_name,
        "derivative_entities":derivatives_entities,
        "Space": "Static PET space"
    }
    
    for sub in tqdm(subs):
        
        sub_root = raw_root / sub
        registration_matrix = derivatives_root / f"registration_matrices/{sub}/mr2petct_body.txt"

        # Create MR-to-PET/CT rigid registration transform
        if not registration_matrix.exists():

            mr = next(sub_root.glob("anat/*DIXONbodyIN_T1w.nii.gz"))
            ct = next(sub_root.glob("anat/*_ct.nii.gz"))

            aff = register_rigid_ants(moving_path=mr,fixed_path=ct)
            save_numpy_array(aff,registration_matrix)
        
        target = next(sub_root.glob("pet/*acstatPSF_pet.nii.gz"))
        
        #Resample CT
        ct = next(sub_root.glob("anat/*_ct.nii.gz"))
        resample_and_save_bids(ct,target,target,cval=-1024,order=3,**default_args)
        
        #Resample Topogram
        try:
            xray = next(sub_root.glob("anat/*Xray.nii.gz"))
            resample_and_save_bids(xray,target,target,cval=-1024,order=3,is_2d_acquisition=True,**default_args)
        except StopIteration:
            pass
        #Rigid Move and Resample MRI
        fastview = next(sub_root.glob("anat/*FASTVIEW*.nii.gz"))
        resample_and_save_bids(fastview,target,target,cval=0,order=3,rigid_registration=registration_matrix,**default_args)
        
        for mr in sub_root.glob("anat/*DIXONbody*.nii.gz"):
            resample_and_save_bids(mr,target,target,cval=0,order=3,rigid_registration=registration_matrix,**default_args)
        
        #Resample derivatives
        for seg in derivatives_root.glob(f"totalsegmentator/{sub}/**/*.nii.gz"):
            resample_and_save_bids(seg,target,target,cval=0,order=0,**default_args)    

if __name__ == "__main__":
    from hedypet.utils import RAW_ROOT, DERIVATIVES_ROOT

    PIPELINE_NAME = "pipeline-bodystat"
    DERIVATIVE_ENTITIES = f"_space-individual"

    subs = load_splits()["all"]
    main(subs,RAW_ROOT,DERIVATIVES_ROOT,PIPELINE_NAME,DERIVATIVE_ENTITIES)


    
# %%
