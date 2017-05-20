#!/usr/bin/env python
# coding=utf-8

import rospy
from std_msgs.msg import String
from wm_tts.srv import *
import os
from subprocess import check_call, CalledProcessError

class wm_tts:
    def __init__(self, node_name):
        rospy.init_node(node_name)
        s = rospy.Service('wm_say', say_service, self.say)

    def say(self, req):
        rospy.loginfo(req.say.sentence)

        try:
            os.system("pico2wave -l=fr-FR -w=/tmp/test.wav " + '"'+str(req.say.sentence)+'"')
            os.system("aplay /tmp/test.wav")
            os.system("rm /tmp/test.wav")
            rospy.loginfo("SARA said: %s", req.say.sentence)
            return True

        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
            return False

if __name__ == '__main__':

    try:
        wm_tts('wm_tts_node')

        rospy.spin()

    except rospy.ROSInterruptException:
        pass
