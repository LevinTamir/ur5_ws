# ur5_ws

A ROS 2 Jazzy workspace for the Agricultural Robotics Lab (ARL), focused on simulating and controlling a UR5 robotic arm using MoveIt and Gazebo.

---

## 🔧 Setup Instructions

Follow these 5 steps to install and run the workspace:

---

### 1. Create the Workspace and Clone the Repository

```bash
mkdir -p ~/ros2_workspaces/ur5_ws/src
cd ~/ros2_workspaces/ur5_ws/src
git clone https://github.com/LevinTamir/ur5_ws.git .

### 2. Install Dependencies

Install the Universal Robots driver for ROS 2 Jazzy:

```bash
sudo apt update
sudo apt install ros-jazzy-ur

### 3. Build the Workspace

After installing all dependencies, build the workspace using `colcon`:

```bash
cd ~/ros2_workspaces/ur5_ws
colcon build

### 4. Source the Workspace

Before using any ROS 2 packages from this workspace, you need to source its environment.

For the current terminal session:

```bash
source install/setup.bash

### 5. Launch the Simulation

To verify the setup, launch the UR5 simulation with Gazebo and MoveIt:

```bash
ros2 launch ur_simulation_gz ur_sim_moveit.launch.py


