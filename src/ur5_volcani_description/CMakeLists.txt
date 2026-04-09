cmake_minimum_required(VERSION 3.8)
project(ur5_volcani_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf launch config meshes worlds models rviz srdf
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS scripts/publish_collision_objects.py
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
