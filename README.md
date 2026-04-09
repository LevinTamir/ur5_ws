# UR5 Volcani Workspace

A ROS 2 Jazzy workspace for simulating a UR5e robotic arm mounted upside-down on the Volcaniarm mobile table, with an RGBD camera for weed detection in agricultural environments.

## Quick Start

```bash
# 1. Clone
mkdir -p ~/ur5_ws && cd ~/ur5_ws
git clone --recurse-submodules https://github.com/LevinTamir/ur5_ws.git .

# 2. Install dependencies
sudo apt update && sudo apt install ros-jazzy-ur
rosdep install --from-paths src --ignore-src -r -y

# 3. Build
colcon build && source install/setup.bash

# 4. Launch
ros2 launch ur5_volcani_description ur5_volcani_sim_moveit.launch.py
```

> If you cloned without `--recurse-submodules`, run `git submodule update --init --recursive`

> To auto-source the workspace, add to `~/.bashrc`:
> ```bash
> source ~/ur5_ws/install/setup.bash
> ```

## Launching

### Simulation + MoveIt (default: lab world)

```bash
ros2 launch ur5_volcani_description ur5_volcani_sim_moveit.launch.py
```

### Simulation only (no MoveIt)

```bash
ros2 launch ur5_volcani_description ur5_volcani_sim_control.launch.py
```

### Choose a world

```bash
ros2 launch ur5_volcani_description ur5_volcani_sim_moveit.launch.py world_name:=lab    # default
ros2 launch ur5_volcani_description ur5_volcani_sim_moveit.launch.py world_name:=feild
ros2 launch ur5_volcani_description ur5_volcani_sim_moveit.launch.py world_name:=empty
```

### Weed detection

In a separate terminal (while the simulation is running):

```bash
ros2 run weed_detector weed_detection_node
```

Subscribes to the RGBD camera topics and publishes:
- `/weed_position_raw` (`geometry_msgs/PointStamped`) — 3D weed location
- `/weed_marker` (`visualization_msgs/Marker`) — RViz visualization marker

### Send the arm to a detected position

```bash
ros2 action send_goal /move_action moveit_msgs/action/MoveGroup "{
  request: {
    group_name: 'ur_manipulator',
    goal_constraints: [{
      position_constraints: [{
        header: {frame_id: 'base_link'},
        link_name: 'tool0',
        constraint_region: {
          primitives: [{type: 2, dimensions: [0.01]}],
          primitive_poses: [{position: {x: 0.124, y: 0.188, z: 0.733}, orientation: {w: 1.0}}]
        },
        weight: 1.0
      }]
    }]
  }
}"
```

## Project Structure

```
ur5_ws/
├── src/
│   ├── ur_simulation_gz/              # [submodule] UR Gazebo simulation package
│   │
│   ├── ur5_volcani_description/       # Main package: UR5 on volcaniarm table
│   │   ├── urdf/                      #   URDF/Xacro (table + UR5 + camera)
│   │   ├── srdf/                      #   MoveIt semantic description
│   │   ├── launch/                    #   Launch files (sim, MoveIt, etc.)
│   │   ├── config/                    #   ros2_control controller config
│   │   ├── rviz/                      #   RViz config (MoveIt + camera views)
│   │   ├── meshes/                    #   Table, legs, wheels, camera STLs
│   │   ├── worlds/                    #   Gazebo worlds (empty, lab, field)
│   │   ├── models/                    #   Gazebo models (plants, trees, terrain)
│   │   └── scripts/                   #   Collision object publisher
│   │
│   └── weed_detector/                 # Weed detection via HSV + depth camera
│       └── weed_detector_py/          #   Python node (subscribes RGBD, publishes 3D position)
```
