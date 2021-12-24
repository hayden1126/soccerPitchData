import requests
import json
import datetime
import re
from bs4 import BeautifulSoup
import bcrypt
# import zlib and crc32
import zlib


headers = {"Content-Type":"application/xml",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:50.0) Gecko/20100101 Firefox/50.0", 
"Connection": "close"}

def generate_hash_value(a, b, c):
    '''
    a: Name_cn
    b: Opening_hours_cn
    c: Remarks_cn
    '''
    if c == None:
        c = ""
    s = a + b + c
    print(s)
    t = zlib.crc32(s.encode())

    return t

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
    if sText == None:
        return ""
    else:
        soup = BeautifulSoup(sText, 'html.parser')
        cText = soup.text
        return cText

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

def determineMultiPurpose(a):
    if "multi" in a.lower():
        return True
    else:
        return False

def determineToilet(a):
    if "toilet" in a.lower():
        return True
    else:
        return False

def cleanPhoneNum(a):
    phoneNum = a
    if type(a) != int:
        phoneNum = int(a.replace(" ", ""))    
    return phoneNum

def determineChangingRoom(a):
    if "changing" in a.lower():
        return True
    else:
        return False

def determineSpectatorStand(a):
    if "spectator" in a.lower():
        return True
    else:
        return False

def determineOverall(a, b):
    if b in a.lower():
        return True
    else:
        return False

def determineSpectatorStand(a):
    if "spectator" in a.lower():
        return True
    else:
        return False

def main():
    startTime = datetime.datetime.now()

    download_files()

    x= open("soccer_pitches_data_raw.json")
    data = json.load(x)

    newPitchesList =[]
    counter = 0

    for ele in data:
        
        cleanFacilityString = clean_facilities(ele["Ancillary_facilities_en"])
        # if ele["Remarks_en"] !=  "":
        #     print(ele["Remarks_en"])
        #counter+=1
        #if counter > 10:
            #break

        
        newPitchesData = {   
            "UUID" : ele["GIHS"],
            "hashValue": generate_hash_value(ele["Name_cn"],ele["Opening_hours_cn"],ele["Remarks_cn"]),
            "location" : {
                "name" : {
                    "en" : ele["Name_en"],
                    "cn" : ele["Name_cn"]
                },
                "address" : {
                    "en" : "",
                    "cn" : ""
                },
                "district" : {
                    "en" : ele["District_en"],
                    "cn" : ele["District_cn"]
                },
                "geocode" : {
                    "WGS84": {
                        "lat": "",
                        "lng": "",
                        "DMS": {
                            "lat": ele["Latitude"],
                            "lng": ele["Longitude"]
                        }
                    }
                },
                "court_no": int(ele["Court_no_en"])
            },
            "phone": cleanPhoneNum(ele["Phone"]),
            "opening_hours": ele["Opening_hours_en"],
            "multiPurposeCourt": determineMultiPurpose(ele["Remarks_en"]),
            "facilities": {
                "toilet": determineToilet(cleanFacilityString),
                "changingRoom": determineChangingRoom(cleanFacilityString),
                "locker": True,
                "accessibility": {
                    "toilet": True,
                    "tactileGuidePath": True,
                    "brailleDirectoryMap": True
                },
                "carpark": "",
                "kiosk": "",
                "spectatorStand": determineSpectatorStand(cleanFacilityString),
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


        newPitchesList.append(newPitchesData)
        counter += 1

        if counter % 20 == 0:
            x = open("soccer_pitches_cleaned.json","w")
            x.write(json.dumps(newPitchesList, indent=4))
            x.close()



    timeNow =  datetime.datetime.now()
    print(
        "Total use {} seconds to run".format(round((timeNow - startTime).total_seconds()))
    )


if __name__ == "__main__":
    main()