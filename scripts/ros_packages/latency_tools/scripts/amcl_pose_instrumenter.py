#!/usr/bin/env python2

import rospy
from geometry_msgs.msg import PoseWithCovarianceStamped

class AMCLPoseInstrumenter:
    def __init__(self):
        rospy.init_node('amcl_pose_instrumenter')

        self.pub = rospy.Publisher(
            '/robot/amcl_pose_stamped',
            PoseWithCovarianceStamped,
            queue_size=10
        )

        self.sub = rospy.Subscriber(
            '/robot/amcl_pose',
            PoseWithCovarianceStamped,
            self.callback,
            queue_size=10
        )

    def callback(self, msg):
        # Sobrescribir timestamp
        msg.header.stamp = rospy.Time.now()

        self.pub.publish(msg)

if __name__ == '__main__':
    AMCLPoseInstrumenter()
    rospy.spin()