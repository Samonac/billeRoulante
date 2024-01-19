import RPi.GPIO as GPIO
import time

def setup_gpio(servo_pin, hall_sensor_pin):
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(servo_pin, GPIO.OUT)
    GPIO.setup(hall_sensor_pin, GPIO.IN)

def initialize_pwm(servo_pin, pwm_frequency=50):
    pwm = GPIO.PWM(servo_pin, pwm_frequency)
    pwm.start(0)  # Start with 0% duty cycle
    return pwm

def cleanup_gpio():
    GPIO.cleanup()

def set_servo_angle(pwm, angle, pwm_duty_cycle_min=5, pwm_duty_cycle_max=10, debounce_time=1):
    try:
        # Map angle (0 to 180) to duty cycle (1280 to 1720)
        duty_cycle = ((angle / 180.0) * (pwm_duty_cycle_max - pwm_duty_cycle_min)) + pwm_duty_cycle_min
        pwm.ChangeDutyCycle(duty_cycle)

        # Debounce the hall sensor
        time.sleep(debounce_time)

    except KeyboardInterrupt:
        pass


def set_servo_angle2(pwm, angle, pwm_duty_cycle_min=5, pwm_duty_cycle_max=10, debounce_time=1):
    try:
        # Map angle (0 to 180) to duty cycle (1280 to 1720)
        duty_cycle = ((angle / 180.0) * (pwm_duty_cycle_max - pwm_duty_cycle_min)) + pwm_duty_cycle_min
        pwm.ChangeDutyCycle(duty_cycle)

        # Debounce the hall sensor
        time.sleep(debounce_time)

    except KeyboardInterrupt:
        pass

def main():
    servo_pin = 32
    hall_sensor_pin = 18

    setup_gpio(servo_pin, hall_sensor_pin)
    pwm = initialize_pwm(servo_pin)

    try:
        while True:
            # Assume you want to set the servo to 90 degrees
            # set_servo_angle(pwm, 90)
            pwm.ChangeDutyCycle(1500)
            print('hall sensor should be : ')
            print(GPIO.input(hall_sensor_pin))
            time.sleep(1)  # Wait for the servo to reach the desired angle

    except KeyboardInterrupt:
        pass

    finally:
        cleanup_gpio()
        pwm.stop()

if __name__ == "__main__":
    main()
