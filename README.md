
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

### 🧪 Data Collection Platform Description
![Data Collection Platform](https://github.com/OOPartsfili/DATAD/raw/main/image/equip.png)

To ensure the authenticity of gaze data, all takeover scenarios in this dataset were conducted on a real-vehicle-based driving simulation platform. As shown in the images above, the platform integrates a full-scale real vehicle with an immersive surround projection system, providing participants with highly realistic visual and operational feedback. The setup includes:

Real Vehicle Platform: As shown in the top-left image, we built a four-wheel dynamometer testbed with adjustable wheelbase, enabling compatibility with real vehicles of different brands and sizes. Since the driver operates an actual vehicle ("real car in loop"), the use of a genuine steering wheel, accelerator, and brake pedals ensures high fidelity in driving interaction (including rollable wheels).

Surround Projection System: The driving environment is rendered in CARLA and projected onto a large-angle curved screen, creating an immersive and realistic visual experience. As shown in the second and third images on the left, the virtual scenes faced by the driver closely resemble real road environments.

Remote Eye-Tracking System: As shown in the third image, a contactless remote eye tracker is installed inside the cabin. It records gaze point coordinates continuously at 60 Hz and also captures physiological metrics such as eyelid openness and pupil diameter.


### ✅ Qualitative Comparison
![Qualitative Comparison](https://github.com/OOPartsfili/DATAD/raw/main/image/output_check.png)
As shown in Fig. X, we visualize the gaze prediction results across three critical frames in an urban driving scenario involving a sudden vehicle intrusion from the right. Our model, PILOT, demonstrates strong consistency with the ground truth by accurately capturing the driver’s gaze shift from the forward-looking position (Frame #195) to the intruding vehicle (Frame #205). Compared to baseline methods, PILOT maintains sharper focus and better temporal consistency. In contrast, models such as DRIVE and PGnet tend to exhibit dispersed attention or delayed reactions. DBVM sometimes overemphasizes non-salient distant regions, while DR(eye)VE often fixates on central or static objects, missing dynamic threats. These observations highlight the superiority of PILOT in modeling attention transitions in real-time, safety-critical scenes.


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
