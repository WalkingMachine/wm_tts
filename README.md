# wm_tts [![Build Status](https://travis-ci.org/WalkingMachine/wm_tts.svg?branch=master)](https://travis-ci.org/WalkingMachine/wm_tts)

## Description :
wm_tts is a collect a series of text to speech api and chose the correct one to use depending on the network availability and chosen language.

## Dependencies :

`sudo apt install libttspico-utils -y`  
`sudo apt install mpg123`  
`sudo apt install sox`  
`pip install gtts`  
`pip install urllib`  
`pip install pygame`  
https://github.com/marytts/marytts

## rosparams:

```/langue``` Allow to choose the language. (default: en-US) also support fr-FR

```/gain``` Apply a volume gain to the offline voice.

```/force_offline``` Force the use of offline solution to avoid network issues.


## Topic :

```/say```

message type wm_tts/say


## Service:

```/wm_say```

service type wm_tts/say_service
