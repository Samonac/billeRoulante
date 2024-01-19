#!/usr/bin/env python3
#-- coding: utf-8 --
import RPi.GPIO as GPIO
import time


#Set function to calculate percent from angle
def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180 #Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent


GPIO.setmode(GPIO.BOARD) #Use Board numerotation mode
GPIO.setwarnings(False) #Disable warnings

#Use pin 32 for PWM signal
pwm_gpio = 32
#Use pin 18 for hall sensor signal
sensor_gpio = 18
frequence = 50
GPIO.setup(pwm_gpio, GPIO.OUT)
pwm = GPIO.PWM(pwm_gpio, frequence)

print('Goto 0')
#Init at 0°
pwm.start(angle_to_percent(0))
time.sleep(5)
print('Done with 0 - starting 90')

#Go at 90°
pwm.ChangeDutyCycle(angle_to_percent(90))
time.sleep(5)

print('Done with 90 - starting 180')
#Finish at 180°
pwm.ChangeDutyCycle(angle_to_percent(180))
time.sleep(5)

print('Done with 180 - exiting')
#Close GPIO & cleanup
pwm.stop()
GPIO.cleanup()