import nibabel as nib
from hedypet.utils import load_splits, DERIVATIVES_ROOT
from tqdm import tqdm
from hedypet.preprocessing.normalization import *
from hedypet.utils import *
from hedypet.preprocessing.utils import *
from hedypet.preprocessing.bids import *
from pet_id import suv_id

def main(sub,raw_root,derivatives_root):
    
    sub_root = raw_root / sub
    pipeline_root= derivatives_root / "pet_norm_consts"
    
    pet_path = next(sub_root.glob("pet/*acstatPSF_pet.nii.gz"))
    ts_total_path = next(derivatives_root.glob(f"totalsegmentator/{sub}/**/*br38f*total*.nii.gz"))
    ts_body_path = next(derivatives_root.glob(f"totalsegmentator/{sub}/**/*br38f*body*.nii.gz"))
    ts_tissue_path = next(derivatives_root.glob(f"totalsegmentator/{sub}/**/*br38f*tissue*.nii.gz"))
    
    pet_nii = nib.load(pet_path)
    ts_total_nii = nib.load(ts_total_path)
    ts_body_nii = nib.load(ts_body_path)
    ts_tissue_nii = nib.load(ts_tissue_path)
    
    metadata = get_participant_metadata(sub)
    weight = metadata["weight"]
    dose = metadata["InjectedRadioactivity"]*1e6 
    sex = metadata["sex"]
    height = metadata["height"]

    if not (save_path:=((pipeline_root/sub) / "suv.txt")).exists():
        const = SUV(injected_dose=dose,patient_weight=weight)
        save_constant_bids(const,save_path,description="Body weight SUV",sources=[pet_path])
    
    if not (save_path:=((pipeline_root/sub) / "sul_janma.txt")).exists():
        const = SUL_janma(injected_dose=dose,patient_weight=weight,patient_height=height,patient_sex=sex)
        save_constant_bids(const,save_path,description="Lean body mass normalized SUV (SUL) using the Janmahasatian LBM formula https://doi.org/10.2165/00003088-200544100-00004",sources=[pet_path])
    
    if not (save_path:=((pipeline_root/sub) / "sul_james.txt")).exists():
        const = SUL_james(injected_dose=dose,patient_weight=weight,patient_height=height,patient_sex=sex)
        save_constant_bids(const,save_path,description="Lean body mass normalized SUV (SUL) using James LBM formula https://doi.org/10.2967/jnumed.113.136986",sources=[pet_path])
    
    if not (save_path:=((pipeline_root/sub) / "sul_decazes.txt")).exists():
        const = SUL_decazes(injected_dose=dose,patient_weight=weight,ts_total_nii=ts_total_nii,ts_tissue_nii=ts_tissue_nii)
        save_constant_bids(const,save_path,description="Lean body mass normalized SUV (SUL) using CT and VI equation from Decazes et al. 2016",sources=[pet_path,ts_total_path,ts_tissue_path])
    
    if not (save_path:=((pipeline_root/sub) / "suv_id.txt")).exists():
        const = suv_id(pet_nii, ts_total_nii,ts_tissue_nii,ts_body_nii)
        save_constant_bids(const,save_path,description="Image-derived (id) body weight SUV",sources=[pet_path,ts_total_path,ts_tissue_path,ts_body_path])
    
if __name__ == "__main__":
    from hedypet.utils import RAW_ROOT, DERIVATIVES_ROOT

    subs = load_splits()["all"]
    for sub in tqdm(subs):

        main(sub,RAW_ROOT,DERIVATIVES_ROOT)

