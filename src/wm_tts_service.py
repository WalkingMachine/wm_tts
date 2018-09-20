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

        s = rospy.Service('wm_say', say_service, self.serviceCallback)
        sub = rospy.Subscriber('say', data_class=say, callback=self.topicCallback, queue_size=1)

    # Fonction utilisé pour executer les appels de service.
    def serviceCallback(self, req):
        self.rospy.loginfo(req.say.sentence)

    # Fonction utilisé pour executer les commandes faites par topic.
    def topicCallback(self, data):
        self.saySomething(data.sentence)

    # Fonction qui dit quelque chose.
    def saySomething(self, sentence):
        rospy.loginfo(sentence)
        self.langue = rospy.get_param("/langue", 'en-US')
        self.langue_online = self.langue[:2]
        self.gain = rospy.get_param("/gain", 8)
        self.forceOffline = rospy.get_param("/force_offline", True)

        if not self.forceOffline and self.internet_on():
            self.online_tts(sentence)
        else:
            self.offline_tts(sentence)
        return True

    # Vérifie que l'internet est disponnible
    @staticmethod
    def internet_on():
        try:
            urllib2.urlopen('http://172.217.13.174', timeout=0.1)
            return True
        except urllib2.URLError as err:
            return False


    def offline_tts(self, sentence):
        self.p2w_tts(sentence)

    # Utilise le Pico2Wav pour dire quelque chose.
    def p2w_tts(self, sentence):
        try:
            os.system("amixer set Capture 0")
            os.system("pico2wave -l=" + self.langue + " -w=/tmp/test1.wav " + '"' + str(sentence) + '"')
            os.system("sox /tmp/test1.wav /tmp/test2.wav gain -n " + str(self.gain))
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


    # Utilise le GoogleSpeechAPI pour dire quelque chose.
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


if __name__ == '__main__':

    try:
        wm_tts('wm_tts_node')
        rospy.spin()

    except rospy.ROSInterruptException:
        pass
