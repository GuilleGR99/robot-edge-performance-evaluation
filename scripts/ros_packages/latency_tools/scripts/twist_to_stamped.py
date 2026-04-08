#!/usr/bin/env python2

import rospy
from geometry_msgs.msg import Twist, TwistStamped

class TwistToStamped:
    def __init__(self):

        rospy.init_node('twist_to_stamped')

        # Esperar a tiempo simulado v�lido
        while rospy.Time.now().to_sec() == 0:
            rospy.loginfo("Esperando tiempo simulado...")
            rospy.sleep(0.1)

        self.pub = rospy.Publisher(
            '/robot/move_base/cmd_vel_stamped',
            TwistStamped,
            queue_size=10
)

        # Subscriber
        self.sub = rospy.Subscriber(
            '/robot/move_base/cmd_vel',
            Twist,
            self.callback,
            queue_size=10
        )

    def callback(self, msg):
        rospy.loginfo("Recibiendo cmd_vel")

        stamped = TwistStamped()
        stamped.header.stamp = rospy.Time.now()
        stamped.header.frame_id = "base_link"
        stamped.twist = msg

        self.pub.publish(stamped)

if __name__ == '__main__':
    TwistToStamped()
    rospy.spin()