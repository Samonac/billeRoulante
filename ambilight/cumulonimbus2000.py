#!/usr/bin/env python3
# NeoPixel library strandtest example
# Author: Tony DiCola (tony@tonydicola.com)
#
# Direct port of the Arduino NeoPixel library strandtest example.  Showcases
# various animations on a strip of NeoPixels.

import time
from rpi_ws281x import PixelStrip, Color
import argparse
import python_weather
import asyncio
import os
from random import randrange
import requests
import json
import datetime
import glob
from dotenv import load_dotenv

load_dotenv()

apiKey = os.getenv('RATP_API_KEY')
query = {'MonitoringRef': 'STIF:StopArea:SP:474151:', 'LineRef': 'STIF:Line::C01742:'}  # , {'name':'Châtelet les Halles', 'id':'474151', 'rer':'A'}]
my_headers = {'apiKey' : apiKey}
dataRatp = {'codesRer' : {'C': 'C01727', 'N': 'C01736', 'A': 'C01742'},
            'arrayArrets' : [{'name':'Gare de Meudon', 'id':'41214', 'rer': 'N'}, {'name':'Meudon Val Fleury', 'id':'41213', 'rer':'C'}]}
#  response = requests.get('http://httpbin.org/headers', headers=my_headers)  {}  

async def getRatpData(saveJson=False):

    jsonOutput = {}
    for rerTemp in dataRatp['codesRer'].keys():
        jsonOutput[rerTemp] = []

    for arretArray in dataRatp['arrayArrets']:
        print(arretArray)

        codeRerTemp = dataRatp['codesRer'][arretArray['rer']]
        codeArretTemp = arretArray['id']

        query = {'MonitoringRef': 'STIF:StopArea:SP:{}:'.format(codeArretTemp), 'LineRef': 'STIF:Line::{}:'.format(codeRerTemp)}
        #  requestUrl_old = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?MonitoringRef=STIF%3AStopArea%3ASP%3A{}%3A&LineRef=STIF%3ALine%3A%3A{}%3A'.format(codeArretTemp, codeRerTemp)
        #  requestUrl = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring?MonitoringRef=STIF:StopArea:SP:{}:&LineRef=STIF:Line::{}:'.format(codeArretTemp, codeRerTemp)
        requestUrl = 'https://prim.iledefrance-mobilites.fr/marketplace/stop-monitoring'
        # print(query)
        response = requests.get(requestUrl, params=query, headers=my_headers)
        monitoredStopsArray = response.json()['Siri']['ServiceDelivery']['StopMonitoringDelivery'][0]['MonitoredStopVisit']
        # print(monitoredStopsArray)
        for monitoredStopTemp in monitoredStopsArray:
            
            jsonInputTemp = monitoredStopTemp['MonitoredVehicleJourney']
            # print(jsonInputTemp['MonitoredCall'])
            jsonTemp = {}
            try:
                jsonTemp['DestinationName'] = jsonInputTemp['DestinationName'][0]['value']
            except KeyError as err:
                jsonTemp['DestinationName'] = None
            try:
                jsonTemp['RecordedAtTime'] = monitoredStopTemp['RecordedAtTime']
            except KeyError as err:
                jsonTemp['RecordedAtTime'] = None
            try:
                jsonTemp['ExpectedArrivalTime'] = jsonInputTemp['MonitoredCall']['ExpectedArrivalTime']
            except KeyError as err:
                jsonTemp['ExpectedArrivalTime'] = None
            try:
                jsonTemp['ExpectedDepartureTime'] = jsonInputTemp['MonitoredCall']['ExpectedDepartureTime']
            except KeyError as err:
                jsonTemp['ExpectedDepartureTime'] = None
            try:
                jsonTemp['DepartureStatus'] = jsonInputTemp['MonitoredCall']['DepartureStatus']
            except KeyError as err:
                jsonTemp['DepartureStatus'] = None
            try:
                jsonTemp['AimedArrivalTime'] = jsonInputTemp['MonitoredCall']['AimedArrivalTime']
            except KeyError as err:
                jsonTemp['AimedArrivalTime'] = None
            try:
                jsonTemp['AimedDepartureTime'] = jsonInputTemp['MonitoredCall']['AimedDepartureTime']
            except KeyError as err:
                jsonTemp['AimedDepartureTime'] = None
            try:
                jsonTemp['ArrivalStatus'] = jsonInputTemp['MonitoredCall']['ArrivalStatus']
            except KeyError as err:
                jsonTemp['ArrivalStatus'] = None

            # print(jsonTemp)

            jsonOutput[arretArray['rer']].append(jsonTemp)
    # print(jsonOutput)
    if saveJson:
        print('Saving RATP json file')
        currentTime = datetime.datetime.now()
        fileName = '{}'.format(currentTime).replace(' ', '_').replace(':', '-').replace('.', '_')
        print('fileName : ', fileName)


        jsonArray = glob.glob('data/ratp/*.json')
        while len(jsonArray) > 10:
            os.remove('{}'.format(jsonArray[0]))
            jsonArray = glob.glob('data/ratp/*.json')

        with open('data/ratp/{}.json'.format(fileName), "w") as outfile:
            outfile.write('{}'.format(jsonOutput))

    return jsonOutput

