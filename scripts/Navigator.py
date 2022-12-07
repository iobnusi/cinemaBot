# TurtleBot must have minimal.launch & amcl_demo.launch
# running prior to starting this script
# For simulation: launch gazebo world & amcl_demo prior to run this script

import rospy
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
import actionlib
from actionlib_msgs.msg import *
from geometry_msgs.msg import Pose, Point, Quaternion


class Navigator():
    def __init__(self):

        self.goal_sent = False
        rospy.Subscriber("Guest_Info", Pose, self.callback)

        # What to do if shut down (e.g. Ctrl-C or failure)
        rospy.on_shutdown(self.shutdown)

        # Tell the action client that we want to spin a thread by default
        self.move_base = actionlib.SimpleActionClient(
            "move_base", MoveBaseAction)
        rospy.loginfo("Wait for the action server to come up")

        # Allow up to 5 seconds for the action server to come up
        self.move_base.wait_for_server(rospy.Duration(5))

    def callback(self, seatLocation):
        position = {'x': seatLocation.pose.position.x,
                    'y': seatLocation.pose.position.x}
        quaternion = {'r1':seatLocation.pose.orientation.x,'r2':seatLocation.pose.orientation.y, 'r3':seatLocation.pose.orientation.z, 'r4':seatLocation.pose.orientation.w}
        
        rospy.loginfo("Go to (%s, %s) pose", position['x'], position['y'])
        success = self.goto(position, quaternion)

        if success:
            rospy.loginfo("Hooray, reached the desired pose")
        else:
            rospy.loginfo("The base failed to reach the desired pose")

        

    def goto(self, pos, quat):

        # Send a goal
        self.goal_sent = True
        goal = MoveBaseGoal()
        goal.target_pose.header.frame_id = 'map'
        goal.target_pose.header.stamp = rospy.Time.now()
        goal.target_pose.pose = Pose(Point(pos['x'], pos['y'], 0.000),
                                     Quaternion(quat['r1'], quat['r2'], quat['r3'], quat['r4']))

        # Start moving
        self.move_base.send_goal(goal)

        # Allow TurtleBot up to 60 seconds to complete task
        success = self.move_base.wait_for_result(rospy.Duration(60))

        state = self.move_base.get_state()
        result = False

        if success and state == GoalStatus.SUCCEEDED:
            # We made it!
            result = True
        else:
            self.move_base.cancel_goal()

        self.goal_sent = False
        return result

    def shutdown(self):
        if self.goal_sent:
            self.move_base.cancel_goal()
        rospy.loginfo("Stop")
        rospy.sleep(1)


if __name__ == '__main__':
    try:
        rospy.init_node('navigator_listener', anonymous=True)
        rospy.init_node('nav_test', anonymous=False)
        navigator = Navigator()

        

        # Sleep to give the last log messages time to be sent
        rospy.sleep(1)
        rospy.spin()

    except rospy.ROSInterruptException:
        rospy.loginfo("Ctrl-C caught. Quitting")
