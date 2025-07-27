## 🔧 Setup Instructions

Create the Workspace and Clone the Repository

```bash
mkdir -p <PATH>/ur5_ws
cd <PATH>/ur5_ws
git clone https://github.com/LevinTamir/ur5_ws.git .
```

Clone the required submodules manually:

```bash
cd <PATH>/ur5_ws/src
git clone https://github.com/LevinTamir/Universal_Robots_ROS2_GZ_Simulation.git ur_simulation_gz
```

Initialize and update all submodules:

```bash
cd <PATH>/ur5_ws/src
git submodule update --init --recursive
```

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

> **Note:** If this is your first time using rosdep, you may need to initialize it first:
> ```bash
> sudo rosdep init
> rosdep update
> ```

After installing all dependencies, build the workspace using `colcon`:

```bash
cd <PATH>/ur5_ws
colcon build
source install/setup.bash
```

> **Note:** To automatically source the workspace in every new terminal, add this line to your `~/.bashrc`:
> ```bash
> echo "source <PATH>/ur5_ws/install/setup.bash" >> ~/.bashrc
> ```

To launch the UR5 simulation with Gazebo and MoveIt:

```bash
ros2 launch ur_simulation_gz ur_sim_moveit.launch.py
```