async def getweather(saveJson=False):
  # declare the client. the measuring unit used defaults to the metric system (celcius, km/h, etc.)
  async with python_weather.Client(unit=python_weather.METRIC) as client:
    # fetch a weather forecast from a city
    weather = await client.get('Meudon')
    jsonOutput = {}
    jsonOutput['now'] = {}
    jsonOutput['now']['temperature'] = weather.current.temperature
    jsonOutput['now']['description'] = weather.current.description
    jsonOutput['now']['kind'] = '{}'.format(weather.current.kind).replace('Kind.', '')
    # returns the current day's forecast temperature (int)
    print(weather.current)
    
    # get the weather forecast for a few days
    for forecast in weather.forecasts:
        # print(forecast) datetime.date(2024, 1, 24)
        foreCastDate = '{}'.format(forecast.date).replace('datetime.date(', '').replace(')', '').replace(' ', '').replace(',', '-')
      
        jsonOutput[foreCastDate] = {}
        jsonOutput[foreCastDate]['hourly'] = []
        jsonOutput[foreCastDate]['temperature'] = forecast.temperature
        jsonOutput[foreCastDate]['astronomy'] = {}
        jsonOutput[foreCastDate]['astronomy']['moon_phase'] = '{}'.format(forecast.astronomy.moon_phase).replace('Phase.', '')
        jsonOutput[foreCastDate]['astronomy']['sun_rise'] = '{}'.format(forecast.astronomy.sun_rise).replace('datetime.date(', '').replace(')', '').replace(' ', '').replace(',', '-')
        jsonOutput[foreCastDate]['astronomy']['sun_set'] = '{}'.format(forecast.astronomy.sun_set).replace('datetime.date(', '').replace(')', '').replace(' ', '').replace(',', '-')
      
        # hourly forecasts
        for hourly in forecast.hourly:
            jsonHourly = {}
            foreCastTime = '{}'.format(hourly.time).replace('datetime.date(', '').replace(')', '').replace(' ', '').replace(',', '-').replace(':', '-')
            jsonHourly['time'] = foreCastTime
            jsonHourly['temperature'] = hourly.temperature
            jsonHourly['description'] = hourly.description
            jsonHourly['kind'] = '{}'.format(hourly.kind).replace('Kind.', '')
            
            jsonOutput[foreCastDate]['hourly'].append(jsonHourly)
            # print(f' --> {hourly!r}')

    if saveJson:
        print('Saving Weather json file')
        currentTime = datetime.datetime.now()
        fileName = '{}'.format(currentTime).replace(' ', '_').replace(':', '-').replace('.', '_')
        print('fileName : ', fileName)

        jsonArray = glob.glob('data/weather/*.json')
        while len(jsonArray) > 10:
            os.remove('{}'.format(jsonArray[0]))
            jsonArray = glob.glob('data/weather/*.json')

        with open('data/weather/{}.json'.format(fileName), "w") as outfile:
            outfile.write('{}'.format(jsonOutput))


