
import json
import os
from hedypet.preprocessing.resample import resample_series
import re

def path_to_bids_uri(image_path):
    dataset_root , sub,  relative_path = re.split("/(sub-.{3})/",str(image_path))
    dataset_name = os.path.basename(dataset_root)
    return f"bids:{dataset_name}:{sub}/{relative_path}"

def make_pipeline_derivative_name(img_path,pipeline_root,derivative_entities):
    _ , sub,  relative_path = re.split("/(sub-.{3})/",str(img_path))
    source, suffix,_ = re.split("(_[^_]*\.nii\.gz)", relative_path)
    out_path = (pipeline_root / sub) / (source + derivative_entities +suffix)
    return out_path

def create_derivatives_sidecar(image_path,reference, sources=[],**kwargs):
    if str(image_path).endswith(".nii.gz"):
        outjson = str(image_path).replace(".nii.gz",".json")
    else:
        outjson = str(image_path.parent / (image_path.stem +".json"))
    sources = [path_to_bids_uri(source) for source in sources]
    try:
        ref_uri = path_to_bids_uri(reference)
    except:
        ref_uri = None
    sidecar = {
            "SpatialReference": ref_uri,
            "Sources":sources,
        }
    sidecar.update(**kwargs)
    os.makedirs(os.path.dirname(outjson),exist_ok=True)
    with open(outjson,"w") as handle:
        json.dump(sidecar,handle,sort_keys=True,indent=4)

def resample_and_save_bids(img_path,target,spatial_reference,pipeline_root, derivative_entities,cval,order,rigid_registration=None, overwrite=False, is_2d_acquisition=False,**sidecar_entries):
    out_path = make_pipeline_derivative_name(img_path,pipeline_root,derivative_entities)
    
    if not out_path.exists() or overwrite:
        resample_series(
            img_path,
            target,
            out_path,
            pre_affine=rigid_registration,
            cval=cval,
            order=order,
            mode = "nearest" if is_2d_acquisition else "constant",
            is_2d_acquisition=is_2d_acquisition
        )
        sources = [img_path]

        if rigid_registration is not None:
            sources.append(rigid_registration)

        create_derivatives_sidecar(
            out_path, 
            reference=spatial_reference,
            sources=sources,
            **sidecar_entries
        )

    return out_path
