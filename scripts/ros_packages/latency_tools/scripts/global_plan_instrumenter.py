#!/usr/bin/env python2

import rospy
from nav_msgs.msg import Path

class GlobalPlanInstrumenter:
    def __init__(self):
        rospy.init_node('global_plan_instrumenter')

        # Esperar tiempo simulado válido
        while rospy.Time.now().to_sec() == 0:
            rospy.loginfo("Esperando tiempo simulado...")
            rospy.sleep(0.1)

        self.pub = rospy.Publisher(
            '/robot/move_base/GlobalPlanner/plan_stamped',
            Path,
            queue_size=10
        )

        self.sub = rospy.Subscriber(
            '/robot/move_base/GlobalPlanner/plan',
            Path,
            self.callback,
            queue_size=10
        )

    def callback(self, msg):
        stamped = Path()
        stamped.header.stamp = rospy.Time.now()
        stamped.header.frame_id = msg.header.frame_id
        stamped.poses = msg.poses

        self.pub.publish(stamped)

if __name__ == '__main__':
    GlobalPlanInstrumenter()
    rospy.spin()