from rpi_ws281x import *
import time

TOTAL_LED_COUNT = 120
LED_CHIP_NUMBER = 11
R = 155
G = 5
B = 5

"""class PixelStrip:
    def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False,
            brightness=255, channel=0, strip_type=None, gamma=None):
        Class to represent a SK6812/WS281x LED display.  Num should be the
        number of pixels in the display, and pin should be the GPIO pin connected
        to the display signal line (must be a PWM pin like 18!).  Optional
        parameters are freq, the frequency of the display signal in hertz (default
        800khz), dma, the DMA channel to use (default 10), invert, a boolean
        specifying if the signal line should be inverted (default False), and
        channel, the PWM channel to use (defaults to 0)."""

strip = Adafruit_NeoPixel(TOTAL_LED_COUNT, 18, 1000000, 5, True, 255)
strip.begin()

def checkLed(strip, LED_CHIP_NUMBER):

    print('\nin checkLed with LED_CHIP_NUMBER : ', LED_CHIP_NUMBER)
    
    strip.setPixelColorRGB(LED_CHIP_NUMBER, 100, 100, 100)
    print(LED_CHIP_NUMBER, 100, 100, 100)
    strip.show()
    time.sleep(0.5)
    strip.setPixelColorRGB(LED_CHIP_NUMBER, 0, 0, 0)
    strip.show()
    print((LED_CHIP_NUMBER, 0, 0, 0))

def checkLed_old(strip, LED_CHIP_NUMBER, i):
    print('in checkLed with LED_CHIP_NUMBER : ', LED_CHIP_NUMBER)
    print('in checkLed with i : ', i)
    strip.setPixelColorRGB(LED_CHIP_NUMBER, i, 10, 10)
    strip.show()
    print((LED_CHIP_NUMBER, i, 10, 10))
    time.sleep(0.1)
    strip.setPixelColorRGB(LED_CHIP_NUMBER, 0, i, 0)
    print(LED_CHIP_NUMBER, 0, i, 0)
    strip.show()
    time.sleep(0.1)
    strip.setPixelColorRGB(LED_CHIP_NUMBER, 0, 0, i)
    print(LED_CHIP_NUMBER, 0, 0, i)
    strip.show()
    time.sleep(0.1)
    strip.setPixelColorRGB(LED_CHIP_NUMBER, i, 0, 0)
    print(LED_CHIP_NUMBER, i, 0, 0)
    strip.show()
    time.sleep(0.1)
    strip.setPixelColorRGB(LED_CHIP_NUMBER, 10, i, 0)
    print(LED_CHIP_NUMBER, 10, i, 0)
    strip.show()


i = 50
while i< 255:
    i += 10
    j = 0
    while j< TOTAL_LED_COUNT:
        j += 1
        """checkLed(strip, LED_CHIP_NUMBER-2, i)
        checkLed(strip, LED_CHIP_NUMBER-1, i)"""
        checkLed_old(strip, j, i)
        """checkLed(strip, LED_CHIP_NUMBER+1, i)
        checkLed(strip, LED_CHIP_NUMBER+2, i)
        checkLed(strip, LED_CHIP_NUMBER+3, i)"""
        time.sleep(0.1)
