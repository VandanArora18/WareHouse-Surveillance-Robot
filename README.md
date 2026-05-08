<p align="center">
  <h1 align="center">🚨 Autonomous Warehouse Surveillance Robot</h1>

  <p align="center">
    <strong>ROS 2 Humble Based Mobile Robot for Warehouse Mapping and Monitoring</strong>
  </p>

  <p align="center">
    <a href="#-overview">Overview</a> •
    <a href="#-system-capabilities">Capabilities</a> •
    <a href="#-visual-gallery">Gallery</a> •
    <a href="#-technology-stack">Tech Stack</a> •
    <a href="#-working-methodology">Methodology</a> •
    <a href="#-getting-started">Installation & Usage</a> •
    <a href="#-future-directions">Future Scope</a>
  </p>
</p>

---

## 📘 Overview

The **Warehouse Surveillance Robot** is a comprehensive robotics simulation project built using **ROS 2 Humble**. It features a custom-designed differential drive robot equipped with a robotic arm and camera, designed to navigate, map, and monitor a simulated warehouse environment.

Leveraging Ignition Gazebo for physics simulation and SLAM Toolbox for real-time mapping, this system serves as a foundational architecture for automated logistics surveillance, inventory monitoring, and industrial security.

---

## ✨ System Capabilities

| ✅ Supported Functions | 🚫 Outside Scope |
|---|---|
| Real-time SLAM (Simultaneous Localization and Mapping) | Physical hardware deployment (Simulation only) |
| Keyboard teleoperation (Base & Arm) | Fully autonomous path planning (Nav2) |
| Sensor simulation (LIDAR, IMU, Camera) | Real-time AI object detection |
| Custom 3D environment interaction | Dynamic moving obstacles |
| RViz2 real-time visualization | Fleet management / Multi-robot coordination |
| URDF/Xacro dynamic modeling | Automated battery/docking management |

---

## 📸 Visual Gallery

*(Replace the placeholder links inside the brackets `( )` with your actual image URLs)*

### 1. CAD Design & Modelling
<p align="center">
  <img src="[INSERT_CAD_PHOTO_1_URL_HERE]" alt="CAD Design 1" width="45%">
  <img src="[INSERT_CAD_PHOTO_2_URL_HERE]" alt="CAD Design 2" width="45%">
</p>

### 2. Simulated Environment & Mapping
<p align="center">
  <img src="[INSERT_WAREHOUSE_WORLD_PHOTO_URL_HERE]" alt="Gazebo Warehouse World" width="45%">
  <img src="[INSERT_SLAM_RVIZ_PHOTO_URL_HERE]" alt="RViz2 SLAM Mapping" width="45%">
</p>

---

## 🛠 Technology Stack

| Component | Tools Used |
|---|---|
| Framework | ROS 2 (Humble) |
| Programming | Python (`rclpy`) |
| CAD & Modelling | PTC Creo / SolidWorks, URDF, Xacro |
| Simulation | Ignition Gazebo |
| Visualization | RViz2 |
| Mapping | SLAM Toolbox |
| Communication | `ros_gz_bridge` |

---

## 🔬 Working Methodology

<p align="center">
  <!-- UPLOAD YOUR METHODOLOGY FLOWCHART PHOTO HERE -->
  <img src="[INSERT_METHODOLOGY_FLOWCHART_URL_HERE]" alt="System Architecture Flowchart" width="90%">
</p>

The system operates on a 10-step architectural pipeline, seamlessly translating CAD models into a functional ROS 2 simulation:

1. **CAD Design (PTC Creo):** Robot assembly (base, wheels, arm, camera) is designed, physical properties (mass, inertia) are defined, and exported as STL mesh files.
2. **URDF / Xacro Modelling:** The robot description is built defining links, joints, and simulation plugins (DiffDrive, JointPositionController), alongside sensor attachments.
3. **ROS 2 Package Structure:** Standard ROS 2 workspace generation containing `urdf`, `meshes`, `launch`, `worlds`, `config`, and mandatory `CMakeLists.txt`/`package.xml` files.
4. **Launch File Configuration:** `gazebo.launch.py` triggers Ignition Gazebo, spawns the robot, and starts essential nodes (`robot_state_publisher`, `ros_gz_bridge`).
5. **Gazebo Simulation Environment:** The custom warehouse world is loaded, handling robot placement, physics engines, and sensor activation.
6. **Sensor Integration (Critical):** `ros_gz_bridge` translates Gazebo sensor data (LIDAR, IMU, Camera) into standard ROS 2 topics (`/scan`, `/imu`, `/camera/image`).
7. **SLAM Implementation (Core Logic):** The SLAM Toolbox utilizes `/scan` and `/odom` data for scan matching and pose graph calculation, outputting a real-time occupancy grid (`/map`) and localization (`/tf tree`).
8. **Teleoperation System:** A custom Python node (`teleop.py`) takes WASD keyboard inputs and translates them into `/cmd_vel` commands for the chassis and joint topics for the arm/camera.
9. **RViz2 Visualization:** Live monitoring setup displaying the map, laser scans, TF tree, and camera feed.
10. **Complete System Workflow:** The synchronized execution of the above nodes allowing simultaneous exploration, mapping, and surveillance.

---

## 🚀 Getting Started (Installation & Usage)

Follow these steps to run the warehouse surveillance robot on your local machine.

### Prerequisites
* Ubuntu 22.04 LTS
* ROS 2 Humble installed
* Ignition Gazebo (Fortress) installed

### Step 1: Clone and Build the Workspace
Open your terminal and execute the following commands:

```bash
# Create a ROS 2 workspace
mkdir -p ~/warehouse_ws/src
cd ~/warehouse_ws/src

# Clone the repository
git clone [https://github.com/VandanArora18/WareHouse-Surveillance-Robot.git](https://github.com/VandanArora18/WareHouse-Surveillance-Robot.git)

# Navigate to workspace root and install dependencies
cd ~/warehouse_ws
rosdep install -i --from-path src --rosdistro humble -y

# Build the packages
colcon build --symlink-install

# Source the workspace
source install/setup.bash
