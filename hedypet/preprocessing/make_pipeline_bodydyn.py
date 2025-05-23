#%%
from hedypet.utils import load_splits
from tqdm import tqdm
from bids import resample_and_save_bids

def main(subs,raw_root,derivatives_root,pipeline_name,derivatives_entities):

    default_args = {
        "pipeline_root":derivatives_root / pipeline_name,
        "derivative_entities":derivatives_entities,
        "Space": "Dynamic PET space"
    }
    
    for sub in tqdm(subs):
        
        sub_root = raw_root / sub
        registration_matrix_head = derivatives_root / f"registration_matrices/{sub}/mr2petct_head.txt"

        # run make_pipeline_head to create registration_matrices
        assert registration_matrix_head.exists()

        try:
            target = next(sub_root.glob("pet/*acdyn*_pet.nii.gz"))
        except:
            continue
        
        #Resample CT
        ct = next(sub_root.glob("anat/*_ct.nii.gz"))
        resample_and_save_bids(ct,target,target,cval=-1024,order=3,**default_args)
        
        #Resample derivatives
        for seg in derivatives_root.glob(f"totalsegmentator/{sub}/**/*.nii.gz"):
            resample_and_save_bids(seg,target,target,cval=0,order=0,**default_args)    
        
        for seg in derivatives_root.glob(f"synthseg/{sub}/**/*.nii.gz"):
            resample_and_save_bids(seg,target,target,cval=0,order=0,rigid_registration=registration_matrix_head,**default_args)  

if __name__ == "__main__":
    from hedypet.utils import RAW_ROOT, DERIVATIVES_ROOT

    PIPELINE_NAME = "pipeline-bodydyn"
    DERIVATIVE_ENTITIES = f"_space-individual"

    subs = load_splits()["all"]
    main(subs,RAW_ROOT,DERIVATIVES_ROOT,PIPELINE_NAME,DERIVATIVE_ENTITIES)


    
# %%
