from phue import Bridge, Light
import requests
import time
import json
import datetime
import glob
import sys
import os

# code Params
currentTime = datetime.datetime.now()
printDebug = False
lightDebug = False
sleepOffset = 0.1
lightDict = {
    "Chambre - Pyramide": 0,
    "Salon Petit Lampadaire": 1,
    "Lampadaire Salle à manger": 2,
    "Chevet Antoine": 3,
    "Chevet Silène": 4,
    "Guirlande Chambre": 5,
    "Hue white spot 1": 6,
    "Hue white spot 2": 7,
    "Hue white spot 3": 8,
    "Hue white spot 4": 9
}
lightSwitchDict = {
    'ZONE Chambre': ["Chambre - Pyramide"],  # , "Guirlande Chambre"
    'ZONE Salle à manger': ["Hue white spot 1"],  # , "Hue white spot 2", "Hue white spot 3", "Hue white spot 4"
    'ZONE Salon': ["Lampadaire Salle à manger"]
}
lightsToSwitchPerRoomDict = {
    'ZONE Chambre': ["Chambre - Pyramide", "Guirlande Chambre", "Chevet Antoine", "Chevet Silène"],
    'ZONE Salle à manger': ["Hue white spot 1", "Hue white spot 2", "Hue white spot 3", "Hue white spot 4"],
    'ZONE Salon': ["Lampadaire Salle à manger", "Salon Petit Lampadaire"]  # Add more in the future
}
specialLightSwitchDict = {
    'ZONE Dodo Muffin': ["Chevet Antoine", "Chevet Silène"]
}

# Set up the bridge
bridge_ip = "192.168.1.19"
api_key = "QcCTJEqu4z-IfcqpbG9H8108JCqX9dLtcXReKquc"


def getAllLights():

    if lightDebug: setSpecificLightBrightness("Chevet Antoine", 33)
    b = Bridge(bridge_ip, api_key)
    # print('{}'.format(b.get_ip_address()))
    lights = b.lights
    if printDebug: print(lights)
    return lights

b = Bridge(bridge_ip, api_key)
# print('{}'.format(b.get_ip_address()))
lights = b.lights

def ordered(obj):
    if isinstance(obj, dict):
        return sorted((k, ordered(v)) for k, v in obj.items())
    if isinstance(obj, list):
        return sorted(ordered(x) for x in obj)
    else:
        return obj

def jsonEquals(a, b):
    return ordered(a) == ordered(b)

def fluctuateLights(zone='Salon'):
    for lightName in lightDict.keys():
        if zone in lightName:
            try:
                print(f"lights[{lightName}].brightness = {lights[lightDict[lightName]].brightness}")
            except KeyError as err:
                print(err)
                continue

            if (lights[lightDict[lightName]].brightness != 0):
                print('decreasing lights')
                currentPercent = lights[lightDict[lightName]].brightness * 0.9
                newPercent = 10
                if lights[lightDict[lightName]].brightness - currentPercent < newPercent:
                    currentPercent = 0
                print(f'with currentPercent : {currentPercent}')
                setSpecificLightBrightness(lightName, currentPercent)
            else:
                print('increasing lights ! ')
                setSpecificLightBrightness(lightName, 200)


def decreaseLights():
    for lightName in lightDict.keys():
        if 'Salon' in lightName:
            decreaseSpecificLight(lightName)


def setSpecificLightBrightness(lightName="Lampadaire Salle à manger", brightnessInput=50):
    # Turn on a light
    lights[lightDict[lightName]].brightness = int(brightnessInput)
    # lights[lightDict["Salon Coin 2"]].brightness*0.9


def decreaseSpecificLight(lightName="Lampadaire Salle à manger"):
    # Turn on a light
    lights[lightDict[lightName]].brightness = int(lights[lightDict[lightName]].brightness * 0.9)
    # lights[lightDict["Salon Coin 2"]].brightness*0.9


