import requests
import json
import datetime
import re
from bs4 import BeautifulSoup

headers = {"Content-Type":"application/xml",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0", 
"Connection": "close"}


def download_files():
    #download the file into memory
    res = requests.get("https://www.lcsd.gov.hk/datagovhk/facility/facility-hssp7.json", headers=headers)

    json_file= json.loads(res.text)
    json_data= json.dumps(json_file, indent=4, sort_keys=True, ensure_ascii=False)
    #print(json_data)
    x= open("soccer_pitches_data_raw.json","w")
    x.write(json_data)
    x.close()


def clean_facilities(sText):
    soup = BeautifulSoup(sText, 'html.parser')
    cText = soup.text
    print(cText)

def clean_newline(address):
    cleanedAddress = address.replace("\n", " ")
    return cleanedAddress

def process_string(address):
    cleanedAddress = clean_newline(address)
    cleanedAddress = remove_useless_whitespace(cleanedAddress)
    return cleanedAddress

def remove_useless_whitespace(address):
    cleanedAddress = address.strip().lower()
    return cleanedAddress



def main():
    startTime = datetime.datetime.now()

    download_files()

    x= open("soccer_pitches_data_raw.json")
    data = json.load(x)

    newStationsList =[]
    counter = 0

    for ele in data:
        cleanFacilityString = clean_facilities(ele["Ancillary_facilities_en"])
        if ele["Remarks_en"] !=  "":
            print(ele["Remarks_en"])
        #counter+=1
        #if counter > 10:
            #break

        
        newPitchesData = {   
    "UUID" : "9G5i7NFpXL",
    "location" : {
        "name" : {
            "en" : "",
            "cn" : ""
        },
        "address" : {
            "en" : "",
            "cn" : ""
        },
        "district" : {
            "en" : "",
            "cn" : ""
        },
        "geocode" : {
            "WGS84": {
                "lat": "",
                "lng": "",
                "DMS": {
                    "lat": "",
                    "lng": ""
                }
            }
        },
        "court_no": "1"
    },
    "phone": ["12341234"],
    "opening_hours": "7am - 11pm",
    "multiPurposeCourt": "",
    "facilities": {
        "toilet": True,
        "changingRoom": True,
        "locker": True,
        "accessibility": {
            "toilet": True,
            "tactileGuidePath": True,
            "brailleDirectoryMap": True
        },
        "carpark": "",
        "kiosk": "",
        "spectatorStand": "",
        "footballPitch": {
            "artificial": "",
            "natural": ""
        },
        "basketballCourt": "",
        "playground": "",
        "childernPlayEquipment": "",
        "fitnessStation": "",
        "elderlyFitnessEquipment": "",
        "volleyballCourt": "",
        "cyclingTrack": "",
        "joggingTrack": "",
        "pebbleWalkingTrail": "",
        "tennisCourt": "",
        "rollerSkatingRink": "",
        "raceCourse": ""
    }
        }




    #     """
    #     "vehicle" value should be Tesla, BYD or General
    #     """
    #     newStationData = {
    #         "uuid": station["no"],
    #         "address": {
    #             "full": {
    #                 "zh": "",
    #                 "en": process_string(remove_useless_whitespace(station["address"]))
    #             },
    #             "streetName": process_string(station["address"]),
    #             "region": process_string(station["districtL"]),
    #             "district": process_string(station["districtS"]),
    #             "locationName": {
    #                 "zh" : "",
    #                 "en": process_string(station["location"])
    #             },
    #             "geocode":{
    #                 "WGS84": {
    #                     "lat": station["lat"],
    #                     "lng": station["lng"],
    #                 }
    #             }
    #         },
    #         "provider": process_string(station["provider"]),
    #         "type": {
    #             "charging": process_string(station["type"]).split(";"), #standard / semiquick / quick
    #             "vehicle": vehicle_supported_type(station["parkingNo"]), 
    #         },
    #         "publicPermit": check_public_permit(station["parkingNo"]),
    #         "parkingSlot": parking_slot_list(station["parkingNo"]),
    #         "updateCheckSum": ""
    #     }


    #     newStationsList.append(newStationData)
    #     counter += 1

    #     if counter % 20 == 0:
    #         x = open("cleaned_EV_raw.json","w")
    #         x.write(json.dumps(newStationsList, indent=4))
    #         x.close()



    timeNow =  datetime.datetime.now()
    print(
        "Total use {} seconds to run".format(round((timeNow - startTime).total_seconds()))
    )


if __name__ == "__main__":
    main()