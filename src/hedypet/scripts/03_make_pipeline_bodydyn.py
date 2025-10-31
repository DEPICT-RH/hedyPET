from hedypet.utils import load_splits
from tqdm import tqdm
from hedypet.preprocessing.resampling import resample_and_save_bids

def main(sub,static_root,dynamic_root):

    dynamic_derivatives_root = dynamic_root / "derivatives"
    static_derivatives_root = static_root / "derivatives"

    default_args = {
        "pipeline_root":dynamic_derivatives_root / "pipeline-bodydyn",
        "derivative_entities":f"_space-individual",
        "Space": "Dynamic PET space"
    }

    sub_static_root = static_root / sub
    sub_dynamic_root = dynamic_root  /sub

    registration_matrix_head = static_derivatives_root / f"registration_matrices/{sub}/mr2petct_head.txt"
    registration_matrix = static_derivatives_root / f"registration_matrices/{sub}/mr2petct_body.txt"

    # run make_pipeline_head and make_pipeline_bodstat to create registration_matrices
    assert registration_matrix_head.exists()
    assert registration_matrix.exists()

    target = next(sub_dynamic_root.glob("ses-quadra/pet/*acdyn*_pet.nii.gz"))
    
    #Resample CT
    for ct in sub_static_root.glob("ses-quadra/ct/*_ct.nii.gz"):
        resample_and_save_bids(ct,target,target,cval=-1024,order=3,**default_args)
    
    #Resample Topogram
    try:
        xray = next(sub_static_root.glob("ses-quadra/ct/*Xray.nii.gz"))
        resample_and_save_bids(xray,target,target,cval=-1024,order=3,is_2d_acquisition=True,**default_args)
    except StopIteration:
        # One participant does not have Xray acq.
        pass
    
    #Rigid Move and Resample MRI
    fastview = next(sub_static_root.glob("ses-vida/anat/*FASTVIEW*.nii.gz"))
    resample_and_save_bids(fastview,target,target,cval=0,order=3,rigid_registration=registration_matrix,**default_args)
    
    for mr in sub_static_root.glob("ses-vida/anat/*DIXONbody*.nii.gz"):
        resample_and_save_bids(mr,target,target,cval=0,order=3,rigid_registration=registration_matrix,**default_args)

    #Resample derivatives
    for seg in static_derivatives_root.glob(f"totalsegmentator/{sub}/**/*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,**default_args)    
    
    for seg in static_derivatives_root.glob(f"synthseg/{sub}/**/*.nii.gz"):
        resample_and_save_bids(seg,target,target,cval=0,order=0,rigid_registration=registration_matrix_head,**default_args)  
    
if __name__ == "__main__":
    from hedypet.utils import STATIC_ROOT, DYNAMIC_ROOT
    from multiprocessing import Pool
    
    subs = load_splits()["all"]
    
    def worker(sub):
        return main(sub, STATIC_ROOT,DYNAMIC_ROOT)
    
    with Pool(12) as pool:
        list(tqdm(pool.imap(worker, subs), total=len(subs)))