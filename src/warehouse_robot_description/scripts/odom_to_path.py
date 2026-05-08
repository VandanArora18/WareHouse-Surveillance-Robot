#!/usr/bin/env python3
"""
Converts /odom (nav_msgs/Odometry) → /path (nav_msgs/Path)
so RViz Path display can show the robot's trajectory.
"""
import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry, Path
from geometry_msgs.msg import PoseStamped


class OdomToPath(Node):
    def __init__(self):
        super().__init__('odom_to_path')
        self.path = Path()
        self.path.header.frame_id = 'odom'

        self.sub = self.create_subscription(
            Odometry, '/odom', self.odom_cb, 10)
        self.pub = self.create_publisher(Path, '/path', 10)

    def odom_cb(self, msg: Odometry):
        pose = PoseStamped()
        pose.header = msg.header
        pose.pose   = msg.pose.pose

        self.path.header.stamp = msg.header.stamp
        self.path.poses.append(pose)

        # Keep last 500 poses to avoid memory growth
        if len(self.path.poses) > 500:
            self.path.poses.pop(0)

        self.pub.publish(self.path)


def main():
    rclpy.init()
    rclpy.spin(OdomToPath())
    rclpy.shutdown()

if __name__ == '__main__':
    main()