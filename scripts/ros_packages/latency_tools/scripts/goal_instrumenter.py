#!/usr/bin/env python2

import rospy
from geometry_msgs.msg import PoseStamped

class GoalInstrumenter:
    def __init__(self):
        rospy.init_node('goal_instrumenter')

        self.pub = rospy.Publisher(
            '/robot/move_base_simple/goal_stamped',
            PoseStamped,
            queue_size=10
        )

        self.sub = rospy.Subscriber(
            '/robot/move_base_simple/goal',
            PoseStamped,
            self.callback,
            queue_size=10
        )

    def callback(self, msg):
        # Sobrescribir timestamp
        msg.header.stamp = rospy.Time.now()

        self.pub.publish(msg)

if __name__ == '__main__':
    GoalInstrumenter()
    rospy.spin()