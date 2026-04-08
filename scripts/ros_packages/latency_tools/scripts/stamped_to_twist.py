#!/usr/bin/env python2

import rospy
from geometry_msgs.msg import Twist, TwistStamped

class StampedToTwist:
    def __init__(self):
        rospy.init_node('stamped_to_twist')

        self.sub = rospy.Subscriber(
            '/robot/move_base/cmd_vel_stamped',
            TwistStamped,
            self.callback,
            queue_size=10
        )

        self.pub = rospy.Publisher(
            '/robot/move_base/cmd_vel_instrumented',
            Twist,
            queue_size=10
        )

    def callback(self, msg):
        self.pub.publish(msg.twist)

if __name__ == '__main__':
    StampedToTwist()
    rospy.spin()
