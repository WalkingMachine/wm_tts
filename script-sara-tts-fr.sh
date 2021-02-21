#!/usr/bin/env sh


# sentence="Bonjour les petits rois\!"
sentence="$1"
gain="8"
pico2wave -l="fr-FR" -w=/tmp/test1.wav "$sentence"
sox /tmp/test1.wav /tmp/test2.wav gain -n $gain
aplay /tmp/test2.wav
rm /tmp/test1.wav
rm /tmp/test2.wav
