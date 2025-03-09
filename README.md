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

## Repository Structure

```
DATAD/

```

### 2. Data Format
The subset consists of:
- **Gaze Data**: Eye-tracking coordinates, timestamps, fixation durations
- **Driving Data**: Steering angles, brake and accelerator positions, speed
- **Traffic Context**: Surrounding vehicle positions, velocities, and object categories
- **RGB Images**: Raw images of the driver’s foreground view
- **Semantic Segmentation Maps**: Instance-labeled foreground objects

### 3. Using the Dataset
Load the dataset using Python:
```python
wait update
```

### 4. Visualizing Gaze Trajectories
Run the visualization script to generate gaze point picture:
```bash
wait update
```



## License
This dataset is released under the MIT License. See `LICENSE` for details.