# LED strip configuration:
LED_COUNT = 240        # Number of LED pixels.
LED_PIN = 18          # GPIO pin connected to the pixels (18 uses PWM!).
LED_COUNT_1 = 240        # Number of LED pixels.
LED_PIN_1 = 19          # GPIO pin connected to the pixels (18 uses PWM!).
LED_COUNT_2 = 120        # Number of LED pixels.
LED_PIN_2 = 18          # GPIO pin connected to the pixels (12 uses PWM!).
# LED_PIN = 10        # GPIO pin connected to the pixels (10 uses SPI /dev/spidev0.0).
LED_FREQ_HZ = 800000  # LED signal frequency in hertz (usually 800khz)
LED_DMA = 10          # DMA channel to use for generating signal (try 10)
LED_DMA_2 = 11          # DMA channel to use for generating signal (try 10)
LED_BRIGHTNESS = 255  # Set to 0 for darkest and 255 for brightest
LED_INVERT = False    # True to invert the signal (when using NPN transistor level shift)
LED_CHANNEL = 0      # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_CHANNEL_1 = 1      # set to '1' for GPIOs 13, 19, 41, 45 or 53
LED_CHANNEL_2 = 0      # set to '1' for GPIOs 13, 19, 41, 45 or 53

def doubleColorWipe(stripArray, colorArray, wait_ms=50):
    [strip240, strip120] = stripArray
    [R1, G1, B1, R2, G2, B2] = colorArray

    colorTemp1 = Color(R1, G1, B1)
    colorTemp2 = Color(R2, G2, B2)
    # inverseColorTemp = Color(255-R, G, B)
    for i in range(strip120.numPixels()):

        strip120.setPixelColor(i, colorTemp1)
            # print('in colorWipe with i : ', i)
            # print('and color : ', color)
            # print('and strip.numPixels() : ', strip.numPixels())
        strip240.setPixelColor(i, colorTemp2)
        strip240.setPixelColor(strip240.numPixels()-i, colorTemp2)
        strip120.show()
        strip240.show()
        if (wait_ms > 0): time.sleep(wait_ms / 1000.0)

def colorWipe(strip, color, wait_ms=50):
# Define functions which animate LEDs in various ways.
    """Wipe color across display a pixel at a time."""

    inverse = randrange(2)

    # OK print('inverse : ', inverse)
    for i in range(strip.numPixels()+1):
        # print('in colorWipe with i : ', i)
        # print('and color : ', color)
        # print('and strip.numPixels() : ', strip.numPixels())
        if inverse > 0: 
            strip.setPixelColor(strip.numPixels()-i, color)
            # print('in colorWipe with strip.numPixels()-i : ', strip.numPixels()-i)
            # if i == strip.numPixels()-1:
            #     strip.setPixelColor(0, color)
        else: strip.setPixelColor(i, color)
        strip.show()
        if (wait_ms > 0): time.sleep(wait_ms / 1000.0)


def theaterChase(strip, color, wait_ms=500, iterations=5):
    """Movie theater light style chaser animation."""
    for j in range(iterations):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, color)
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


def wheel(pos):
    """Generate rainbow colors across 0-255 positions."""
    if pos < 85:
        return Color(pos * 3, 255 - pos * 3, 0)
    elif pos < 170:
        pos -= 85
        return Color(255 - pos * 3, 0, pos * 3)
    else:
        pos -= 170
        return Color(0, pos * 3, 255 - pos * 3)


