#!/usr/bin/env python
# coding=utf-8

import os
import urllib2
from subprocess import CalledProcessError
import actionlib
import rospy
from std_msgs.msg import String
from wm_tts.msg import say
from sara_msgs.msg import tellAction, tellActionResult
# import sara_msgs.msg

class wm_tts:

    def __init__(self, node_name):
        rospy.init_node(node_name)
        self.pub = rospy.Publisher('sara_said', String, queue_size=10)

        self.langue = rospy.get_param("/langue", 'fr-FR')
        self.langue_online = self.langue[:2]

        self.server = actionlib.SimpleActionServer('sara_say', tellAction, self.execute, False)
        self.server.start()

        sub = rospy.Subscriber('say', data_class=say, callback=self.callback, queue_size=1)

        rospy.loginfo("language is set to " + self.langue)

    def callback(self, data):
        try:
            rospy.loginfo(data.sentence)
            if self.internet_on():
                self.online_tts(data.sentence)
            else:
                self.offline_tts(data.sentence)

        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
            return False

    @staticmethod
    def internet_on():
        try:
            urllib2.urlopen('http://172.217.13.174', timeout=1)
            return True
        except urllib2.URLError as err:
            return False

    def offline_tts(self, sentence):
        try:
            os.system("amixer set Capture 0")
            os.system("pico2wave -l=" + self.langue + " -w=/tmp/test.wav " + '"' + str(sentence) + '"')
            os.system("aplay /tmp/test.wav")
            os.system("rm /tmp/test.wav")
            sentence_str = "SARA said: %s" % sentence
            rospy.loginfo(sentence_str)
            self.pub.publish(sentence_str)
            os.system("amixer set Capture 127")
            return True
        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
        return False

    def online_tts(self, sentence):
        try:
            os.system("amixer set Capture 0")

            os.system("gtts-cli " + '"' + str(sentence) + '"' + " -l '" + self.langue_online + "' -o /tmp/test.mp3")
            rospy.loginfo("gtts-cli " + '"' + str(sentence) + '"' + " -l '" + self.langue_online + "' -o /tmp/test.mp3")
            os.system("mpg123 /tmp/test.mp3")
            os.system("rm /tmp/test.mp3")
            sentence_str = "SARA said: %s" % sentence
            rospy.loginfo(sentence_str)
            self.pub.publish(sentence_str)
            os.system("amixer set Capture 127")
            return True
        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
        return False

    def execute(self, goal):
        result = tellActionResult()
        try:
            rospy.loginfo(goal.message)
            if self.internet_on():
                self.online_tts(goal.message)
            else:
                self.offline_tts(goal.message)

            result.result.success = True
            self.server.set_succeeded(result.result)

        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
            result.result.success = False
            self.server.set_succeeded(result.result)
            return False


if __name__ == '__main__':

    try:
        wm_tts('wm_tts_node')
        rospy.spin()

    except rospy.ROSInterruptException:
        pass