def activateSync_old():
    # Set up the endpoint URL and headers
    endpoint_url = 'http://' + bridge_ip + '/api/' + api_key + '>/sensors/<your_hue_sync_sensor_id>/state'
    headers = {'Content-Type': 'application/json'}

    # Set up the data for starting the sync
    sync_start_data = {
        'status': True
    }

    # Send the request to start the sync
    response = requests.put(endpoint_url, headers=headers, data=json.dumps(sync_start_data))

    # Print the response
    print(response.content)

    # Set up the data for stopping the sync
    sync_stop_data = {
        'status': False
    }

    # Send the request to stop the sync
    response = requests.put(endpoint_url, headers=headers, data=json.dumps(sync_stop_data))

    # Print the response
    print(response.content)


def activateSync_lessOld():
    # Set up the API endpoint and authentication token
    api_url = "http://" + bridge_ip + "/api/" + api_key + "/"
    access_token = api_key

    # Start the sync
    start_url = api_url + "sync/start"
    headers = {'Authorization': 'Bearer ' + access_token}
    response = requests.post(start_url, headers=headers)
    print(response.json())

    # Stop the sync
    stop_url = api_url + "sync/stop"
    response = requests.post(stop_url, headers=headers)
    print(response.json())


def activateSync():
    # Set up the bridge and get the lights
    b = Bridge(bridge_ip)
    lights = b.lights

    # # Set up the entertainment area
    # area_name = "your_entertainment_area_name_here"
    # area = b.create_group(area_name, [l.light_id for l in lights], type="Entertainment")

    # Get the Hue Entertainment device

    # Get the Entertainment Group object
    entertainment_group = b.get_group('TV area')

    # Print information about the Entertainment Group
    print("Entertainment Group:")
    print(f"Name: {entertainment_group}")

    # Get the ID of the Hue Sync sensor
    sensor_id = b.get_sensor_id_by_name('TV area')
    print(sensor_id)

    # Get the ID of the Entertainment group
    group_id = b.get_group_id_by_name('TV area')
    print(group_id)

    # Activate the sync for the Entertainment group
    b.activate_scene(group_id, 'TV area')

    # b.set_group('TV area', {'stream': {'active': True}})
    # print(f"Name: {entertainment_group.name}")
    # print(f"ID: {entertainment_group.group_id}")
    # print(f"Type: {entertainment_group.type}")
    # Start the sync
    # entertainment_device[0].start()

    # Stop the sync
    # entertainment_device[0].stop()


# activateSync()

def main(param1, param2):
    print(f"param1: {param1}")
    print(f"param2: {param2}")
    if param2 == 'off':
        for lightName in lightDict.keys():
            if 'Salon' in lightName:
                setSpecificLightBrightness(lightName, 0)
    if param2 == 'hibernate':
        for lightName in lightDict.keys():
            if 'Salon' in lightName:
                setSpecificLightBrightness(lightName, 1)
    if param2 == 'full':
        for lightName in lightDict.keys():
            if 'Salon' in lightName:
                setSpecificLightBrightness(lightName, 200)
    if param2 == 'decrease':
        decreaseLights()
    if param2 == 'fluctuate':
        fluctuateLights()


def doActions(actionsInput):
    print('In doActions with actionsInput : ', actionsInput)
    for zoneTemp in actionsInput.keys():
        lightsToChange = []
        if 'ZONE ' in zoneTemp:
            print('need to act on zone : {}, so lights : {}'.format(zoneTemp, lightsToSwitchPerRoomDict[zoneTemp]))
            lightsToChange = lightsToSwitchPerRoomDict[zoneTemp]
        elif zoneTemp in lightDict.keys():
            print('Action required on single light : ', zoneTemp)
            lightsToChange = [zoneTemp]
        for lightToChange in lightsToChange:
            for actionType in actionsInput[zoneTemp].keys():
                actionValue = actionsInput[zoneTemp][actionType]
                print('\n => Changing actionType {} to actionValue = {} on lightToChange {}'.format(actionType, actionValue, lightToChange))
                print("lights[lightDict[lightToChange]] : {}", '{}'.format(lights[lightDict[lightToChange]]).lower())
                if actionType == 'brightness':
                    if 'guirlande' not in '{}'.format(lights[lightDict[lightToChange]]).lower():
                        print('lightToChange.on : {}'.format(lights[lightDict[lightToChange]].on))
                        if lights[lightDict[lightToChange]].on:
                            print('turning brightness from {} to {}'.format(lights[lightDict[lightToChange]].brightness,
                                                                            int(actionValue)))
                            lights[lightDict[lightToChange]].brightness = int(actionValue)

                        print('turning <on> from {} to {}'.format(lights[lightDict[lightToChange]].on, int(actionValue) > 0))
                        lights[lightDict[lightToChange]].on = int(actionValue) > 0
                    else:
                        print('turning <on> from {} to {}'.format(lights[lightDict[lightToChange]].on, int(actionValue) > 0))
                        lights[lightDict[lightToChange]].on = int(actionValue) > 0


                if actionType == 'on':
                    lights[lightDict[lightToChange]].on = bool(actionValue)


    return True

