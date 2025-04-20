
# DATAD: Driver Attention in Takeover of Autonomous Driving

## Overview

**DATAD** (Driver Attention in Takeover of Autonomous Driving) is a dataset specifically designed for human-machine interaction research in autonomous driving. It captures driver gaze behavior, operational inputs, and surrounding traffic dynamics during emergency takeovers. 

The dataset is collected from **60 participants** across **12 types of takeover scenarios** and includes approximately **600,000 frames** of gaze point data. This dataset provides insights into driver attention allocation, which is essential for enhancing autonomous vehicle safety and human-machine interaction strategies.

## Features
- **Large-scale dataset**: 600,000 frames of driver gaze behavior
- **High-fidelity simulation**: Collected using CARLA-based driving simulators
- **Comprehensive driving context**: Includes gaze data, vehicle control inputs, and surrounding traffic information
- **Emergency scenarios**: Captures real-time driver reactions to critical events
- **Rich metadata**: Position, velocity, acceleration, and yaw angle of surrounding vehicles


## Dataset Examples

### 🧪 Equipment Setup
![Equipment](https://github.com/OOPartsfili/DATAD/raw/main/image/equip.png)

### ✅ Output Check Example
![Output Check](https://github.com/OOPartsfili/DATAD/raw/main/image/output_check.png)



## Repository Structure

```
DATAD/
├── DATA/               # Main dataset (not included here due to large size)
│   ├── Tester1/
│   ├── Tester2/
│   └── ...             # Up to Tester10
├── Script/             # Python scripts for processing and visualization
│   ├── visualize_gaze.py
│   └── ...
├── README.md
└── LICENSE
```

> 💾 Due to storage limitations, the full dataset (~40 GB per subject) is not hosted in this repository.  
> You can download individual subjects' data at:  
> 👉 https://huggingface.co/datasets/OOParts/DATAD

---

## 2. Data Format

Each subject's folder (e.g., `Tester1/`) contains:
- **Gaze Data**: Eye-tracking coordinates, timestamps, fixation durations
- **Driving Data**: Steering angles, brake and accelerator positions, speed
- **Traffic Context**: Surrounding vehicle positions, velocities, and object categories
- **RGB Images**: Raw images of the driver’s foreground view
- **Semantic Segmentation Maps**: Instance-labeled foreground objects

---

## 3. Using the Dataset

Download the dataset and you can directly use it by reading readme in each filefold:


## License

This dataset is released under the MIT License. See `LICENSE` for details.
