# hedyPET Dataset 🧠

![hedyPET banner](banner.jpg)

A multimodal total-body dynamic 18F-FDG PET/CT/MRI dataset of 100 healthy humans for quantitative imaging research.

📊 **[Data Explorer](https://hedypet.streamlit.app)** | 📥 **[Get Data](https://datacatalog.publicneuro.eu/dataset/super/V2)** | 📄 **[Read Publication](manuscript/main.tex)**

## Overview

The hedyPET dataset provides comprehensive multimodal imaging data from 100 healthy participants, stratified by age and sex to capture physiological variation across the adult lifespan. This dataset addresses the critical need for normative reference data in quantitative PET imaging research.

### Dataset Highlights ✨

**Raw Imaging Data**
- **100 healthy participants** (18-100 years, stratified by age and sex) 👥
- **Multiple PET reconstructions** (static and dynamic, with/without attenuation correction) 🔄
- **Listmode PET data** (.ptd format) for flexible retrospective reconstruction 📊
- **Topogram and Low-dose CT** for anatomical reference and attenuation correction 🩻
- **Whole-body DIXON MRI and T1 MPRAGE** for soft tissue characterization 🧲

**Processed Derivatives**
- **Anatomical segmentations** TotalSegmentator (organs, tissue, and bodyparts), SynthSeg (brain), and nifti_dynamic (input functions) 🧩
- **Pre-extracted time-activity curves** for all organs and tissues 📈
- **Coordinate spaces** Image resampled to different spaces (body-static, body-dynamic, head-space) 🎯
- **Normalization constants** (SUV, SUL, Patlak Ki) ⚖️

## How to Acquire Data 📥

### Pre-computed readouts 
The repository includes pre-computed quantitative measures for the **80 train/validation subjects** in the `readouts/` folder:
- Time-activity curves (TACs) for all organs and tissues
- Static SUV/SUL measurements with/without mask erosion
- Patlak Ki values
- Participant metadata and demographics

🌐 **Explore the data interactively**: [hedypet.streamlit.app](https://hedypet.streamlit.app)

### Full Image Data (Application Required)
Apply for complete imaging data (PET/CT/MRI) by signing up at [datacatalog.publicneuro.eu](https://datacatalog.publicneuro.eu/dataset/super/V2) and completing the Data User Agreement.

> **Note**: Only 80 train/validation subjects are available. The remaining 20 test subjects are reserved for upcoming competitions.

## Installation & Setup ⚙️

1. **Clone the repository:**
```bash
git clone https://github.com/depict-rh/hedypet.git
cd hedypet
```

2. **Install the package:**
```bash
pip install -e .
```

3. **Set up environment variables:**
Set the required environment variables:
```bash
export RAW_ROOT=/path/to/hedypet/raw
export DERIVATIVES_ROOT=/path/to/hedypet/derivatives
```

## Usage Examples

### Load participant data and splits
```python
from hedypet.utils import load_splits, get_participant_metadata

# Load predefined train/test splits
splits = load_splits()
train_subjects = splits['train']  # 80 subjects
test_subjects = splits['test']    # 20 subjects

# Get participant demographics
metadata = get_participant_metadata('sub-001')
print(f"Age: {metadata['age']}, Sex: {metadata['sex']}")
```

### Extract time-activity curves
```python
from hedypet.preprocessing.tacs import extract_tacs
import pandas as pd

# Load pre-extracted TACs for liver analysis
tacs_file = "derivatives/tacs/sub-001/acdynPSF/ts_total/erosion-0/liver.csv"
tac_data = pd.read_csv(tacs_file)
print(tac_data.head())
```

## Data Processing Pipeline 🔧

The derivatives, standardized coordinate spaces, and readouts were created using a series of preprocessing scripts. Here's the complete workflow:

### Core Processing Scripts
```bash
# 1. Create body-static coordinate space (co-register all modalities)
python src/hedypet/scripts/01_make_pipeline_bodystat.py

# 2. Create head coordinate space (high-resolution brain analysis)  
python src/hedypet/scripts/02_make_pipeline_head.py

# 3. Create body-dynamic coordinate space (for kinetic modeling)
python src/hedypet/scripts/03_make_pipeline_bodydyn.py

# 4. Generate normalization constants (for SUV/SUL calculations)
python src/hedypet/scripts/04_make_normalization_consts.py

# 5. Create aorta input function ROIs (for kinetic modeling)
python src/hedypet/scripts/05_make_input_function_rois.py

# 6. Extract time-activity curves and static measurements
python src/hedypet/scripts/06_extract_tacs_and_means.py
python src/hedypet/scripts/06_extract_tacs_ct.py
```


For detailed methodology, technical specifications, and validation results, see the accompanying manuscript in the `manuscript/` directory.

## Citation 📝

If you use this dataset, please cite:

```bibtex
@article{hinge2024hedypet,
  title={A multimodal total-body dynamic 18F-FDG PET/CT/MRI dataset of 100 healthy humans},
  author={Hinge, Christian and others},
  journal={Scientific Data},
  year={2024},
  publisher={Nature},
  doi={10.xxxx/xxxxxxx}
}
```

## Repository Structure

- **`src/hedypet/`**: Core Python package
  - **`preprocessing/`**: Image processing and registration utilities
  - **`analysis/`**: Analysis tools and notebooks
  - **`scripts/`**: Processing pipeline scripts
- **`readouts/`**: Pre-computed quantitative measures
- **`manuscript/`**: LaTeX manuscript source


## Acknowledgments

We thank Siemens Healthineers for funding, the Danish Blood Donor Study for recruitment, and all participants who contributed to this research. Special thanks to the teams at Rigshospitalet for data acquisition and technical support.

---

**Happy analyzing! 🚀**