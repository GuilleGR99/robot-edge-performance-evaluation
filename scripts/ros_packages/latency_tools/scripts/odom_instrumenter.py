#!/usr/bin/env python2

import rospy
from nav_msgs.msg import Odometry

class OdomInstrumenter:
    def __init__(self):
        rospy.init_node('odom_instrumenter')

        self.pub = rospy.Publisher(
            '/robot/robotnik_base_control/odom_stamped',
            Odometry,
            queue_size=10
        )

        self.sub = rospy.Subscriber(
            '/robot/robotnik_base_control/odom',
            Odometry,
            self.callback,
            queue_size=10
        )

    def callback(self, msg):
        msg.header.stamp = rospy.Time.now()
        self.pub.publish(msg)

if __name__ == '__main__':
    OdomInstrumenter()
    rospy.spin()