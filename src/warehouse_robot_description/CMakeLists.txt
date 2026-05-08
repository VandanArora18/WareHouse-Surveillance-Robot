cmake_minimum_required(VERSION 3.5)
project(warehouse_robot_description)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Install Python scripts as executables
install(PROGRAMS
  scripts/teleop_pick_place.py
  DESTINATION lib/${PROJECT_NAME}
  RENAME teleop_pick_place
)
install(PROGRAMS
  scripts/odom_to_path.py
  DESTINATION lib/${PROJECT_NAME}
)
# Install all resource directories
install(DIRECTORY
  urdf
  meshes
  rviz
  config
  launch
  worlds
  scripts
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