def saveJson(jsonOutput, fileName):
    # Serializing json
    json_object = json.dumps(jsonOutput, indent=4)
    jsonArray = glob.glob('lightData/json/*.json')
    while len(jsonArray) > 10:
        os.remove('{}'.format(jsonArray[0]))
        jsonArray = glob.glob('lightData/json/*.json')
    jsonArray.reverse()
    if len(jsonArray) > 0:
        print('Checking if last JSON was different : Opening ', jsonArray[0])
        f = open(jsonArray[0])
        dataPast = json.load(f)
        if not jsonEquals(dataPast, jsonOutput):
            print('Saving JSON due to difference between dataPast (1) & jsonOutput (2) : \n{}\n{}'.format(dataPast, jsonOutput))
            # Writing to sample.json
            with open('lightData/json/{}.json'.format(fileName), "w") as outfile:
                outfile.write(json_object)
            return True
        else:
            print('No change : Not saving JSON')
            return False

    print('Len of jsonArray seems to be 0, therefore saving ')
    with open('lightData/json/{}.json'.format(fileName), "w") as outfile:
        outfile.write(json_object)
    return True

def compareToPast(jsonNow):

    if lightDebug: setSpecificLightBrightness("Chevet Antoine", 99)
    print('in compareToPast')
    actionsReturn = {}
    jsonArray = glob.glob('lightData/json/*.json')
    jsonArray.reverse()
    if len(jsonArray) > 1:
        print('Opening ', jsonArray[1])
        f = open(jsonArray[1])
        dataPast = json.load(f)

        # Compare lightswitches
        for room in lightSwitchDict.keys():
            print('Checking if lightswitch for room ', room, ' has changed')
            connectedLights = lightSwitchDict[room]
            roomLights = lightsToSwitchPerRoomDict[room]
            for conLightTemp in connectedLights:  # Checking the reachability of all lights connected to mural lightswitches
                if (jsonNow[conLightTemp]['reachable'] != dataPast[conLightTemp]['reachable']):
                    print('(!) Reachable has changed from past {} to now {}'.format(dataPast[conLightTemp]['reachable'],
                                                                                    jsonNow[conLightTemp]['reachable']))

                    if jsonNow[conLightTemp]['reachable']:
                        print(
                            '\n #### ===> Lightswitch in {} seems to have been turned ON : must activate all (reachable) lights : {}'.format(
                                room, roomLights))
                        actionsReturn[room] = {"brightness": 254}
                        return actionsReturn
                    else:
                        print(
                            '\n #### ===> Lightswitch in {} seems to have been turned OFF : must deactivate all (reachable) lights : {}'.format(
                                room, roomLights))
                        actionsReturn[room] = {"brightness": 0}
                        return actionsReturn
                else:  # Looking for ANOMALIES
                    print('No reachable change (current reachability : {}): Checking for anomalies'.format(
                        jsonNow[conLightTemp]['reachable']))
                    anomaly = []
                    for roomLightTemp in roomLights:
                        try:
                            jsonNow[roomLightTemp]
                        except KeyError as err:
                            print('Missing data for roomLightTemp {} '.format(roomLightTemp))
                            if printDebug: print('Missing data for roomLightTemp {} ; Performing speedMode:False on saveLights and refreshing data on old_jsonNow : {}'.format(roomLightTemp, jsonNow))
                            jsonNow = saveLight(speedMode=False)
                            if printDebug: print('New jsonNow : ', jsonNow)
                            try:
                                jsonNow[roomLightTemp]
                            except KeyError as err:
                                print('\n\n\n\n(!!!) roomLightTemp {} is still missing : What do ?'.format(roomLightTemp))
                                continue

                            # for keyTemp in lightsToSwitchPerRoomDict.keys():
                            #     if roomLightTemp in lightsToSwitchPerRoomDict[keyTemp]:
                            #         print('It belongs to room : ', keyTemp)
                            #         for conLightTemp2 in lightSwitchDict[keyTemp]:
                            #             if conLightTemp2 in jsonNow.keys():
                            #                 jsonNow[roomLightTemp]

                        if jsonNow[roomLightTemp]['reachable'] and jsonNow[roomLightTemp]['on'] != \
                                jsonNow[conLightTemp]['on']:
                            anomaly.append(roomLightTemp)
                            print(
                                '(!) Parameter <on> is different between connectedLight {} ({}) and roomLight {} ({})'.format(
                                    conLightTemp, jsonNow[conLightTemp]['on'], roomLightTemp,
                                    jsonNow[roomLightTemp]['on']))
                            if jsonNow[conLightTemp]['on']:
                                print(
                                    'Lightswitch for conLightTemp {} is ON : turning on roomLight : {}'.format(
                                        conLightTemp, roomLightTemp))
                                actionsReturn[roomLightTemp] = {"on": True, "brightness": 254}
                                return actionsReturn
                            else:
                                print(
                                    'Lightswitch for conLightTemp {} is OFF : turning off roomLight : {}'.format(
                                        conLightTemp, roomLights))
                                actionsReturn[roomLightTemp] = {"on": False}
                                return actionsReturn

                    # TODO : Manage specialLightSwitchDict

                    if anomaly != []:
                        print('(!) Anomaly found for roomLights  : ', roomLightTemp)
                    else:
                        print('No anomalies found for config (jsonNow) : ', jsonNow)

    print('\n ==> Done with compareToPast ; actions : {}\n'.format(actionsReturn))

    return actionsReturn


