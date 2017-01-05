#!/usr/bin/python
##
## PhotoMaton V2.0 by Nicolas Cot
##
## 04/01/2017 | V2.0  | initial release
##

#Import
import RPi.GPIO as GPIO
import datetime
import time
import os
import subprocess
import atexit
import threading
#mport exifread
#from PIL import photo
from picamera import PiCamera
from time import sleep

#Configurations defines
# IO Pin define
SWITCH = 23
RESET = 25
PRINT_LED = 22
POSE_LED = 17
BUTTON_LED = 27
# Long press button setup
HOLDTIME = 5                        # Duration for button hold (shutdown)
TAPTIME = 0.01                      # Debounce time for button taps
CAM_ANGLE = 0                       # camera angle in degre
TEXT_SIZE = 100                     # on screen text size
POSTVIEW_TIME = 4                   # time to display the new picture

# GPIO setup
GPIO.setmode(GPIO.BCM)
GPIO.setup(SWITCH, GPIO.IN)
GPIO.setup(RESET, GPIO.IN)
GPIO.setup(POSE_LED, GPIO.OUT)
GPIO.setup(BUTTON_LED, GPIO.OUT)
GPIO.setup(PRINT_LED, GPIO.OUT)
#GPIO Inits
GPIO.output(POSE_LED, False)
GPIO.output(BUTTON_LED, False)
GPIO.output(PRINT_LED, False)

nbphoto = 0
print(" Python script stated ...")

# init file path
directory = '/home/pi/photobooth_images'
if os.path.exists('/media/pi/F866-6C99'):
  directory = '/media/pi/F866-6C99'
  print("found USb drive folder: "+ directory)
  if os.path.exists('/media/pi/F866-6C99/Photos'):
  	print(" Photo directory alreday exist")
  else:
    print(" create Photos directory")
    os.mkdir('/media/pi/F866-6C99/Photos')

@atexit.register
def cleanup():
  GPIO.output(BUTTON_LED, False)
  GPIO.output(POSE_LED, False)
  GPIO.cleanup()

################ blink pose led function ####################################################################################

def blinkPoseLed():
  GPIO.output(POSE_LED, True)
  time.sleep(1.5)
  for i in range(5):
    GPIO.output(POSE_LED, False)
    time.sleep(0.4)
    GPIO.output(POSE_LED, True)
    time.sleep(0.4)
  for i in range(5):
    GPIO.output(POSE_LED, False)
    time.sleep(0.1)
    GPIO.output(POSE_LED, True)
    time.sleep(0.1)
  GPIO.output(POSE_LED, False)

################ start picture capture ######################################################################################
def snapPhoto():
    global nbphoto
    nbphoto += 1
    localnbphoto = nbphoto 
    print("snap started")
    camera.annotate_text = " Photo dans 4 sec. "
    time.sleep(1)
    camera.annotate_text = " Photo dans 3 sec. "
    time.sleep(1)
    camera.annotate_text = " Photo dans 2 sec. "
    time.sleep(1)
    camera.annotate_text = " Photo dans 1 sec. "
    time.sleep(1)
    camera.annotate_text = " Clic ! "
    #camera.capture('%s/Photos/image_%s.jpg' %directory %localnbphoto)
    camera.capture('/media/pi/F866-6C99/Photos/image_%s.jpg' %localnbphoto)

################ photo requested function  ##################################################################################
def tap():
  GPIO.output(BUTTON_LED, False)

#start threads    
  blink = threading.Thread(target=blinkPoseLed)
  snap = threading.Thread(target=snapPhoto)
  blink.start()
  snap.start()
  blink.join()
  snap.join()
  
# Display the new photo
  #img = photo.open('image_%s.jpg' %nbphoto)
  #photoOverlay = camera.add_overlay(ing.tostring(), size=img.size)
  #sleep(POSTVIEW_TIME)
  #camera.remove_overlay(photoOverlay)

# reinit for the next round  
  print("ready for next round")
  camera.annotate_text = " Pret pour la prise de vue "
  GPIO.output(PRINT_LED, False)
  GPIO.output(BUTTON_LED, True)

# shutdown detected function
def hold():
  print("long pressed button! Shutting down system")
  camera.annotate_text = "Shutting down system"
  sleep(7)
  camera.stop_preview()
  subprocess.call("sudo shutdown -hP now", shell=True)

################################ MAIN #######################################################################################

## initial states for detect long or normal pressed button
prevButtonState = GPIO.input(SWITCH)
prevTime        = time.time()
tapEnable       = False
holdEnable      = False

## wait for camera to be connected
camera = PiCamera()
camera.rotation = CAM_ANGLE
camera.annotate_text_size = TEXT_SIZE
  
## Camera is now connected
print("camera is now connected ...")

GPIO.output(BUTTON_LED, True)

#start on screen preview
print("Start preview...")
camera.exif_tags['EXIF.UserComment'] = b'Photomaton V2 par Nicolas Cot'
camera.start_preview()
camera.annotate_text = " Pret pour la prise de vue "

# effect and B&W
#camera.image_effect='sketch'
camera.color_effects = (128,128)

#background
while True:

  buttonState = GPIO.input(SWITCH)
  t           = time.time()

  # Has button state changed
  if buttonState != prevButtonState:
    prevButtonState = buttonState   # Yes, save new state/time
    prevTime        = t
  else:                             # Button state unchanged
    if (t - prevTime) >= HOLDTIME:  # Button held more than 'HOLDTIME'
      # Yes it has.  Is the hold action as-yet untriggered?
      if holdEnable == True:        # Yep!
        hold()                      # Perform hold action (usu. shutdown)
        holdEnable = False          # 1 shot...don't repeat hold action
        tapEnable  = False          # Don't do tap action on release
    elif (t - prevTime) >= TAPTIME: # Not HOLDTIME.  TAPTIME elapsed?
      # Yes.  Debounced press or release...
      if buttonState == False:      # Button released?
        if tapEnable == True:       # Ignore if prior hold()
          tap()                     # Tap triggered (button released)
          tapEnable  = False        # Disable tap and hold
          holdEnable = False
      else:                         # Button pressed
        tapEnable  = True           # Enable tap and hold actions
        holdEnable = True
