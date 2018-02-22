#!/usr/bin/env python
# coding=utf-8

import rospy
from wm_tts.srv import say_service
import os
from subprocess import check_call, CalledProcessError
from wm_tts.msg import say


class wm_tts:

    def __init__(self, node_name):
        rospy.init_node(node_name)
        self.langue = rospy.get_param("/langue", 'fr-FR')
        s = rospy.Service('wm_say', say_service, self.say)
        sub = rospy.Subscriber('say', data_class=say, callback=self.callback, queue_size=1)
        rospy.loginfo("language is set to "+self.langue)

    def say(self, req):
        rospy.loginfo(req.sentence)
        self.ossystem(req.sentence)

    def ossystem(self, sentence):
        try:
            os.system("amixer set Capture 0")
            os.system("pico2wave -l=" + self.langue + " -w=/tmp/test.wav " + '"' + str(sentence) + '"')
            os.system("aplay /tmp/test.wav")
            os.system("rm /tmp/test.wav")
            rospy.loginfo("SARA said: %s", sentence)
            os.system("amixer set Capture 127")
            return True
        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
        return False

    def callback(self, data):
        try:
            rospy.loginfo(data.sentence)
            self.ossystem(data.sentence)

        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
            return False


if __name__ == '__main__':

    try:
        wm_tts('wm_tts_node')
        rospy.spin()

    except rospy.ROSInterruptException:
        pass
