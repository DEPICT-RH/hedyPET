from hedypet.utils import load_splits
from tqdm import tqdm
from bids import resample_and_save_bids

def main(sub,raw_root,derivatives_root):

    default_args = {
        "pipeline_root":derivatives_root / "pipeline-bodydyn",
        "derivative_entities":f"_space-individual",
        "Space": "Dynamic PET space"
    }

    sub_root = raw_root / sub
    registration_matrix_head = derivatives_root / f"registration_matrices/{sub}/mr2petct_head.txt"

    # run make_pipeline_head to create registration_matrices
    assert registration_matrix_head.exists()

    try:
        target = next(sub_root.glob("pet/*acdyn*_pet.nii.gz"))
    except:
        print("No dynamic PET found for", sub)
        return
    
    #Resample CT
    ct = next(sub_root.glob("anat/*_ct.nii.gz"))
    resample_and_save_bids(ct,target,target,cval=-1024,order=3,**default_args)
    
    #Resample derivatives
    for seg in derivatives_root.glob(f"totalsegmentator/{sub}/**/*br38f*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,**default_args)    
    
    for seg in derivatives_root.glob(f"synthseg/{sub}/**/*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,rigid_registration=registration_matrix_head,**default_args)  
    
if __name__ == "__main__":
    from hedypet.utils import RAW_ROOT, DERIVATIVES_ROOT

    subs = load_splits()["all"]
    for sub in tqdm(subs):
        main(sub,RAW_ROOT,DERIVATIVES_ROOT)