#!/usr/bin/env python
# coding=utf-8

import os
import urllib2
from subprocess import CalledProcessError

import rospy
from std_msgs.msg import String
from wm_tts.msg import say
from wm_tts.srv import say_service


# HTTP + URL packages
import httplib2

#from urlparse import urlparse
#from urllib.parse import urlencode, quote # For URL creation
import urllib


# To play wave files
import pygame
import math # For ceiling


# Mary server informations
mary_host = "localhost"
mary_port = "59125"


class wm_tts:

    def __init__(self, node_name):
        rospy.init_node(node_name)
        self.pub = rospy.Publisher('sara_said', String, queue_size=10)

        s = rospy.Service('wm_say', say_service, self.serviceCallback)
        sub = rospy.Subscriber('say', data_class=say, callback=self.topicCallback, queue_size=1)

    # Fonction utilisé pour executer les appels de service.
    def serviceCallback(self, req):
        self.saySomething(req.say.sentence)

    # Fonction utilisé pour executer les commandes faites par topic.
    def topicCallback(self, data):
        self.saySomething(data.sentence)

    # Fonction qui dit quelque chose.
    def saySomething(self, sentence):
        rospy.loginfo(sentence)

        # Met à jours les paramètres.
        self.langue = rospy.get_param("/langue", 'en-US')
        self.langue_online = self.langue[:2]
        self.gain = rospy.get_param("/gain", 8)
        self.forceOffline = rospy.get_param("/force_offline", False)

        print("langue = "+str(self.langue))
        print("gain = "+str(self.gain))
        print("force_offline = "+str(self.forceOffline))

        # Ferme le micro pour pas que le robot s'entende
        os.system("amixer set Capture 0")

        # Choisi si on utilise le tts online ou offline
        if not self.forceOffline and self.internet_on():
            resp = self.online_tts(sentence)
        else:
            resp = self.offline_tts(sentence)

        # Réouvre le micro
        os.system("amixer set Capture 127")
        return resp

    # Vérifie que l'internet est disponnible
    @staticmethod
    def internet_on():
        try:
            urllib2.urlopen('http://172.217.13.174', timeout=0.1)
            return True
        except urllib2.URLError as err:
            return False


    def offline_tts(self, sentence):
        if not self.mary_tts(sentence):
            return self.p2w_tts(sentence)
        else:
            return True

    # Utilise le Pico2Wav pour dire quelque chose.
    def p2w_tts(self, sentence):
        try:
            os.system("pico2wave -l=" + self.langue + " -w=/tmp/test1.wav " + '"' + str(sentence) + '"')
            os.system("sox /tmp/test1.wav /tmp/test2.wav gain -n " + str(self.gain))
            os.system("aplay /tmp/test2.wav")
            os.system("rm /tmp/test1.wav")
            os.system("rm /tmp/test2.wav")

            sentence_str = "SARA said: %s" % sentence
            rospy.loginfo(sentence_str)
            self.pub.publish(sentence_str)
            return True
        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
        return False

    # Utilise le Mary tts pour dire quelque chose.
    def mary_tts(self, sentence):

        if not "en-US" in self.langue:
            print( "not in english")
            return False

        try:
            # Build the query
            # "VOICE":"cmu-slt-hsmm", # Voice informations  (need to be compatible)
            query_hash = {"INPUT_TEXT": sentence,
                          "INPUT_TYPE": "TEXT",  # Input text
                          "LOCALE": "en_US",
                          "Voice": "cmu-slt-hsmm",
                          "style": "",
                          "OUTPUT_TYPE": "AUDIO",
                          "AUDIO": "WAVE",  # Audio informations (need both)
                          "effect_F0Add_selected": "on",
                          "effect_F0Add_parameters": "40.0",
                          "effect_F0Scale_selected": "on",
                          "effect_F0Scale_parameters": "0.5"
                          }
            query = urllib.urlencode(query_hash)
            print("query = \"http://%s:%s/process?%s\"" % (mary_host, mary_port, query))

            # Run the query to mary http server
            h_mary = httplib2.Http()
            resp, content = h_mary.request("http://%s:%s/process?" % (mary_host, mary_port), "POST", query)

            #  Decode the wav file or raise an exception if no wav files
            if (resp["content-type"] == "audio/x-wav"):

                # Write the wav file
                f = open("/tmp/output_wav.wav", "wb")
                f.write(content)
                f.close()

                # Play the wav file
                # os.system("aplay /tmp/output_wav.wav")
                pygame.mixer.init(frequency=48000, )  # Initialise the mixer
                s = pygame.mixer.Sound("/tmp/output_wav.wav")
                s.play()
                pygame.time.wait(int(math.ceil(s.get_length() * 1000)))

            else:
                raise Exception(content)
            return True
        except CalledProcessError:
            rospy.logwarn('Last subprocess call was not valid.')
        return False

    # Utilise le GoogleSpeechAPI pour dire quelque chose.
    def online_tts(self, sentence):
        return self.gsapi_tts(sentence)

    def gsapi_tts(self, sentence):
        try:
            os.system("gtts-cli " + '"' + str(sentence) + '"' + " -l '" + self.langue_online + "' -o /tmp/test.mp3")
            rospy.loginfo("gtts-cli " + '"' + str(sentence) + '"' + " -l '" + self.langue_online + "' -o /tmp/test.mp3")
            os.system("mpg123 /tmp/test.mp3")
            os.system("rm /tmp/test.mp3")
            sentence_str = "SARA said: %s" % sentence
            rospy.loginfo(sentence_str)
            self.pub.publish(sentence_str)
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
