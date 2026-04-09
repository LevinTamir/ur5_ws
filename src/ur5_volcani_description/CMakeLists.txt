cmake_minimum_required(VERSION 3.8)
project(ur5_volcani_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY urdf launch config meshes worlds models rviz
  DESTINATION share/${PROJECT_NAME}
)

ament_package()
