#!/usr/bin/python
# import syslog
import time
import math
import serial
import matplotlib.pyplot as plt
import random
import serial.tools.list_ports as port_list
import cv2
import numpy as np
import json
import datetime
import string
import glob
import os

print('Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))

import settings
# pathRef = os.getenv("pathRef")
# printLogs = os.getenv("printLogs")
# readyToPlot = os.getenv("readyToPlot")
# forceAnglesToInt = os.getenv("forceAnglesToInt")
# coordToPlot = os.getenv("coordToPlot")
# windowSize = os.getenv("windowSize")
# diameter = os.getenv("diameter")
# previousAngles = os.getenv("previousAngles")

pathRef = '.'
printLogs = False
readyToPlot = False
forceAnglesToInt = True
coordToPlot = []
windowSize = [600, 600]
diameter = 60
previousAngles = []


ports = list(port_list.comports())
print("Available ports :")
for p in ports:
    print(p)

d1 = float(15)
d2 = float(15)
currentA = 0
currentB = 0

def writeArduino(tempX, tempY):
    #The following line is for serial over GPIO
    port = 'COM3'


    ard = serial.Serial(port,9600,timeout=5)

    i = 0
    running = True
    while running:
        # Serial write section
        setTemp1 = "A{}:B{}".format(tempX+i, tempY+i)
        print("Python value sent: ")
        print(setTemp1)
        ard.write(setTemp1.encode())
        time.sleep(0.5)  # with the port open, the response will be buffered
        # so wait a bit longer for response here

        # Serial read section
        msg = ard.read(ard.inWaiting())  # read everything in the input buffer
        print("Message from arduino: ")
        print(msg)
        i+=5
        i=i%185

    print ("Exiting")
    exit()

def doRandomCircles():
    index = 0
    while index < 33:
        x = random.randint(-30,30)
        y = random.randint(-30,30)
        if x**2 + y**2 > 30**2:
            continue

        index += 1
        print("Random position : ({}, {})".format(x, y))

        plotCircles(x, y)

def calculateAnglesNative(xAinput, yAinput):
    global previousAngles
    xA = float(xAinput)
    yA = float(yAinput)

    print("\nCalculating angles for ({}, {})".format(xA, yA))
    print('distance is : {}'.format(math.sqrt(xA**2+yA**2)))
    if xA ** 2 + yA ** 2 > (diameter / 2) ** 2:
        print('2. Too far out : Need to put on circle')
        print('Converting {}'.format([xA, yA]))
        theta = math.acos(xA / math.sqrt(xA ** 2 + yA ** 2))
        print('theta : {}'.format(theta))
        # theta = math.radians(theta)
        # print('theta as radian : {}'.format(theta))
        xA = (diameter / 2) * math.cos(theta)

        positiveY = False
        if (yA > 0):
            positiveY = True
        yA = (diameter / 2) * math.sin(theta)
        if (yA > 0 and not positiveY):
            yA = -yA
        # yA = windowSize[1]-(maxRadius / 2) * math.sin(theta)
        print('new (xA,yA) : {}'.format([xA, yA]))


    if xA == 0 and yA == 0:
        if previousAngles == []:
            return [(180, 0), (0, 180)]
        else:
            [(alpha1, beta1), (alpha2, beta2)] = previousAngles

            return [(alpha1, 180), (alpha2, 180)]

    vCa = (xA**2+yA**2+d1**2-d2**2)/2.0
    vA = xA**2+yA**2
    vB = -2.0*yA*vCa
    vC = (vCa**2)-(xA**2)*(d1**2)

    if printLogs: print("vA, vB, vC = ({}, {}, {})".format(vA, vB, vC))
    discri = vB**2-4*vA*vC
    if printLogs: print("discri = {}".format(discri))

    if discri<0:
        discri=0

    y1 = (-vB - math.sqrt(discri))/(2*vA)
    y2 = (-vB + math.sqrt(discri))/(2*vA)
    if printLogs: print("0 current : (y1,y2) = ({}, {})".format(y1, y2))
    if ((y1 > d1 and y1 - 0.001 > d1) or (y1 < -d1 and y1 + 0.001 < d1)):
        y1 = d1*(math.fabs(y1)/y1)
    if ((y2 > d1 and y1 - 0.001 > d1) or (y2 < -d1 and y2 + 0.001 < d1)):
        y2 = d1 * (math.fabs(y2) / y2)
    if printLogs: print("0 : (y1,y2) = ({}, {})".format(y1, y2))
    x1 = math.sqrt(d1**2-y1**2)
    x2 = math.sqrt(d1**2-y2**2)
    if printLogs: print("0 current : (x1,x2) = ({}, {})".format(x1, x2))
    if ((x1 > d1 and x1 - 0.001 > d1) or (x1 < -d1 and x1 + 0.001 < d1)):
        x1 = d1*(math.fabs(x1)/x1)
    if ((x2 > d1 and x1 - 0.001 > d1) or (x2 < -d1 and x2 + 0.001 < d1)):
        x2 = d1 * (math.fabs(x2) / x2)

    if printLogs: print("0 : (x1,x2) = ({}, {})".format(x1, x2))
    switchX1 = False
    if (discri==0):
        if printLogs: print('   !  ')
        if printLogs: print('discri = 0, switching x1, maybe ? ')
        x1 = -x1
        switchX1 = True
    if printLogs: print("INITIAL X, Y spots are : ")
    # x1 = math.ceil(x1)
    # x2 = math.ceil(x2)
    if printLogs: print("1 : (x1,y1) = ({}, {})".format(x1, y1))
    if printLogs: print("2 : (x2,y2) = ({}, {})".format(x2, y2))
    if printLogs: print("(x1-xA)**2+(y1-yA)**2 = {}".format((x1-xA)**2+(y1-yA)**2))
    if ((x1-xA)**2+(y1-yA)**2<d2**2-1 or (x1-xA)**2+(y1-yA)**2>d2**2+1):
        if printLogs: print('switching x1   (* -1)')
        x1=-x1
    if ((x2-xA)**2+(y2-yA)**2<d2**2-1 or (x2-xA)**2+(y2-yA)**2>d2**2+1):
        if printLogs: print('switching x2   (* -1)')
        x2=-x2
    # y2 = (vA1 - x2*vD)
    #
    # if (xAinput < 0):
    #     # x1 = - x1
    #     x2 = - x2

    # if (yAinput < 0):
    #     y1 = - y1
    if printLogs:
        print("Possible x1, y1 spots are : ")
        print("1 : ({}, {})".format(x1, y1))
        print("2 : ({}, {})".format(x2, y2))

    alpha1 = math.asin(y1/d1)*180.0/math.pi
    alpha2 = math.asin(y2/d1)*180.0/math.pi
    if printLogs:
        print("INITIAL ALPHAS : ")
        print("alpha1 : {}".format(alpha1))
        print("alpha2 : {}".format(alpha2))
    switchAlpha1 = False
    if (x1 < 0):
        if printLogs:
            print("  !  ")
            print("x1 < 0 : {} < {}".format(x1, 0))
            print("alpha1 goes from {} to {}".format(alpha1, 180 - alpha1))
        alpha1 = 180 - alpha1
        switchAlpha1 = True
    switchAlpha2 = False
    if (x2 < 0):
        if printLogs:
            print("  !  ")
            print("x2 < 0 : {} < {}".format(x2, 0))
            print("alpha1 goes from {} to {}".format(alpha2, 180 - alpha2))
        alpha2 = 180 - alpha2
        switchAlpha2 = True
    if printLogs:
        print("POST FORMAT! ALPHAS : ")
        print("alpha1 : {}".format(alpha1))
        print("alpha2 : {}".format(alpha2))

    # print("(yA - y1)/d2 = {}".format((yA - y1)/d2))
    # print("yA = {}".format(yA))
    # print("y1 = {}".format(y1))
    # print("y2 = {}".format(y2))
    # print("(yA - y2)/d2 = {}".format((yA - y2)/d2))
    if (((yA - y1)/d2) > 1) or ((yA - y1)/d2 < -1):
        # y1 = d1*(math.fabs(((yA - y1)/d2)/((yA - y1)/d2)))
        y2 = d2*(math.fabs(y1)/y1)
    if (((yA - y2)/d2) > 1) or ((yA - y2)/d2 < -1):
        y2 = d2*(math.fabs(y2)/y2)
        # y2 = d1 * (math.fabs(y2) / y2)

    # yA = y1 + d2sin(b)
    beta1 = math.asin((yA - y1)/d2)*180.0/math.pi
    beta2 = math.asin((yA - y2)/d2)*180.0/math.pi

    if printLogs:
        print("INITIAL BETAS : ")
        print("beta1 : {}".format(beta1))
        print("beta2 : {}".format(beta2))

    # if (yAinput < 0):
    #     alpha1 = 180 - alpha1
    #     beta1 = 180 - beta1
    #
    if printLogs:
        print("xA : {}    ;    x2 : {}".format(xA, x2))
        print("yA : {}    ;    y2 : {}".format(yA, y2))
    if ((yA > y1 and xA < x1) or switchAlpha2):
        if printLogs:
            print("  !  ")
            print("switchAlpha2 : {}".format(switchAlpha2))
            print("xA < x1 : {} > {}".format(xA, x2))
            print("yA > y2 : {} > {}".format(yA, y2))
            print("beta1 goes from {} to {}".format(beta1, 180 - beta1))
        beta1 = 180 - beta1
    if (xA < x2):
        if printLogs:
            print("  !  ")
            print("xA < x2 : {} < {}".format(xA, x2))
            print("beta2 goes from {} to {}".format(beta2, 180 - beta2))
        beta2 = 180 - beta2
    #####

    print("Possible angles are : ")
    print("1 : ({}, {})".format(alpha1, beta1))
    print("2 : ({}, {})".format(alpha2, beta2))

    previousAngles = [(alpha1, beta1), (alpha2, beta2)]

    return [(alpha1, beta1), (alpha2, beta2)]


def plotCircles(img2, xA, yA, distance=0):
    if printLogs: print('In plotCircles with xA, yA = ({},{})'.format(xA, yA))

    cv2.circle(img2, (int(windowSize[0] / 2), int(windowSize[1] / 2)), radius=int(windowSize[0] / 2),
               color=(255, 255, 255), thickness=1)

    # cv2.circle(img2, convertPlotToWindow((xA, yA)), radius=int(d1*windowSize[0]/30), color=(0, 255, 0), thickness=1)
    if distance != 0:
        tempColor = int(255 * (min(2 * distance, diameter) / diameter))
        # print('TempColor : {}'.format(tempColor))
        cv2.circle(img2, convertPlotToWindow((xA, yA)), radius=3, color=(255-tempColor, 0, tempColor), thickness=1)
    else:
        cv2.circle(img2, convertPlotToWindow((xA, yA)), radius=3, color=(255, 0, 0), thickness=1)

    img3 = img2.copy()

    [(alpha1, beta1), (alpha2, beta2)] = calculateAnglesNative(xA, yA)

    if forceAnglesToInt:
        alpha1 = int(alpha1)
        beta1 = int(beta1)
        alpha2 = int(alpha2)
        beta2 = int(beta2)

    # find the end point
    endyA1 = d1 * math.sin(math.radians(alpha1))
    endxA1 = d1 * math.cos(math.radians(alpha1))

    # ax.plot([0, endxA1], [0, endyA1], color='orange')
    # convertedCoordX = convertPlotToWindow((0, endxA1))
    # convertedCoordY = convertPlotToWindow((0, endyA1))
    convertedCoordX = convertPlotToWindow((0, 0))
    convertedCoordY = convertPlotToWindow((endxA1, endyA1))
    # print('\n orange (first branch for first option) : ')
    # print('convertedCoordX = {}'.format(convertedCoordX))
    # print('convertedCoordY = {}'.format(convertedCoordY))
    cv2.line(img3, convertedCoordX, convertedCoordY, color=(0, 165, 255), lineType=cv2.LINE_AA, thickness=3)
    # cv2.line(img2, (0, int(endxA1)), (0, int(endyA1)), color=(255, 165, 0), lineType=cv2.LINE_AA, thickness=1)
    if printLogs: print("plotted 0 -> A1 in orange : ({}, {})".format(endxA1, endyA1))

    endyA2 = d1 * math.sin(math.radians(alpha2))
    endxA2 = d1 * math.cos(math.radians(alpha2))

    # ax.plot([0, endxA2], [0, endyA2], color='brown')  # GOOD !
    # convertedCoordX = convertPlotToWindow((0, endxA2))
    convertedCoordX = convertPlotToWindow((0, 0))
    convertedCoordY = convertPlotToWindow((endxA2, endyA2))
    # print('\n brown (first branch for second option) : ')
    # print('convertedCoordX = {}'.format(convertedCoordX))
    # print('convertedCoordY = {}'.format(convertedCoordY))
    cv2.line(img3, convertedCoordX, convertedCoordY, color=(42, 42, 165), lineType=cv2.LINE_AA, thickness=3)
    if printLogs: print("plotted 0 -> A2 in brown : ({}, {})".format(endxA2, endyA2))

    endyB1 = endyA1 + d2 * math.sin(math.radians(beta1))
    endxB1 = endxA1 + d2 * math.cos(math.radians(beta1))

    # ax.plot([endxA1, endxB1], [endyA1, endyB1], color='red')  # GOOD AGAIN WITH surprise
    # convertedCoordX = convertPlotToWindow((endxA1, endxB1))
    # convertedCoordY = convertPlotToWindow((endyA1, endyB1))
    convertedCoordX = convertPlotToWindow((endxA1, endyA1))
    convertedCoordY = convertPlotToWindow((endxB1, endyB1))
    # print('\n red (second branch for first option) : ')
    # print('convertedCoordX = {}'.format(convertedCoordX))
    # print('convertedCoordY = {}'.format(convertedCoordY))
    cv2.line(img3, convertedCoordX, convertedCoordY, color=(0, 0, 255), lineType=cv2.LINE_AA, thickness=3)
    if printLogs: print("plotted A1 -> B1 in red : ({}, {})".format(endxB1, endyB1))

    endyB2 = endyA2 + d2 * math.sin(math.radians(beta2))
    endxB2 = endxA2 + d2 * math.cos(math.radians(beta2))

    # print("beta2 : {}".format(beta2))
    # print("endxB2 : {}".format(endxB2))

    # ax.plot([endxA2, endxB2], [endyA2, endyB2], color='magenta')
    # convertedCoordX = convertPlotToWindow((endxA2, endxB2))
    # convertedCoordY = convertPlotToWindow((endyA2, endyB2))
    convertedCoordX = convertPlotToWindow((endxA2, endyA2))
    convertedCoordY = convertPlotToWindow((endxB2, endyB2))
    # print('\n magenta (second branch for second option) : ')
    # print('convertedCoordX = {}'.format(convertedCoordX))
    # print('convertedCoordY = {}'.format(convertedCoordY))
    cv2.line(img3, convertedCoordX, convertedCoordY, color=(255, 0, 255), lineType=cv2.LINE_AA, thickness=3)
    if printLogs: print("plotted A2 -> B2 in magenta : ({}, {})".format(endxB2, endyB2))

    # potting the points
    # plt.plot(x, y)

    # function to show the plot
    # plt.show()
    # plt.show(block=False)
    # plt.pause(1)
    # plt.close()
    cv2.imshow('test plotting', img3)
    if cv2.waitKey(1) & 0xFF == 27:
        print('breaking due to .waitKey! (409)')
    if printLogs: print('plotting img2 and sleeping')
    time.sleep(0.05)



# print("Writing to Arduino :")
# writeArduino(0, 0)


# plotCircles(-15, 15)
# plotCircles(-15, -15)
# plotCircles(15, -15)
#
#
# plotCircles(0, 30)
# plotCircles(30, 0)
# plotCircles(-30, 0)
# plotCircles(0, -30)
#
# plotCircles(0, 20)
# plotCircles(20, 0)
# plotCircles(-20, 0)
# plotCircles(0, -20)

def plotLine(img2, xA, yA, xB, yB, withIndex=False):
    if printLogs: print('Plotting line for ({},{}) -> ({},{})'.format(xA, yA, xB, yB))

    distance = math.sqrt((xB-xA)**2+(yB-yA)**2)
    if printLogs: print('distance : {}'.format(distance))
    if distance > 1:
        if printLogs: print('switching to >withIndex<')
        withIndex = True

    if withIndex:
        deltaX = xB - xA
        deltaY = yB - yA

        index = 0

        while index < 1:
            xP = xA + deltaX*index
            yP = yA + deltaY*index
            plotCircles(img2, xP, yP, distance)
            index += 1/(2*distance)
    else:
        plotCircles(img2, xA, yA)

def plotArc(xA, yA, xB, yB, arc):

    print('Plotting arc for ({},{}) -> ({},{})  &  arc = {}'.format(xA, yA, xB, yB, arc))

def convertWindowToPlot(coord):
    # if printLogs:
    print('In convertWindowToPlot for {}'.format(coord))
    # coord = [[pt1_x, pt1_y], [x, y]]
    try:
        [[xA, yA], [xB, yB]] = coord
        xA = (xA - windowSize[0] / 2) * diameter / windowSize[0]
        xB = (xB - windowSize[0] / 2) * diameter / windowSize[0]
        yA = (windowSize[1] / 2 - yA) * diameter / windowSize[1]
        yB = (windowSize[1] / 2 - yB) * diameter / windowSize[1]

        if printLogs: print('adding this to coord to plot : {}'.format([[xA, yA], [xB, yB]]))

        return [[xA, yA], [xB, yB]]
    except Exception as e:
        # print("Exception during conversion, doing the simple one")
        # print(e)
        (xA, yA) = coord
        xA = (xA - windowSize[0] / 2) * diameter / windowSize[0]
        yA = (windowSize[1] / 2 - yA) * diameter / windowSize[1]

        if xA**2+yA**2 > (diameter / 2)**2:
            print('Too far out : Need to put on circle')
            print('Converting {}'.format([xA, yA]))
            theta = math.acos(xA / math.sqrt(xA**2 + yA**2))
            print('theta : {}'.format(theta))
            # theta = math.radians(theta)
            # print('theta as radian : {}'.format(theta))
            xA = (diameter / 2) * math.cos(theta)
            positiveY = False
            if (yA > 0):
                positiveY = True
            yA = (diameter / 2) * math.sin(theta)
            if (yA > 0 and not positiveY):
                yA = -yA
            print('new (xA,yA) : {}'.format([xA, yA]))

        print('adding this to coord to plot : {}'.format([xA, yA]))
        # if printLogs: print('adding this to coord to plot : {}'.format([xA, yA]))

        return [xA, yA]


def convertPlotToWindow(coord):
    # print('In convertPlotToWindow for {}'.format(coord))
    # coord = [[pt1_x, pt1_y], [x, y]]
    (xA, yA) = coord
    xA = int((xA * windowSize[0] / diameter) + windowSize[0] / 2)
    yA = int(windowSize[1] / 2 - (yA * windowSize[1] / diameter))

    # print('this is the new coord : ({}, {})'.format(xA, yA))

    return (xA, yA)


def sketchPlot(letter='', readFromFile='', plottingInput=False):
    print('In sketchPlot with letter : {}, readFromFile : {}, plottingInput : {}'.format(letter, readFromFile, plottingInput))

    global coordToPlot
    global plotLetter
    global readyToPlot
    global plotting
    global letterTemp

    plotting = plottingInput
    plotLetter = (letter != '')
    print('In sketchPlot with letter : {} & readFromFile : {} & plotting/plottingInput : {} & plotLetter : {}'.format(letter, readFromFile, plotting, plotLetter))


    def draw_circle():
        cv2.circle(img, (int(windowSize[0] / 2), int(windowSize[1] / 2)), radius=int(windowSize[0] / 2),
                   color=(255, 255, 255), thickness=1)

    def draw_grid(line_color=(255, 255, 255), thickness=1, type_=cv2.LINE_AA, pxstep=50):
        '''(ndarray, 3-tuple, int, int) -> void
        draw gridlines on img
        line_color:
            BGR representation of colour
        thickness:
            line thickness
        type:
            8, 4 or cv2.LINE_AA
        pxstep:
            grid line frequency in pixels
        '''
        x = pxstep
        y = pxstep
        #    (x-300)**2+(y-300)**2 = (windowSize[0]/2)**2
        #        x = 300 +- math.sqrt((windowSize[0]/2)**2 - (y-300)**2)
        #        y = 300 +- math.sqrt((windowSize[0]/2)**2 - (x-300)**2)
        while x < img.shape[1]:
            # print("x coord : {} , {}".format((x, int(img.shape[1]/2 + math.sqrt((img.shape[1] / 2) ** 2 - (x-img.shape[1]/2) ** 2))),
            #                                  (x, img.shape[0] - int(img.shape[1]/2 + math.sqrt((img.shape[1] / 2) ** 2 - (x-img.shape[1]/2) ** 2)))))
            cv2.line(img, (x, int(img.shape[1] / 2 + math.sqrt((img.shape[1] / 2) ** 2 - (x - img.shape[1] / 2) ** 2))),
                     (x, img.shape[0] - int(
                         img.shape[1] / 2 + math.sqrt((img.shape[1] / 2) ** 2 - (x - img.shape[1] / 2) ** 2))),
                     color=line_color, lineType=type_, thickness=thickness)
            x += pxstep

        while y < img.shape[0]:
            # print("y coord : {} , {}".format((int(img.shape[0]/2 + math.sqrt((img.shape[0]/2)**2 - (y-img.shape[0]/2)**2)), y), (img.shape[1]-int(img.shape[0]/2 + math.sqrt((img.shape[0]/2)**2 - (y-img.shape[0]/2)**2)), y)))
            cv2.line(img, (int(img.shape[0] / 2 + math.sqrt((img.shape[0] / 2) ** 2 - (y - img.shape[0] / 2) ** 2)), y),
                     (img.shape[1] - int(
                         img.shape[0] / 2 + math.sqrt((img.shape[0] / 2) ** 2 - (y - img.shape[0] / 2) ** 2)), y),
                     color=line_color, lineType=type_, thickness=thickness)
            y += pxstep

        # old :
        # while x < img.shape[1]:
        #     cv2.line(img, (x, 0), (x, img.shape[0]), color=line_color, lineType=type_, thickness=thickness)
        #     x += pxstep
        #
        # while y < img.shape[0]:
        #     cv2.line(img, (0, y), (img.shape[1], y), color=line_color, lineType=type_, thickness=thickness)
        #     y += pxstep

    # mouse callback function
    def line_drawing(event, x, y, flags, param):
        global pt1_x, pt1_y, drawing, coordToPlot, readyToPlot, outOfBorder

        if event == cv2.EVENT_LBUTTONDOWN:

            if (x - windowSize[0] / 2) ** 2 + (y - windowSize[0] / 2) ** 2 > (windowSize[0] / 2) ** 2:
                if printLogs: print(' !! 1. OUT OF BORDERS !!')
                # print(' x = {}'.format(x))
                # print(' y = {}'.format(y))
                # print(' windowSize = {}'.format(windowSize))
                outOfBorder = True
                drawing = False
            else:
                drawing = True
                outOfBorder = False
                pt1_x, pt1_y = x, y

        elif event == cv2.EVENT_MOUSEMOVE:
            try:
                if (x - windowSize[0] / 2) ** 2 + (y - windowSize[0] / 2) ** 2 > (windowSize[0] / 2) ** 2:
                    if printLogs: print(' !! 1. OUT OF BORDERS !!')
                    # print(' x = {}'.format(x))
                    # print(' y = {}'.format(y))
                    # print(' windowSize = {}'.format(windowSize))
                    outOfBorder = True
                    drawing = False
                else:
                    drawing = True
                    outOfBorder = False

                if drawing == True:
                    cv2.line(img, (pt1_x, pt1_y), (x, y), color=(255, 255, 255), thickness=2)
                    coordToPlot.append(convertWindowToPlot([[pt1_x, pt1_y], [x, y]]))
                    # coordToPlot.append([[pt1_x, pt1_y], [x, y]])
                    pt1_x, pt1_y = x, y
            except:
                pass
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            if (x - windowSize[0] / 2) ** 2 + (y - windowSize[0] / 2) ** 2 > (windowSize[0] / 2) ** 2:
                if printLogs: print(' !! 2. OUT OF BORDERS !!')
                outOfBorder = True
            else:
                cv2.line(img, (pt1_x, pt1_y), (x, y), color=(255, 255, 255), thickness=2)

        elif event == cv2.EVENT_RBUTTONDOWN:
            drawing = False
            if printLogs: print('pressed right click')
            readyToPlot = True
            return True

    def startPlotting(coordToPlot = [], plotLetter = ''):
        readyToPlot = False
        print("READY TO START PLOTTING !")
        print('coordToPlot = {}'.format(coordToPlot))
        print('plotLetter = {}'.format(plotLetter))

        jsonToSave = {}
        if coordToPlot != []:
            jsonToSave['coords'] = coordToPlot

        if plotLetter != '':
            coordPlotName = pathRef+'/coordToPlot_{}.json'.format(plotLetter)
            print('\nPlease draw letter : {}'.format(plotLetter))
            return sketchPlot(letter=plotLetter, plottingInput=True)
        else:
            coordPlotName = pathRef+'/coordToPlot/coordToPlot_{:%Y-%m-%d_%H:%M:%S}.json'.format(datetime.datetime.now()).replace(
                ':', '-')
        print('coordPlotName = {}'.format(coordPlotName))

        # print('Timestamp: {:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now()))
        coordPlotName = coordPlotName.replace('C-/Users/', 'C:/Users/')
        with open(coordPlotName, 'w') as fileWriter:
            json.dump(jsonToSave, fileWriter)
        # fileWriter.write(jsonToSave)

        # img2 = np.zeros((windowSize[0], windowSize[1], 1), np.uint8)
        img2 = cv2.imread("background_drawing.PNG", cv2.IMREAD_COLOR)

        cv2.namedWindow('test plotting')
        cv2.imshow('test plotting', img2)
        if cv2.waitKey(1) & 0xFF == 27:
            print('breaking due to .waitKey!')

        for doubleCoordTemp in coordToPlot:
            A = doubleCoordTemp[0]
            B = doubleCoordTemp[1]
            print('\n\nDrawing line from {} to {}'.format(A, B))
            plotLine(img2, A[0], A[1], B[0], B[1])

        print("\n\nALL DONE ! Time to sleep now. Launch me back when you're ready.")
        if plotLetter:
            while True:
                # cv2.imshow('test draw', img)
                cv2.imshow('test plotting', img2)
                time.sleep(1)
        else:
            # cv2.destroyAllWindows()
            time.sleep(5)
            plotLetter = False

    def main(coordToPlot=[], plotLetter=''):
        startPlotting(coordToPlot, plotLetter)


    if (letter != '' and plotting):
        plotLetter = letter
        print("Please draw symbol for char : {}".format(letter))
        try:
            readFromFile = pathRef+'/coordToPlot/coordToPlot_{}.json'.format(letter)
            with open(readFromFile, 'r') as fileReader:
                print('found it : ')
                print(fileReader.read())
                return
        except:
            print("couldn't find it, starting to plot")
            # startPlotting(plotLetter=letter)
    # elif (letter == '' and readFromFile == '') or (letter != '' and plotting):
    #     if readFromFile == '' and not plotLetter:

    # else:
    # with open(readFromFile, 'r') as fileReader:
    print('this is readFromFile : {}'.format(readFromFile))
    if readFromFile != '':
        print(' this is coordToPlot : {}'.format(coordToPlot))
        try:
            if readFromFile.index('.json') > -1 and coordToPlot == []:
                inputFile = open(readFromFile, 'r')
                # with open(readFromFile, 'w') as fileWriter:
                #     json.dump(coordToPlot, fileWriter)
                coordToPlot = json.load(inputFile)
                coordToPlot = coordToPlot['coords']
                print('Loaded coordToPlot : {}'.format(coordToPlot))
                # print('Ready to start plotting with coordToPlot : {}'.format(coordToPlot))
                startPlotting(coordToPlot=coordToPlot)
                readFromFile = ''
                coordToPlot = []

                # cv2.destroyAllWindows()
                print('DONE 1')
                return True
            else:
                if plotLetter != '':
                    print("couldn't find the file, ready to start plotting for letter {}".format(letter))

                    startPlotting(plotLetter=letter)
                    # sketchPlot(letter='', readFromFile='', plottingInput=False)
        except Exception as e:
            print('EXCEPTION AS E : {}'.format(e))
            coordToPlot = []
            plotLetter = False
            readyToPlot = False
            plotting = False
            # plotting = plottingInput
            # plotLetter = (letter != '')
            return False

            # inputFile = open(readFromFile, 'w')
            # coordToPlot = json.dump(coordToPlot)
            coordToSave = {}
            coordToSave['coords'] = coordToPlot
            print('Saving coordToPlot : {}'.format(coordToSave))

            startPlotting(coordToPlot=coordToSave)
            readFromFile = ''
            coordToPlot = []

            print('DONE 2')
            # cv2.destroyAllWindows()
            # inputFile.write(coordToPlot)

            try:
                with open(readFromFile, 'w') as fileWriter:
                    json.dump(coordToSave, fileWriter)
            except Exception as e:
                fileOutput = pathRef+'/{}'.format(readFromFile)
                with open(fileOutput, 'w') as fileWriter:
                    json.dump(coordToSave, fileWriter)

            # startPlotting(coordToPlot)
            pass
    else:

        img = np.zeros((windowSize[0], windowSize[1], 1), np.uint8)

        drawing = False  # true if mouse is pressed
        outOfBorder = False  # true if mouse is outside of circle
        pt1_x, pt1_y = None, None
        print('doing the test draw window')

        cv2.namedWindow('test draw')

        cv2.setMouseCallback('test draw', line_drawing)
        draw_circle()
        draw_grid()

        cv2.imwrite('background_drawing.PNG', img)

        while not readyToPlot:
            cv2.imshow('test draw', img)
            if cv2.waitKey(1) & 0xFF == 27:
                readyToPlot = False
                coordToPlot = []

                break
        # cv2.destroyAllWindows()

        # startPlotting(coordToPlot, letter)

        startPlotting(coordToPlot=coordToPlot)


def getPointFromNumpyArray(input):
    print('in getPointFromNumpyArray for {}'.format(input))
    firstPoint = '{}'.format(input).replace('   ', ' ').replace('  ', ' ').replace('"', '').replace('[ ', '').replace('[', '').replace(']','').split(' ')

    print('firstPoint post replace {}'.format(firstPoint))
    try:
        firstPoint[0] = int(firstPoint[0])
        firstPoint[1] = int(firstPoint[1])
    except Exception as e:
        print('Exception during encapsulation...')
        print(e)
        print(firstPoint)
        print('{}'.format(input))
        firstPoint = [42, 33]
        pass

    print('firstPoint post encapsulation int() {}'.format(firstPoint))
    # firstPoint = convertPlotToWindow((firstPoint[0], firstPoint[1]))
    firstPoint = convertWindowToPlot((firstPoint[0], firstPoint[1]))

    print('firstPoint post convertWindowToPlot {}'.format(firstPoint))

    return firstPoint

def getCoordsFromPicture(pictureFile, showContour=False):
    # Read the image and create a blank mask
    img = cv2.imread(pictureFile)
    img = cv2.resize(img, (windowSize[0],windowSize[1]), interpolation=cv2.INTER_AREA)
    # img = cv2.resize(img, (400,400), interpolation=cv2.INTER_AREA)
    h, w = img.shape[:2]
    mask = np.zeros((h, w), np.uint8)

    # Transform to gray colorspace and threshold the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

    # Search for contours and select the biggest one and draw it on mask
    contours = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[0]
    cnt = max(contours, key=cv2.contourArea)
    print('cnt : {}'.format(contours))
    print('of type : {}'.format(type(contours[0])))
    print('of shape : {}'.format((contours[0].shape)))
    # with open('contour.txt', 'w') as fileWriter:

    (iMax,jMax,kMax) = contours[0].shape
    i=0
    jsonTemp = {}
    jsonTemp['coords'] = []
    while i<iMax:
        # while j<jMax:
            # fileWriter.write('{} '.format(contours[0][i,j]))
        # firstPoint = '{}'.format(contours[0][i,0]).replace('  ', ' ').replace('"', '').replace('[', '').replace(']', '').split(' ')
        # firstPoint[0] = int(firstPoint[0])
        # firstPoint[1] = int(firstPoint[1])
        firstPoint = getPointFromNumpyArray(contours[0][i,0])
        try:
            # secondPoint = '{}'.format(contours[0][i+1,0]).replace('  ', ' ').replace('"', '').replace('[', '').replace(']', '').split('  ')
            # secondPoint[0] = int(secondPoint[0])
            # secondPoint[1] = int(secondPoint[1])
            secondPoint = getPointFromNumpyArray(contours[0][i+1,0])
        except Exception as e:
            print("Exception when trying to get secondPoint")
            print(e)
            secondPoint = firstPoint
            pass
        # j+=1
        # fileWriter.write('\n')
        jsonTemp['coords'].append([firstPoint, secondPoint])
        i+=2
        # fileWriter.write('{}'.format(contours))

    pictureFileRename = pictureFile.replace('PICTURES/','').replace('.png','').replace('.PNG','').replace('.jpg', '')
    jsonName = pathRef+'/coordToPlotFromPicture_{}.json'.format(pictureFileRename)
    with open(jsonName, 'w') as fileWriter:
        json.dump(jsonTemp, fileWriter)

    if showContour:
        cv2.drawContours(mask, [cnt], 0, 255, -1)

        # Perform a bitwise operation
        res = cv2.bitwise_and(img, img, mask=mask)

        # Convert black pixels back to white
        black = np.where(res == 0)
        res[black[0], black[1], :] = [255, 255, 255]

        # Display the image
        cv2.imshow('img', res)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    # startPlotting()
    sketchPlot(readFromFile=jsonName)


def writeTextOnImage(text, imgFile):
    # Write some Text

    img = cv2.imread(imgFile)

    font = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 3
    fontColor = (0, 0, 0)
    lineType = 3
    offset = [int(img.shape[0]/2), int(img.shape[1]/2)]
    imgCenter = [img.shape[0] - offset[0], img.shape[1] - offset[1]]
    bottomLeftCornerOfText = (imgCenter[0] - int(len(text)*fontScale*7.5), imgCenter[1] + int(0.75*len(text)*fontScale))


    cv2.putText(img, text,
                bottomLeftCornerOfText,
                font,
                fontScale,
                fontColor,
                lineType)

    # Display the image
    cv2.imshow("img", img)

    # Save image
    cv2.imwrite("{}_out.png".format(imgFile.split('.')[0]), img)



# startPlotting('coordToPlot/coordToPlot_a.json')

# sketchPlot()
# getCoordsFromPicture('PICTURES/spirale.png')
# getCoordsFromPicture('PICTURES/star.png')
# getCoordsFromPicture('PICTURES/METEO.png', showContour=True)

# with picture & text :
# pictureName = 'PICTURES/white.png'
# writeTextOnImage('hello world', pictureName)
# getCoordsFromPicture(pictureName, showContour=False)


# numbers = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '-', '_', '!', ':', '?', '.']

def confPlotChars():
    print('in confPlotChars')
    fileList = []
    os.chdir(pathRef+'/coordToPlot/')
    for fileName in glob.glob('*'):
        print('found File : {}'.format(fileName))
        fileList.append(fileName)

    for letterTemp in string.ascii_lowercase:

        coordPlotName = 'coordToPlot_{}.json'.format(letterTemp)
        if coordPlotName not in fileList:
            print('letterTemp {} not in fileList'.format(letterTemp))
            sketchPlot(letter=letterTemp, plottingInput=True)
            letterTemp = ''
            plottingInput = False
            cv2.destroyAllWindows()
            time.sleep(3)
        else:
            print('found coord for letter {}'.format(letterTemp))
    #
    # for letterTemp in string.ascii_uppercase:
    #     coordPlotName = 'coordToPlot_{}.json'.format(letterTemp)
    #     if coordPlotName not in fileList:
    #         print('letterTemp {} not in fileList'.format(letterTemp))
    #         sketchPlot(letter=letterTemp, plottingInput=True)
    #     else:
    #         print('found coord for letter {}'.format(letterTemp))
    #
    # for letterTemp in range(10):
    #     coordPlotName = 'coordToPlot_{}.json'.format(letterTemp)
    #     if coordPlotName not in fileList:
    #         print('letterTemp {} not in fileList'.format(letterTemp))
    #         sketchPlot(letter=letterTemp, plottingInput=True)
    #     else:
    #         print('found coord for letter {}'.format(letterTemp))




# sketchPlot(readFromFile='coordToPlot/coordToPlot_b.json')
# sketchPlot()
# confPlotChars()

# getCoordsFromPicture('PICTURES/spirale.png')
getCoordsFromPicture('PICTURES/star.png')