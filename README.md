# UR5 Volcani Workspace

UR5 arm mounted on the Volcaniarm table base for Gazebo simulation with ROS 2 Jazzy.

## Setup Instructions

### Clone the repository with submodules

```bash
mkdir -p <PATH>/ur5_ws
cd <PATH>/ur5_ws
git clone --recurse-submodules https://github.com/LevinTamir/ur5_ws.git .
```

If you already cloned without `--recurse-submodules`, initialize submodules manually:

```bash
git submodule update --init --recursive
```

### Install dependencies

```bash
# Install the Universal Robots driver for ROS 2 Jazzy
sudo apt update
sudo apt install ros-jazzy-ur

# Install all ROS package dependencies
cd <PATH>/ur5_ws
rosdep install --from-paths src --ignore-src -r -y
```

> **Note:** If this is your first time using rosdep:
> ```bash
> sudo rosdep init
> rosdep update
> ```

### Build

```bash
cd <PATH>/ur5_ws
colcon build
source install/setup.bash
```

> To auto-source in every terminal:
> ```bash
> echo "source <PATH>/ur5_ws/install/setup.bash" >> ~/.bashrc
> ```

## Launch

### UR5 on table - Gazebo simulation with MoveIt

```bash
ros2 launch ur5_volcani_description ur5_volcani_sim_moveit.launch.py
```

### UR5 on table - Gazebo simulation only (no MoveIt)

```bash
ros2 launch ur5_volcani_description ur5_volcani_sim_control.launch.py
```

### With a specific world

```bash
# Lab environment
ros2 launch ur5_volcani_description ur5_volcani_sim_moveit.launch.py world_name:=lab

# Field environment
ros2 launch ur5_volcani_description ur5_volcani_sim_moveit.launch.py world_name:=feild
```

### Original UR5 simulation (standalone, no table)

```bash
ros2 launch ur_simulation_gz ur_sim_moveit.launch.py
```

## Project Structure

```
ur5_ws/
  src/
    ur_simulation_gz/          # Git submodule - UR Gazebo simulation package
    ur5_volcani_description/   # UR5 on volcaniarm table - URDF, launch, worlds
      urdf/                    # Combined URDF (table + UR5)
      launch/                  # Launch files for simulation
      meshes/                  # Volcaniarm table meshes
      worlds/                  # Gazebo world files (empty, lab, feild)
      models/                  # Gazebo models (plants, trees, etc.)
      config/                  # Controller configuration
```
