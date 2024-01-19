import pigpio
import time

def set_servo_angle(pi, servo_pin, angle, debounce_time=0.1):
    try:
        # Map angle (0 to 180) to pulse width (1000 to 2000)
        pulse_width = int((angle / 180.0) * 1000) + 1000
        pi.set_servo_pulsewidth(servo_pin, pulse_width)

        # Wait for the servo to reach the desired angle
        time.sleep(1)

        # Stop the servo
        pi.set_servo_pulsewidth(servo_pin, 0)

        # Debounce
        time.sleep(debounce_time)

    except KeyboardInterrupt:
        pass

def main():
    servo_pin = 32

    # Connect to the pigpio daemon
    pi = pigpio.pi()

    try:
        while True:
            # Assume you want to set the servo to 90 degrees
            set_servo_angle(pi, servo_pin, 90)

    except KeyboardInterrupt:
        pass

    finally:
        # Disconnect from the pigpio daemon
        pi.stop()

if __name__ == "__main__":
    main()
