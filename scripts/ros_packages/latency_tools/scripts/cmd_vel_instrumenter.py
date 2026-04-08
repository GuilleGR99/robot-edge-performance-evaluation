#!/usr/bin/env python2

import rospy
from geometry_msgs.msg import Twist, TwistStamped

class CmdVelInstrumenter:
    def __init__(self):
        rospy.init_node('cmd_vel_instrumenter')

        self.sub = rospy.Subscriber(
            '/robot/move_base/cmd_vel',
            Twist,
            self.callback
        )

        self.pub = rospy.Publisher(
            '/robot/move_base/cmd_vel_stamped',
            TwistStamped,
            queue_size=10
        )

    def callback(self, msg):
        stamped_msg = TwistStamped()
        stamped_msg.header.stamp = rospy.Time.now()
        stamped_msg.header.frame_id = "base_link"
        stamped_msg.twist = msg

        self.pub.publish(stamped_msg)

if __name__ == '__main__':
    CmdVelInstrumenter()
    rospy.spin()
