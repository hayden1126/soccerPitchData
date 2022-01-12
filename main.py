import requests
import json
#import datetime
import re
from bs4 import BeautifulSoup
from datetime import datetime
import zlib
import glob
import os
import concurrent.futures
import itertools

## import General helper components ##
from components.helpers import generate_hash_value
from components.helpers import process_string
from components.helpers import clean_phone_num
from components.helpers import DMS_to_WGS84
from components.helpers import get_list_length

## import IO helper components ##
from components.iohelpers import download_files
from components.iohelpers import get_latest_file_in_directory
from components.iohelpers import move_final_file_from_cached_folder
from components.iohelpers import remove_cached_files
from components.iohelpers import read_jsondata_from_file


## constants are list below ##
global CONSTANT
CONSTANT = {
    "url": "https://www.lcsd.gov.hk/datagovhk/facility/facility-hssp7.json"
}
global headers

headers = {"Content-Type":"application/xml",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0", 
"Connection": "close"}

def clean_facilities(sText):
    if sText == None:
        return ""
    else:
        soup = BeautifulSoup(sText, 'html.parser')
        cText = soup.text
        return cText

def determine_overall(a, b):
    if a != None:    
        if type(b) == list:
            returnValue = False
            for keyword in b:
                if keyword.lower() in a.lower():
                    returnValue = True
                    break
            return returnValue
            
        else:
            if b.lower() in a.lower():
                return True
            else:
                return False
    else:
        return False

def determine_overall_with_remark(a, b):
    if a == True or b == True:
        return True
    else:
        return False

def find_court_no(a):
    if a != None or a == "":
        returnValue = a.strip()[:2]
        if returnValue.isnumeric():
            return int(a)
        else:
            return "No information provided"
    else:
        return "No information provided"

def convert_opening_hours(a, b):
    aSplit = a.split(b)
    start = aSplit[0].strip().replace(" ", "")
    end = aSplit[1].strip().replace(" ", "")
    if ":" in start:
        inTime = datetime.strptime(start, "%I:%M%p")
        startTime = datetime.strftime(inTime, "%H:%M")
    else:
        inTime = datetime.strptime(start, "%I%p")
        startTime = datetime.strftime(inTime, "%H:%M")
    if ":" in end:
        inTime = datetime.strptime(end, "%I:%M%p")
        endTime = datetime.strftime(inTime, "%H:%M")
    else:
        inTime = datetime.strptime(end, "%I%p")
        endTime = datetime.strftime(inTime, "%H:%M")
    return("{}-{}".format(startTime, endTime))

def find_opening_hours(a, b):
    if b == "blUhXe01yV":
        a = "5:30 am to 11:30 pm daily"
            #"7 am to 11 pm daily"
            #"7 am to 11 pm daily (1 hour per session)"

            #"24 hours daily"
            #"7am – 9pm daily"

            #"7:30 am &ndash; 10:00 pm daily"
            #"7:00 am &ndash; 11:00 pm daily (No provision of floodlight)"
    if "daily" in a:
        a = a[:a.find("daily")].strip()
    else:
        #print(a.find("("))
        a = a[:a.find("(")]
    a = a.replace("–", "-")
    #print()
    #print(b)
    #print(a)
    
    if a == "24 hours":
        openingHours = "00:00-23:59"
        #print(openingHours)
        return openingHours
    
    elif "to" in a:
        openingHours = convert_opening_hours(a, "to")
        #print(openingHours)
        return openingHours
    
    elif "ndash" in a:
        openingHours = convert_opening_hours(a, "&ndash;")
        #print(openingHours)
        return openingHours

    elif "-" in a:
        openingHours = convert_opening_hours(a, "-")
        #print(openingHours)
        return openingHours

    else:
        #print("Unknown")
        return "Unknown"