def convertPhueToJson(lightInput):
    lightJson = {}
    try:
        lightJson["light_id"] = lightInput.light_id
    except KeyError as err:
        if printDebug: print('No light_id for this light : setting to None')
        lightJson["light_id"] = None
    try:
        lightJson["name"] = lightInput.name
    except KeyError as err:
        if printDebug: print('No name for this light : setting to None')
        lightJson["name"] = None
    try:
        lightJson["on"] = lightInput.on
    except KeyError as err:
        if printDebug: print('No on for this light : setting to None')
        lightJson["on"] = None
    try:
        lightJson["brightness"] = lightInput.brightness
    except KeyError as err:
        if printDebug:  print('No brightness for this light : setting to None')
        lightJson["brightness"] = None
    try:
        lightJson["colormode"] = lightInput.colormode
    except KeyError as err:
        if printDebug: print('No colormode for this light : setting to None')
        lightJson["colormode"] = None
    try:
        lightJson["hue"] = lightInput.hue
    except KeyError as err:
        if printDebug: print('No hue for this light : setting to None')
        lightJson["hue"] = None
    try:
        lightJson["saturation"] = lightInput.saturation
    except KeyError as err:
        if printDebug: print('No saturation for this light : setting to None')
        lightJson["saturation"] = None
    try:
        lightJson["xy"] = lightInput.xy
    except KeyError as err:
        if printDebug: print('No xy for this light : setting to None')
        lightJson["xy"] = None
    try:
        lightJson["colortemp"] = lightInput.colortemp
    except KeyError as err:
        if printDebug: print('No colortemp for this light : setting to None')
        lightJson["colortemp"] = None
    try:
        lightJson["effect"] = lightInput.effect
    except KeyError as err:
        if printDebug: print('No effect for this light : setting to None')
        lightJson["effect"] = None
    try:
        lightJson["alert"] = lightInput.alert
    except KeyError as err:
        if printDebug: print('No alert for this light : setting to None')
        lightJson["alert"] = None
    try:
        lightJson["transitiontime"] = lightInput.transitiontime
    except KeyError as err:
        if printDebug: print('No transitiontime for this light : setting to None')
        lightJson["transitiontime"] = None
    try:
        lightJson["reset_bri_after_on"] = lightInput.reset_bri_after_on
    except AttributeError as err:
        if printDebug: print('No reset_bri_after_on for this light : setting to None')
        lightJson["reset_bri_after_on"] = None
    except KeyError as err:
        if printDebug: print('No reset_bri_after_on for this light : setting to None')
        lightJson["reset_bri_after_on"] = None
    try:
        lightJson["reachable"] = lightInput.reachable
    except KeyError as err:
        if printDebug: print('No reachable for this light : setting to None')
        lightJson["reachable"] = None
    try:
        lightJson["type"] = lightInput.type
    except KeyError as err:
        if printDebug: print('No type for this light : setting to None')
        lightJson["type"] = None

    return lightJson


