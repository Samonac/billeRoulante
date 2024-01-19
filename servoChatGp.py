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

def set_servo_angle(pwm, angle, debounce_time=0.1):
    try:
        # Map angle (0 to 180) to control signal pulse width (1280 to 1720 μs)
        pulse_width = ((angle / 180.0) * (1720 - 1280)) + 1280
        pwm.ChangeDutyCycle(pulse_width / 20.0)  # Convert pulse width to duty cycle

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
            set_servo_angle(pwm, 180)
            time.sleep(1)  # Wait for the servo to reach the desired angle

    except KeyboardInterrupt:
        pass

    finally:
        cleanup_gpio()
        pwm.stop()

if __name__ == "__main__":
    main()
