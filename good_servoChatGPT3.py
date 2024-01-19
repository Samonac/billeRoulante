import RPi.GPIO as GPIO
import time
from datetime import datetime

def setup_gpio(servo_pin, feedback_pin):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setup(feedback_pin, GPIO.IN)

def initialize_pwm(servo_pin, pwm_frequency=50):
    pwm = GPIO.PWM(servo_pin, pwm_frequency)
    pwm.start(0)  # Start with 0% duty cycle
    return pwm

def cleanup_gpio():
    GPIO.cleanup()

def set_servo_angle(pwm, angle, pwm_duty_cycle_min=1.28, pwm_duty_cycle_max=1.72, debounce_time=0.1):
    try:
        # Map angle (0 to 360) to duty cycle (5 to 10)
        duty_cycle = ((angle / 360) * (pwm_duty_cycle_max - pwm_duty_cycle_min)) + pwm_duty_cycle_min
        pwm.ChangeDutyCycle(duty_cycle)

        # Debounce
        time.sleep(debounce_time)

    except KeyboardInterrupt:
        pass

def always_read_feedback_signal(feedback_pin):

    servo_pin = 32

    setup_gpio(servo_pin, feedback_pin)
    try:
        feedback_total = 0
        offset_feedback_total = -30
        max_feedback = 0
        min_feedback = 9999
        max_mean_length = 30
        max_big_mean_length = 30
        mean_feedback_array = []
        big_mean_feedback_array = []
        mean_feedback = 0
        big_mean_feedback = 0

        while True:
            # MinitTime = datetime.now()
            
            # M while (datetime.now().microsecond-initTime.microsecond < 1100):
            
            feedback_value = GPIO.input(feedback_pin)
            # M print('feedback_value of type int : ', isinstance(feedback_value, int))
            #print('feedback_value : ', feedback_value)

            if (feedback_value == 0 and feedback_total != 0):
                # print("Feedback feedback_total:", feedback_total)
                if (feedback_total > max_feedback):
                    max_feedback=feedback_total
                elif (feedback_total
                       < min_feedback): 
                    min_feedback=feedback_total

                mean_feedback_array.append(feedback_total + offset_feedback_total)
                if (len(mean_feedback_array) >= max_mean_length):
                    mean_feedback = sum(mean_feedback_array)/len(mean_feedback_array)
                    #print(' => Sum of mean_feedback_array [', mean_feedback_array, '] is : ')
                    #print(' => ', mean_feedback)
                    mean_feedback_array = []
                    big_mean_feedback_array.append(mean_feedback)

                if (len(big_mean_feedback_array) >=  max_big_mean_length):
                    big_mean_feedback = sum(big_mean_feedback_array)/len(big_mean_feedback_array)
                    print(' => Sum of big_mean_feedback_array [', big_mean_feedback_array, '] is : ')
                    print(' => ', big_mean_feedback)
                    theoritical_angle = 90.0 * (big_mean_feedback / 150.0)
                    print(' => theoritical_angle is : ', theoritical_angle)

                    big_mean_feedback_array = []

                feedback_total = 0
            else:
                feedback_total += feedback_value
            # time.sleep(2)

    except KeyboardInterrupt:
        print(' (x) Interrupting ! ')
        print(' => max_feedback : ', max_feedback)
        print(' => min_feedback : ', min_feedback)

        pass

def read_feedback_signal(feedback_pin):
    # try:
        # while True:
    feedback_value = GPIO.input(feedback_pin)
    print("Feedback Value:", feedback_value)
    time.sleep(0.1)

    # except KeyboardInterrupt:
     #    pass

def mainTest():
    servo_pin = 32
    feedback_pin = 33

    setup_gpio(servo_pin, feedback_pin)
    pwm = initialize_pwm(servo_pin)
    print('starting....')
    time.sleep(2)
    # Assume you want to set the servo to 90 degrees
    pwm.ChangeDutyCycle(6.4)
    read_feedback_signal(feedback_pin)
    time.sleep(1)  # Wait for the servo to reach the desired angle
    # Assume you want to set the servo to 90 degrees
    pwm.ChangeDutyCycle(7.5)
    read_feedback_signal(feedback_pin)
    time.sleep(1)  # Wait for the servo to reach the desired angle
    # Assume you want to set the servo to 90 degrees
    pwm.ChangeDutyCycle(8.6)
    read_feedback_signal(feedback_pin)
    time.sleep(3)  # Wait for the servo to reach the desired angle
    # Assume you want to set the servo to 90 degrees
    pwm.ChangeDutyCycle(7.5)
    read_feedback_signal(feedback_pin)
    time.sleep(1)  # Wait for the servo to reach the desired angle
    # Assume you want to set the servo to 90 degrees
    pwm.ChangeDutyCycle(6.4)
    read_feedback_signal(feedback_pin)
    time.sleep(1)  # Wait for the servo to reach the desired angle

    cleanup_gpio()
    pwm.stop()


