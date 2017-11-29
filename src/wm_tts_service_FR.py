#!/usr/bin/env python
# coding=utf-8

import rospy
from std_msgs.msg import String
from wm_tts.srv import *
from wm_tts.msg import *
import os
from subprocess import check_call, CalledProcessError


class wm_tts:
    def __init__(self, node_name):
        rospy.init_node(node_name)
        s = rospy.Service('wm_say', say_service, self.say)
        sub = rospy.Subscriber('say', data_class=say, callback=self.callback, queue_size=1)
    def say(self, req):
        rospy.loginfo(req.say.sentence)

        try:
            os.system("amixer set Capture 0")
            os.system("pico2wave -l=fr-FR -w=/tmp/test.wav " + '"'+str(req.say.sentence)+'"')
            os.system("aplay /tmp/test.wav")
            os.system("rm /tmp/test.wav")
            rospy.loginfo("SARA said: %s", req.say.sentence)
            os.system("amixer set Capture 127")
            return True

        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
            return False

    def callback(self, data):
        rospy.loginfo(data.sentence)

        try:
            os.system("amixer set Capture 0")
            os.system("pico2wave -l=fr-FR -w=/tmp/test.wav " + '"'+str(data.sentence)+'"')
            os.system("aplay /tmp/test.wav")
            os.system("rm /tmp/test.wav")
            os.system("amixer set Capture 127")
            rospy.loginfo("SARA said: %s", data.sentence)

        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')



if __name__ == '__main__':

    try:
        wm_tts('wm_tts_node')

        rospy.spin()

    except rospy.ROSInterruptException:
        pass
