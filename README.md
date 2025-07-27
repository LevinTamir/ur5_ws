## 🔧 Setup Instructions

### Create the Workspace and Clone the Repository

```bash
mkdir -p ~/ros2_workspaces/ur5_ws/src
cd ~/ros2_workspaces/ur5_ws
git clone git@github.com:LevinTamir/ur5_ws.git .
```

### Install Dependencies

Install the Universal Robots driver for ROS 2 Jazzy:

```bash
sudo apt update
sudo apt install ros-jazzy-ur
```

Install all ROS package dependencies using rosdep:

```bash
cd <PATH>/ur5_ws
rosdep install --from-paths src --ignore-src -r -y
```

>**Note:** If this is your first time using rosdep, you may need to initialize it first:
>
>```bash
>sudo rosdep init
>rosdep update
>```

### Build the Workspace

After installing all dependencies, build the workspace using `colcon`:

```bash
cd <PATH>/ur5_ws
colcon build
source install/setup.bash
```

> **Note:** to automatically source the workspace in every new terminal, add this line to your `~/.bashrc`:
>
>```bash
>echo "source <PATH>/ur5_ws/install/setup.bash" >> ~/.bashrc
>```

### Launch the Simulation

To verify the setup, launch the UR5 simulation with Gazebo and MoveIt:

```bash
ros2 launch ur_simulation_gz ur_sim_moveit.launch.py
```
