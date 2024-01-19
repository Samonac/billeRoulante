import RPi.GPIO as GPIO
import time

# duty cycle, calibrate if needed
MIN_DUTY = 2.9
MAX_DUTY = 97.1

servo_signal_pin = 32

def deg_to_duty(deg):
    return 1.0*((deg - 0) * (MAX_DUTY- MIN_DUTY) / 180 + MIN_DUTY)

if __name__ == "__main__":
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)

    GPIO.setup(servo_signal_pin, GPIO.OUT)
    # set pwm signal to 50Hz
    servo = GPIO.PWM(servo_signal_pin, 50)
    servo.start(0)

    # loop from 0 to 180
    for deg in range(181):
        print('deg : ', deg)
        duty_cycle = deg_to_duty(deg)    
        print('duty_cycle : ', duty_cycle)
        servo.ChangeDutyCycle(duty_cycle)
        time.sleep(0.5)

    # cleanup the gpio pins
    GPIO.cleanup()