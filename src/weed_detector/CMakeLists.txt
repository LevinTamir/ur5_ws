cmake_minimum_required(VERSION 3.8)
project(weed_detector)

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)

# Install Python package
ament_python_install_package(weed_detector_py)

# Install Python executables
install(PROGRAMS
  src/weed_detection_node
  DESTINATION lib/${PROJECT_NAME}
)

ament_package()