def saveLight(speedMode=True):
    lightArrayInput = getAllLights()
    currentTime = datetime.datetime.now()
    print('{} : In saveLight (speedMode : {}) with : {} of length : {}'.format(currentTime, speedMode, lightArrayInput,
                                                                               len(lightArrayInput)))
    fileName = '{}'.format(currentTime).replace(' ', '_').replace(':', '-').replace('.', '_')
    if printDebug: print('fileName : ', fileName)
    lightJsonOutput = {}
    searchDict = lightDict.keys()
    if speedMode:
        searchDict = []
        for lightTemp in lightSwitchDict.keys():
            searchDict += lightSwitchDict[lightTemp]
    if printDebug: print('SearchDict is : ', searchDict)

    if lightDebug: setSpecificLightBrightness("Chevet Antoine", 40)
    for lightName in searchDict:
        if printDebug: print('searching for ', lightName)
        if lightName in '{}'.format(lightArrayInput):
            try:
                # print(f"lights[{lightName}] = {lights[lightDict[lightName]]}")
                lightJson = convertPhueToJson(lightArrayInput[lightDict[lightName]])
                print('#######################################################')
                print('#    light_id : ', lightJson['light_id'])
                print('#    name : ', lightJson['name'])
                print('#    on : ', lightJson['on'])
                print('#    reachable : ', lightJson['reachable'])
                print('#    brightness : ', lightJson['brightness'])
                print('#    type : ', lightJson['type'])
                print('#######################################################')
                if printDebug: print('lightJson : ', lightJson)
                lightJsonOutput[lightJson['name']] = lightJson
            except KeyError as err:
                print('\n\n\n(!) Error for lightName : ', lightName, ' (!) \n')
                print(err)
                continue
        else:
            print('(!) WARN (!) Light {} is not in lightArrayInput {}'.format(lightName, lightArrayInput))

    if lightDebug: setSpecificLightBrightness("Chevet Antoine", 50)
    saveResult = False

    # if not speedMode:
    #     print('Not speedmode ; saving to fileName : ', fileName)
    saveResult = saveJson(lightJsonOutput, fileName)

    currentTime = datetime.datetime.now()
    if saveResult: print('\n ==> lightData saved correctly at {}\n'.format(currentTime))

    return lightJsonOutput



if __name__ == '__main__':
    print(sys.argv)  # philips_watcher.py
    # setup everything

    print('\n ==> Launching at {} <== \n'.format(currentTime))
    nextSpeedMode = False

    while True:

        if lightDebug: setSpecificLightBrightness("Chevet Antoine", 1)
        # saveLightContext
        jsonNow = saveLight(speedMode=nextSpeedMode)

        # compareToPast ; returns json dict with rooms /
        actions = compareToPast(jsonNow)

        if actions != {}:

            if lightDebug: setSpecificLightBrightness("Chevet Antoine", 40)
            nextSpeedMode = True
            doActions(actions)
        else:
            print('No actions : sleeping for ', sleepOffset)
            nextSpeedMode = True
            time.sleep(sleepOffset)

        # main(sys.argv[0], sys.argv[1])
        # fluctuateLights()
        # time.sleep(2)

    # decreaseCornerLight()
