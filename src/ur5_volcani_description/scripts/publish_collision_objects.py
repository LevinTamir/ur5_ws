#!/usr/bin/env python3
"""Publish table mesh and floor as MoveIt collision objects."""

import struct
import os

import rclpy
from rclpy.node import Node
from ament_index_python.packages import get_package_share_directory
from moveit_msgs.msg import PlanningScene, CollisionObject
from shape_msgs.msg import SolidPrimitive, Mesh, MeshTriangle
from geometry_msgs.msg import Pose, Point
from math import sin, cos, pi


def load_stl_binary(filepath):
    """Parse a binary STL file and return vertices and triangles."""
    vertices = []
    triangles = []
    vertex_map = {}

    with open(filepath, "rb") as f:
        f.read(80)  # skip header
        num_triangles = struct.unpack("<I", f.read(4))[0]

        for _ in range(num_triangles):
            f.read(12)  # skip normal
            tri_indices = []
            for _ in range(3):
                vx, vy, vz = struct.unpack("<fff", f.read(12))
                key = (round(vx, 6), round(vy, 6), round(vz, 6))
                if key not in vertex_map:
                    vertex_map[key] = len(vertices)
                    vertices.append(key)
                tri_indices.append(vertex_map[key])
            triangles.append(tri_indices)
            f.read(2)  # skip attribute byte count

    return vertices, triangles


class CollisionPublisher(Node):
    def __init__(self):
        super().__init__("collision_object_publisher")
        self.publisher = self.create_publisher(PlanningScene, "/planning_scene", 10)
        self.timer = self.create_timer(2.0, self.publish_scene)
        self.published = False

    def publish_scene(self):
        if self.published:
            return

        scene = PlanningScene()
        scene.is_diff = True

        # --- Floor ---
        floor = CollisionObject()
        floor.header.frame_id = "world"
        floor.header.stamp = self.get_clock().now().to_msg()
        floor.id = "floor"
        floor.operation = CollisionObject.ADD

        floor_box = SolidPrimitive()
        floor_box.type = SolidPrimitive.BOX
        floor_box.dimensions = [3.0, 3.0, 0.01]

        floor_pose = Pose()
        floor_pose.position.z = -0.005
        floor_pose.orientation.w = 1.0

        floor.primitives.append(floor_box)
        floor.primitive_poses.append(floor_pose)
        scene.world.collision_objects.append(floor)

        # --- Table top (from STL mesh) ---
        pkg_dir = get_package_share_directory("ur5_volcani_description")
        stl_path = os.path.join(pkg_dir, "meshes", "base_link.STL")

        if os.path.exists(stl_path):
            vertices, triangles = load_stl_binary(stl_path)

            table = CollisionObject()
            table.header.frame_id = "world"
            table.header.stamp = self.get_clock().now().to_msg()
            table.id = "table_top"
            table.operation = CollisionObject.ADD

            mesh = Mesh()
            for vx, vy, vz in vertices:
                mesh.vertices.append(Point(x=float(vx), y=float(vy), z=float(vz)))
            for tri in triangles:
                mt = MeshTriangle()
                mt.vertex_indices = [tri[0], tri[1], tri[2]]
                mesh.triangles.append(mt)

            # table_top_link is at xyz=(0,0,0.98) rpy=(0,0,pi) from world
            table_pose = Pose()
            table_pose.position.x = 0.0
            table_pose.position.y = 0.0
            table_pose.position.z = 0.98
            # Quaternion for yaw=pi: (0, 0, sin(pi/2), cos(pi/2)) = (0, 0, 1, 0)
            table_pose.orientation.x = 0.0
            table_pose.orientation.y = 0.0
            table_pose.orientation.z = 1.0
            table_pose.orientation.w = 0.0

            table.meshes.append(mesh)
            table.mesh_poses.append(table_pose)
            scene.world.collision_objects.append(table)
            self.get_logger().info(
                f"Loaded table mesh: {len(vertices)} vertices, {len(triangles)} triangles"
            )
        else:
            self.get_logger().warn(f"Table mesh not found at {stl_path}, skipping")

        self.publisher.publish(scene)
        self.get_logger().info("Published collision objects (floor + table mesh)")
        self.published = True


def main():
    rclpy.init()
    node = CollisionPublisher()
    rclpy.spin(node)
    rclpy.shutdown()


if __name__ == "__main__":
    main()
