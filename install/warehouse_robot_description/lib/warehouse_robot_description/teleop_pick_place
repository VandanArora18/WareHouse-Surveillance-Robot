#!/usr/bin/env python3
"""
teleop_pick_place.py  —  Keyboard teleop + pick-and-place for warehouse robot
ROS 2 Humble + Ignition Fortress

Controls:
  W / Arrow UP    → forward
  S / Arrow DOWN  → backward
  A / Arrow LEFT  → turn left
  D / Arrow RIGHT → turn right
  SPACE           → PICK (when near a box) / PLACE (when holding)
  R               → rotate arm (spins robot slowly in place)
  Q / ESC         → quit

Note: SPACE pick works by teleporting the nearest box model to the
      gripper tip position every 50 ms. This is the standard approach
      for fixed-gripper robots in Ignition simulations.
"""

import sys, math, select, tty, termios
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
from ros_gz_interfaces.srv import SetEntityPose
from ros_gz_interfaces.msg import Entity
from geometry_msgs.msg import Pose, Point, Quaternion
import tf2_ros

HELP = """
╔══════════════════════════════════════════════════════╗
║     WAREHOUSE ROBOT  —  Keyboard Teleop              ║
╠══════════════════════════════════════════════════════╣
║  W / ↑   Forward          S / ↓   Backward          ║
║  A / ←   Turn Left        D / →   Turn Right         ║
║  SPACE   Pick box (near) / Place box (holding)       ║
║  R       Rotate arm (robot spins in place)           ║
║  Q / ESC Quit                                        ║
╚══════════════════════════════════════════════════════╝
"""

LIN   = 0.4   # m/s linear speed
ANG   = 0.8   # rad/s turn speed
ROT   = 0.3   # rad/s arm-rotation speed
# Gripper offset from base_link origin (tune after visual check in RViz)
GRIP_X = 0.50   # metres in front of robot
GRIP_Z = 0.55   # metres above ground

# All pick-able box names defined in the SDF
BOX_NAMES = ['box_A1_1','box_A1_2','box_A1_3','box_A2_1','box_A2_2']


def get_key(timeout=0.05):
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        r, _, _ = select.select([sys.stdin], [], [], timeout)
        if r:
            ch = sys.stdin.read(1)
            if ch == '\x1b':
                ch2 = sys.stdin.read(1) if select.select([sys.stdin],[],[],0.05)[0] else ''
                ch3 = sys.stdin.read(1) if select.select([sys.stdin],[],[],0.05)[0] else ''
                return ch + ch2 + ch3
            return ch
        return ''
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)


class TeleopNode(Node):
    def __init__(self):
        super().__init__('teleop_pick_place')
        self.pub = self.create_publisher(Twist, '/cmd_vel', 10)
        self.tf  = tf2_ros.Buffer()
        tf2_ros.TransformListener(self.tf, self)
        self.cli = self.create_client(SetEntityPose,
                                      '/world/warehouse_factory/set_pose')
        self.held = None
        self.create_timer(0.05, self._attach_update)
        self.get_logger().info('Waiting for Ignition set_pose service...')
        ok = self.cli.wait_for_service(timeout_sec=8.0)
        if not ok:
            self.get_logger().warn('set_pose service not found — pick/place disabled')
        self.get_logger().info('Ready! ' + HELP)

    def _vel(self, lin, ang):
        m = Twist(); m.linear.x = lin; m.angular.z = ang
        self.pub.publish(m)

    def _robot_pose(self):
        try:
            t = self.tf.lookup_transform('world','base_link',
                rclpy.time.Time(), rclpy.duration.Duration(seconds=0.2))
            tr = t.transform.translation
            ro = t.transform.rotation
            yaw = math.atan2(2*(ro.w*ro.z+ro.x*ro.y),
                             1-2*(ro.y*ro.y+ro.z*ro.z))
            return tr.x, tr.y, tr.z, yaw
        except Exception:
            return None

    def _gripper_pose(self):
        p = self._robot_pose()
        if not p: return None
        rx,ry,rz,yaw = p
        return (rx + GRIP_X*math.cos(yaw),
                ry + GRIP_X*math.sin(yaw),
                GRIP_Z, yaw)

    def _set_pose(self, name, x, y, z, yaw=0.0):
        if not self.cli.service_is_ready(): return
        req = SetEntityPose.Request()
        req.entity = Entity(); req.entity.name = name
        req.entity.type = Entity.MODEL
        cy,sy = math.cos(yaw/2), math.sin(yaw/2)
        req.pose = Pose(position=Point(x=x,y=y,z=z),
                        orientation=Quaternion(x=0.0,y=0.0,z=sy,w=cy))
        self.cli.call_async(req)

    def _attach_update(self):
        if not self.held: return
        gp = self._gripper_pose()
        if gp: self._set_pose(self.held, *gp)

    def _pick(self):
        gp = self._gripper_pose()
        if not gp:
            print('Cannot get robot pose — is sim running?'); return
        gx,gy,gz,_ = gp
        best,dist = None, 1e9
        for name in BOX_NAMES:
            if name == self.held: continue
            try:
                t = self.tf.lookup_transform('world', name+'/link',
                    rclpy.time.Time(), rclpy.duration.Duration(seconds=0.1))
                bx = t.transform.translation.x
                by = t.transform.translation.y
                bz = t.transform.translation.z
                d = math.sqrt((gx-bx)**2+(gy-by)**2+(gz-bz)**2)
                if d < dist: dist=d; best=name
            except Exception:
                pass
        if best and dist < 0.8:
            self.held = best
            print(f'✓ PICKED {best}  (dist={dist:.2f} m)')
        else:
            print(f'✗ No box in range (closest {dist:.2f} m). Drive closer.')

    def _place(self):
        if not self.held: print('Not holding a box.'); return
        gp = self._gripper_pose()
        if gp:
            gx,gy,gz,yaw = gp
            self._set_pose(self.held, gx, gy, gz-0.06, yaw)
        print(f'✓ PLACED {self.held}')
        self.held = None

    def run(self):
        print(HELP)
        try:
            while rclpy.ok():
                rclpy.spin_once(self, timeout_sec=0.0)
                k = get_key()
                if   k in ('q','Q','\x1b'): break
                elif k in ('w','\x1b[A'): self._vel( LIN, 0.0)
                elif k in ('s','\x1b[B'): self._vel(-LIN, 0.0)
                elif k in ('a','\x1b[D'): self._vel(0.0,  ANG)
                elif k in ('d','\x1b[C'): self._vel(0.0, -ANG)
                elif k in ('r','R'):       self._vel(0.0,  ROT)
                elif k == ' ':
                    self._vel(0.0, 0.0)
                    if self.held: self._place()
                    else:         self._pick()
                elif k: self._vel(0.0, 0.0)
        except KeyboardInterrupt:
            pass
        finally:
            self._vel(0.0, 0.0)
            print('Stopped.')


def main(args=None):
    rclpy.init(args=args)
    n = TeleopNode(); n.run()
    n.destroy_node(); rclpy.shutdown()

if __name__ == '__main__': main()
