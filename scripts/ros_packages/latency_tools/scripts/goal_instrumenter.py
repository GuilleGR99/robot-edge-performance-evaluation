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
        stamped = PoseStamped()
        stamped.header.stamp = rospy.Time.now()
        stamped.header.frame_id = msg.header.frame_id
        stamped.pose = msg.pose

        self.pub.publish(stamped)

if __name__ == '__main__':
    GoalInstrumenter()
    rospy.spin()