# warehouse_robot_description

ROS 2 Humble + Ignition Gazebo Fortress (v6) description package for the
warehouse pick-and-place robot.

---

## Package layout

```
warehouse_robot_description/
├── CMakeLists.txt
├── package.xml
├── urdf/
│   └── warehouse_robot.urdf.xacro   ← main robot model
├── meshes/
│   └── base/
│       └── base.stl                 ← chassis mesh (Z-up, mm units)
├── launch/
│   ├── display.launch.py            ← RViz2 visualisation (no Gazebo)
│   └── gazebo.launch.py             ← Ignition Fortress simulation
├── config/
│   └── ros_gz_bridge.yaml           ← topic bridge config
├── rviz/
│   └── display.rviz                 ← RViz2 config
└── worlds/
    └── warehouse.sdf                ← Ignition world (20×20 m warehouse)
```

---

## URDF geometry summary

| Property | Value | Source |
|---|---|---|
| STL units | mm | measured from mesh |
| URDF scale | `0.001 0.001 0.001` | mm → m |
| Chassis width (X) | 0.600 m | |
| Chassis depth (Y) | 0.795 m | |
| Chassis height (Z) | 0.891 m | |
| Base mass | 5.0 kg | assumed aluminium frame |
| Wheel radius | 0.100 m | placeholder – adjust |
| Wheel separation | 0.500 m | (2 × wheel_y) |
| Caster radius | 0.050 m | rear passive caster |

---

## Prerequisites (WSL2 Ubuntu 22.04)

```bash
# ROS 2 Humble base
sudo apt install ros-humble-desktop

# Ignition Fortress + bridge
sudo apt install ros-humble-ros-gz
# which installs: ros-humble-ros-gz-sim ros-humble-ros-gz-bridge

# URDF / launch tools
sudo apt install \
  ros-humble-xacro \
  ros-humble-robot-state-publisher \
  ros-humble-joint-state-publisher-gui \
  ros-humble-rviz2
```

### WSL2 GPU note

If GPU passthrough is not available:
```bash
export LIBGL_ALWAYS_SOFTWARE=1   # software mesa renderer
export OGRE_RTT_MODE=Copy        # fixes Ogre2 FBO issues on mesa
```
Add both lines to `~/.bashrc` for persistence.

---

## Build

```bash
cd ~/ros2_ws
# drop the package here:
# ~/ros2_ws/src/warehouse_robot_description/

colcon build --packages-select warehouse_robot_description
source install/setup.bash
```

---

## Run

### 1 – RViz2 display (no Gazebo)

```bash
ros2 launch warehouse_robot_description display.launch.py
```

Use the **Joint State Publisher GUI** sliders to rotate the drive wheels.

### 2 – Ignition Gazebo Fortress

```bash
ros2 launch warehouse_robot_description gazebo.launch.py
# With RViz2 open alongside:
ros2 launch warehouse_robot_description gazebo.launch.py open_rviz:=true
# Headless (server only):
ros2 launch warehouse_robot_description gazebo.launch.py gz_headless:=true
```

### 3 – Drive the robot

```bash
# Keyboard teleoperation (install if needed: sudo apt install ros-humble-teleop-twist-keyboard)
ros2 run teleop_twist_keyboard teleop_twist_keyboard --ros-args -r cmd_vel:=/cmd_vel
```

---

## Customisation

### Swap in real wheel meshes
Replace the cylinder geometry in the `drive_wheel` macro inside
`urdf/warehouse_robot.urdf.xacro` with:
```xml
<mesh filename="package://warehouse_robot_description/meshes/wheel/wheel.stl"
      scale="0.001 0.001 0.001"/>
```

### Adjust wheel base / track width
Edit `wheel_y` (half-track) and `wheel_x` properties at the top of the xacro.
The `wheel_separation` in the diff-drive plugin is derived automatically as `2 * wheel_y`.

### Add sensors (LiDAR, camera)
Add new `<link>` + `<joint>` pairs after the caster block, then add the
corresponding Ignition sensor plugin inside a `<gazebo reference="...">` tag.

---

## Coordinate frames

```
odom (world)
 └── base_footprint  (ground plane, Z=0)
      └── base_link  (chassis bottom, Z = +0.325 m above footprint)
           ├── left_wheel_link   (continuous joint, axis Y)
           ├── right_wheel_link  (continuous joint, axis Y)
           └── caster_rear_link  (fixed joint, passive sphere)
```