def asserv_angle(angle_input = 0, speed_input = 50, servoNumber = 1):

    servo_pin = 32
    feedback_pin = 33

    if (speed_input == 100):
        negativeDutyCycle = 12
        neutralDutyCycle = 0
        positiveDutyCycle = 2
    else:
        negativeDutyCycle = 7.5
        neutralDutyCycle = 0
        positiveDutyCycle = 6.5

    offset_feedback_total = -30
    sleep_pwm = 0.04
    long_sleep_pwm = 2
    min_delta_angle = 5

    setup_gpio(servo_pin, feedback_pin)
    pwm = initialize_pwm(servo_pin) 
    try:
        feedback_total = 0
        max_feedback = 0
        min_feedback = 9999
        max_mean_length = 30
        max_big_mean_length = 33
        mean_feedback_array = []
        big_mean_feedback_array = []
        mean_feedback = 0
        big_mean_feedback = 0

        input_user_necessary = False

        while True:
            # MinitTime = datetime.now()
            
            # M while (datetime.now().microsecond-initTime.microsecond < 1100):
            
            feedback_value = GPIO.input(feedback_pin)
            # M print('feedback_value of type int : ', isinstance(feedback_value, int))
            #print('feedback_value : ', feedback_value)

            if (feedback_value == 0 and feedback_total != 0):
                # print("Feedback feedback_total:", feedback_total)
                if (feedback_total > max_feedback):
                    max_feedback=feedback_total
                elif (feedback_total
                       < min_feedback): 
                    min_feedback=feedback_total

                mean_feedback_array.append(feedback_total + offset_feedback_total)
                if (len(mean_feedback_array) >= max_mean_length):
                    mean_feedback = sum(mean_feedback_array)/len(mean_feedback_array)
                    #print(' => Sum of mean_feedback_array [', mean_feedback_array, '] is : ')
                    #print(' => ', mean_feedback)
                    mean_feedback_array = []
                    big_mean_feedback_array.append(mean_feedback)

                if (len(big_mean_feedback_array) >=  max_big_mean_length):
                    big_mean_feedback = sum(big_mean_feedback_array)/len(big_mean_feedback_array)
                    #print(' => Sum of big_mean_feedback_array [', big_mean_feedback_array, '] is : ')
                    #print(' => ', big_mean_feedback)
                    theoritical_angle = 90.0 * (big_mean_feedback / 150.0)
                    print('\n\n##########\n# => theoritical_angle is : ', theoritical_angle)
                    print(' => angle_input is : ', angle_input)

                    # should be new function
                    print('           theoritical_angle - angle_input : ', theoritical_angle - angle_input)
                    print('           360.0 - theoritical_angle + angle_input : ', 360.0 - theoritical_angle + angle_input)

                    delta_angle = min(abs(theoritical_angle - angle_input), abs(360.0 - theoritical_angle + angle_input))

                    print(' => delta_angle is : ', delta_angle)

                    #if (delta_angle == abs(theoritical_angle - angle_input)):
                    #if (delta_angle == abs(360.0 - theoritical_angle + angle_input)):
                    if (theoritical_angle > angle_input):
                    #if (360.0 - theoritical_angle + angle_input > theoritical_angle - angle_input):
                        delta_angle = -1.0 * delta_angle
                        print('  (?) delta_angle should be negative (?) : ', delta_angle)
                    if (abs(delta_angle) < min_delta_angle):
                        print(' (!) should be close enough, pwm.dutyCycle(0)')
                        pwm.ChangeDutyCycle(neutralDutyCycle)
                        # input_user_necessary = True
                        angle_input = float(input('\n ===> Choose a new angle :'))
                    else:
                        if(delta_angle > 0):
                            # duty_cycle = ((delta_angle / 360) * (pwm_duty_cycle_max - pwm_duty_cycle_min)) + pwm_duty_cycle_min
                            print('  -> delta is positive : pwm.dutyCycle(', positiveDutyCycle, ')')
                            pwm.ChangeDutyCycle(positiveDutyCycle)
                            time.sleep(sleep_pwm)
                            pwm.ChangeDutyCycle(0)
                        elif (delta_angle < 0):
                            print('  -> delta is negative : pwm.dutyCycle(', negativeDutyCycle, ')')
                            pwm.ChangeDutyCycle(negativeDutyCycle)
                            time.sleep(sleep_pwm)
                            pwm.ChangeDutyCycle(0)

                        # time.sleep(long_sleep_pwm)
                        
                    

                    big_mean_feedback_array = []

                feedback_total = 0
            else:
                feedback_total += feedback_value
            # time.sleep(2)

    except KeyboardInterrupt:
        print(' (x) Interrupting ! ')
        print(' => max_feedback : ', max_feedback)
        print(' => min_feedback : ', min_feedback)

        pass


def mainTestLoop():
    servo_1_pin = 12
    feedback_1_pin = 32
    servo_2_pin = 33
    feedback_2_pin = 35
    duty_cycle = 7

    setup_gpio(servo_1_pin, feedback_1_pin)
    setup_gpio(servo_2_pin, feedback_2_pin)
    pwm = initialize_pwm(servo_1_pin)
    pwm2 = initialize_pwm(servo_2_pin)
    print('starting....')
    # time.sleep(2)
    # Assume you want to set the servo to 90 degree

    try:
        while True:
            duty_cycle = float(input('duty_cycle ? '))
            print('duty_cycle : ', duty_cycle)
            pwm.ChangeDutyCycle(duty_cycle)
            pwm2.ChangeDutyCycle(duty_cycle)

            time.sleep(3)  # Wait for the servo to reach the desired angle

            pwm.ChangeDutyCycle(0)
            pwm2.ChangeDutyCycle(0)
            # read_feedback_signal(feedback_pin)
            # time.sleep(1)  # Wait for the servo to reach the desired angle
            # duty_cycle += 0.01

    except KeyboardInterrupt:
        pass
    

    cleanup_gpio()
    pwm.stop()

def main():
    servo_pin = 32
    feedback_pin = 33

    setup_gpio(servo_pin, feedback_pin)
    pwm = initialize_pwm(servo_pin)

    try:
        while True:
            # Assume you want to set the servo to 90 degrees
            set_servo_angle(pwm, 90)
            read_feedback_signal(feedback_pin)
            time.sleep(1)  # Wait for the servo to reach the desired angle

    except KeyboardInterrupt:
        pass

    finally:
        cleanup_gpio()
        pwm.stop()
        


if __name__ == "__main__":
    # asserv_angle(90)

    # always_read_feedback_signal(33)
     # main()
    
    mainTestLoop()