def rainbow(strip, wait_ms=500, iterations=1):
    """Draw rainbow that fades across all pixels at once."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel((i + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def rainbowCycle(strip, wait_ms=500, iterations=5):
    """Draw rainbow that uniformly distributes itself across all pixels."""
    for j in range(256 * iterations):
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, wheel(
                (int(i * 256 / strip.numPixels()) + j) & 255))
        strip.show()
        time.sleep(wait_ms / 1000.0)


def theaterChaseRainbow(strip, wait_ms=100):
    """Rainbow movie theater light style chaser animation."""
    for j in range(256):
        for q in range(3):
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, wheel((i + j) % 255))
            strip.show()
            time.sleep(wait_ms / 1000.0)
            for i in range(0, strip.numPixels(), 3):
                strip.setPixelColor(i + q, 0)


# Main program logic follows:
if __name__ == '__main__':
    # Process arguments


  # see https://stackoverflow.com/questions/45600579/asyncio-event-loop-is-closed-when-getting-loop
    # for more details
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(getweather(saveJson=True))
    asyncio.run(getRatpData(saveJson=True))
    

    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='clear the display on exit')
    args = parser.parse_args()
    # Create NeoPixel object with appropriate configuration.
    strip240 = PixelStrip(LED_COUNT_1, LED_PIN_1, LED_FREQ_HZ, LED_DMA, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL_1)
    strip120 = PixelStrip(LED_COUNT_2, LED_PIN_2, LED_FREQ_HZ, LED_DMA_2, LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL_2)
    # Intialize the library (must be called once before other functions).
    strip240.begin()
    strip120.begin()

    print('Press Ctrl-C to quit.')
    if not args.clear:
        print('Use "-c" argument to clear LEDs on exit')

    try:

        while True:
            print('Color wipe animations.')

            # colorWipe(strip240, Color(0, 255, 0))  # Green wipe
            # colorWipe(strip240, Color(0, 0, 255))  # Blue wipe

            # print(randrange(255))
            R = randrange(255)
            G = randrange(255)
            B = randrange(255)

            print(' => RandomColor : (', R, ', ', G, ', ', B, ')')
            colorTemp = Color(R, G, B)

            doubleColorWipe([strip240, strip120], [R, G, B, int((R+G+B)/765), G, 255], 50)  # Random wipe

            """colorWipe(strip240, Color(255-R, G, B), 5)  # Random wipe
            colorWipe(strip120, Color(R, 255-G, B), 5)  # Random wipe
            colorWipe(strip240, Color(255-R, G, 255-B), 5)  # Random wipe
            colorWipe(strip120, Color(R, 255-G, 255-B), 5)  # Random wipe
            colorWipe(strip240, Color(255-R, 255-G, B), 5)  # Random wipe
            colorWipe(strip120, Color(R, 255-G, B), 5)  # Random wipe
            colorWipe(strip240, Color(255-R, 255-G, 255-B), 5)  # Random wipe"""

            # tempBrightnessPercent = randrange(255)
            # print('Random Brightness : ', tempBrightnessPercent)

            # colorWipe(strip120, Color(0, 255, 0))  # Green wipe
            # colorWipe(strip120, Color(0, 255, 0))  # Green wipe

            # colorWipe(strip120, Color(tempBrightnessPercent, tempBrightnessPercent, tempBrightnessPercent), 1)  # White wipe
            # colorWipe(strip240, Color(tempBrightnessPercent, tempBrightnessPercent, tempBrightnessPercent), 1)  # White wipe

            colorWipe(strip120, Color(0, 0, 0), 0)  # Black wipe
            colorWipe(strip240, Color(0, 0, 0), 0)  # Black wipe

            # print('Theater chase animations.')
            # theaterChase(strip, Color(127, 127, 127))  # White theater chase
            # theaterChase(strip, Color(127, 0, 0))  # Red theater chase
            # theaterChase(strip120, Color(127, 0, 0))  # Red theater chase
            # theaterChase(strip, Color(0, 0, 127))  # Blue theater chase
            # theaterChase(strip240, Color(0, 0, 127))  # Blue theater chase

            # print('Rainbow animations.')
            # rainbow(strip)
            # rainbowCycle(strip120)
            # rainbowCycle(strip240)
            # theaterChaseRainbow(strip120)
            # theaterChaseRainbow(strip240)

    except KeyboardInterrupt:
        colorWipe(strip120, Color(0, 0, 0), 10)
        colorWipe(strip240, Color(0, 0, 0), 10)

print('Script has ended. Good night !')
