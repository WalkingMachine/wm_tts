#!/usr/bin/env python
# coding=utf-8

import os
import urllib2
from subprocess import CalledProcessError

import rospy
from std_msgs.msg import String
from wm_tts.msg import say
from wm_tts.srv import say_service


class wm_tts:

    def __init__(self, node_name):
        rospy.init_node(node_name)
        self.pub = rospy.Publisher('sara_said', String, queue_size=10)

        s = rospy.Service('wm_say', say_service, self.say)
        sub = rospy.Subscriber('say', data_class=say, callback=self.callback, queue_size=1)

    def say(self, req):
        rospy.loginfo(req.say.sentence)
        self.langue = rospy.get_param("/langue", 'en-US')
        self.langue_online = self.langue[:2]
        self.gain = rospy.get_param("/gain", 8)
        self.forceOffline = rospy.get_param("/force_offline", True)

        if not self.forceOffline and self.internet_on():
            self.online_tts(req.say.sentence)
        else:
            self.offline_tts(req.say.sentence)
        return True

    @staticmethod
    def internet_on():
        try:
            urllib2.urlopen('http://172.217.13.174', timeout=0.1)
            return True
        except urllib2.URLError as err: 
            return False

    def offline_tts(self, sentence):
        try:
            os.system("amixer set Capture 0")
            os.system("pico2wave -l=" + self.langue + " -w=/tmp/test1.wav " + '"' + str(sentence) + '"')
            os.system("sox /tmp/test1.wav /tmp/test2.wav gain -n "+str(self.gain))
            os.system("aplay /tmp/test2.wav")
            os.system("rm /tmp/test1.wav")
            os.system("rm /tmp/test2.wav")
            
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

    def callback(self, data):
        try:
            rospy.loginfo(data.sentence)
            if not self.forceOffline and self.internet_on():
                self.online_tts(data.sentence)
            else:
                self.offline_tts(data.sentence)

        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
            return False


if __name__ == '__main__':

    try:
        wm_tts('wm_tts_node')
        rospy.spin()

    except rospy.ROSInterruptException:
        pass
