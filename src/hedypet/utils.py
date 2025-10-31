from pathlib import Path
from dotenv import load_dotenv
import os 
import json
import numpy as np
import pandas as pd

load_dotenv()

DYNAMIC_ROOT = Path(os.environ["hedypet_dynamic_root"])
STATIC_ROOT = Path(os.environ["hedypet_static_root"])



def load_splits():
    with open(Path(__file__).parents[2] / "data_splits.json","r") as handle:
        return json.load(handle)
    
def load_sidecar(image_path):
    with open(str(image_path).replace(".nii.gz",".json"),"r") as handle:
        return json.load(handle)
    
def get_time_frames_midpoint(sub):
    dpet_path = next((DYNAMIC_ROOT / sub).glob("ses-quadra/pet/*acdyn*_pet.nii.gz"))
    sidecar = load_sidecar(dpet_path)
    frame_time_start = np.array(sidecar['FrameTimesStart'])
    frame_time_duration = np.array(sidecar["FrameDuration"])
    return frame_time_start + frame_time_duration/2

def get_participant_metadata(sub):
    df = pd.read_csv(STATIC_ROOT / "participants.tsv",sep="\t")
    row = df[df.participant_id == sub].iloc[0].to_dict()
    row["InjectedRadioactivity"] = load_sidecar(next((STATIC_ROOT / sub).glob("ses-quadra/pet/*acstat*_pet.nii.gz")))["InjectedRadioactivity"]
    return row

def get_norm_consts(sub):
    norm_consts = {}
    for p in (STATIC_ROOT / "derivatives/pet_norm_consts").glob(f"{sub}/*.txt"):
        with open(p,"r") as handle:
            norm_consts[p.stem] = float(handle.read())
    return norm_consts