def reformat_raw_data(ele):
    # ele = list[1]
    # totalProcess = list[0]
    # print("totalProcess: ", totalProcess)
    global totalProcess, counter
    totalProcess = get_list_length(data)
    cleanFacilityString = clean_facilities(ele["Ancillary_facilities_en"])

    newPitchesData = {   
        "UUID" : ele["GIHS"],
        "hashValue": generate_hash_value(ele["Name_cn"],ele["Opening_hours_cn"],ele["Remarks_cn"]),
        "location" : {
            "name" : {
                "en" : ele["Name_en"].strip(),
                "cn" : ele["Name_cn"].strip()
            },
            "address" : {
                "en" : ele["Address_en"].strip(),
                "cn" : ele["Address_cn"].strip()
            },
            "district" : {
                "en" : ele["District_en"].strip(),
                "cn" : ele["District_cn"].strip()
            },
            "geocode" : {
                "WGS84": {
                    "lat": DMS_to_WGS84(ele["Latitude"]),
                    "lng": DMS_to_WGS84(ele["Longitude"]),
                    "DMS": {
                        "lat": ele["Latitude"],
                        "lng": ele["Longitude"]
                    }
                }
            },
            "court_no": find_court_no(ele["Court_no_en"])
        },
        "phone": clean_phone_num(ele["Phone"]),
        

        "opening_hours": find_opening_hours(clean_facilities(ele["Opening_hours_en"]), ele["GIHS"]),
        "multiPurposeCourt": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "multi"), 
                determine_overall(ele["Remarks_en"], "multi")
                ),
        "facilities": {
            "toilet": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "toilet"), 
                determine_overall(ele["Remarks_en"], "toilet")
                ),
            "changingRoom": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "changing"), 
                determine_overall(ele["Remarks_en"], "changing")
                ),
            "locker": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "locker"), 
                determine_overall(ele["Remarks_en"], "locker")
                ),
            "accessibility": {
                "toilet": determine_overall(cleanFacilityString, "Accessible Toilet"),
                "tactileGuidePath": determine_overall(cleanFacilityString, "tactile guide path"),
                "brailleDirectoryMap": determine_overall(cleanFacilityString, "braille directory")
            },
            "carpark": determine_overall_with_remark(
                determine_overall(cleanFacilityString, ["car park", "carpark"]), 
                determine_overall(ele["Remarks_en"], ["car park", "carpark"])
                ),
            "kiosk": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "kiosk"), 
                determine_overall(ele["Remarks_en"], "kiosk")
                ),
            "spectatorStand": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "spectator"), 
                determine_overall(ele["Remarks_en"], "spectator")
                ),
            "soccerPitch": {
                "artificialTurf": determine_overall_with_remark(
                determine_overall(cleanFacilityString, ["artificial"]), 
                determine_overall(ele["Remarks_en"], ["artificial"])
                ),
                "naturalTurf": determine_overall_with_remark(
                determine_overall(cleanFacilityString, ["natural"]), 
                determine_overall(ele["Remarks_en"], ["natural"])
                )
            },
            "basketballCourt": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "basketball"), 
                determine_overall(ele["Remarks_en"], "basketball")
                ),
            "playground": determine_overall_with_remark(
                determine_overall(cleanFacilityString, ["play ", "playground"]), 
                determine_overall(ele["Remarks_en"], ["play ", "playground"])
                ),
            "fitnessStation": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "fitness"), 
                determine_overall(ele["Remarks_en"], "fitness")
                ),
            "elderlyFitnessEquipment": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "elderly fitness"), 
                determine_overall(ele["Remarks_en"], "elderly fitness")
                ),
            "volleyballCourt": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "volleyball"), 
                determine_overall(ele["Remarks_en"], "volleyball")
                ),
            "cyclingTrack": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "cycling"), 
                determine_overall(ele["Remarks_en"], "cycling")
                ),
            "joggingTrack": determine_overall_with_remark(
                determine_overall(cleanFacilityString, ["running", "jogging"]), 
                determine_overall(ele["Remarks_en"], ["running", "jogging"])
                ),
            "pebbleWalkingTrail": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "pebble"), 
                determine_overall(ele["Remarks_en"], "pebble")
                ),
            "tennisCourt": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "tennis"), 
                determine_overall(ele["Remarks_en"], "tennis")
                ),
            "rollerSkatingRink": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "roller skating"), 
                determine_overall(ele["Remarks_en"], "roller skating")
                ),
            "raceCourse": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "race course"), 
                determine_overall(ele["Remarks_en"], "race course")
                ),
            "handball": determine_overall_with_remark(
                determine_overall(cleanFacilityString, "handball"), 
                determine_overall(ele["Remarks_en"], "handball")
                )
        }
    }

    counter += 1
    print("Processing {} of {}, {:.1%} finished".format(counter, totalProcess, counter/int(totalProcess)),
    end="\r", flush=True)

    return newPitchesData


def main(data):
    print(totalProcess, counter)

    newPitchesList =[]
    global totalProcess
    totalProcess = get_list_length(data)

    print("\nWe have {} data to process.".format(totalProcess))
    print("\n\n")

    #legend
    # for d in data:
    #     cleanedObj = reformat_raw_data(totalProcess, d)
    #     newPitchesList.extend(cleanedObj)
    
    # currentTime = datetime.now()
    # x = open("./data/cached/soccer_pitches_cleaned" + "_" + currentTime.isoformat() + ".json","w")
    # x.write(json.dumps(newPitchesList, indent=4, sort_keys=True, ensure_ascii=False))
    # x.close()


    # for concurrent
    array = [(ele, totalProcess) for ele in data], totalProcess
    args = ((totalProcess, d) for d in data)
    # with concurrent.futures.ThreadPoolExecutor(max_workers=8) as executor:
    with concurrent.futures.ProcessPoolExecutor(max_workers=7) as executor:
        # formattedObject = executor.map(
        #     lambda p: reformat_raw_data( * p), args)
    
        formattedObject = executor.map(reformat_raw_data, [d for d in data])
        newPitchesList.extend(formattedObject)

        # for d in executor.map(lambda p: reformat_raw_data( * p), args):
        #     newPitchesList.extend(d)
        
        currentTime = datetime.now()
        x = open("./data/cached/soccer_pitches_cleaned" + "_" + currentTime.isoformat() + ".json","w")
        x.write(json.dumps(newPitchesList, indent=4, sort_keys=True, ensure_ascii=False))
        x.close()

    


if __name__ == "__main__":
    global totalProcess, counter
    counter = 0
    startTime = datetime.now()
    # download_files(CONSTANT["url"], headers)
    data = read_jsondata_from_file("./data/raw/")
    totalProcess = get_list_length(data)
    main(data)
    move_final_file_from_cached_folder("./data/cached/", "./data/clean/")
    remove_cached_files("./data/cached/")
    timeNow =  datetime.now()
    print(
        "\n\nTotal use {} seconds to run".format(round((timeNow - startTime).total_seconds()))
    )