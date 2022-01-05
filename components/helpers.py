import requests
import json
#import datetime
import re
from bs4 import BeautifulSoup
from datetime import datetime
import zlib

<<<<<<< HEAD
=======
from components.iohelpers import get_latest_file_in_directory

def get_list_length(data=get_latest_file_in_directory("./data/raw/")[0]):
    x= open(data)
    data = json.load(x)
    return (len(data))

>>>>>>> 6e7304b (remove useless files, concurrent future works, multi args not working)
def generate_hash_value(a, b, c):
    '''
    a: Name_cn
    b: Opening_hours_cn
    c: Remarks_cn
    '''
    if c == None:
        c = ""
    s = a + b + c
    #print(s)
    t = zlib.crc32(s.encode())

    return t

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

def clean_phone_num(a):
    phoneNum = a
    if type(a) != int:
        phoneNum = a.replace(" ", "")
        if phoneNum.isnumeric():
            phoneNum = [int(phoneNum)]
        else:
            phoneNum = phoneNum.split("/")
            #print(phoneNum)
    else:
        phoneNum = [int(phone) for phone in phoneNum]
    #print(phoneNum)
    return phoneNum

def DMS_to_WGS84(DMS):
    DMSSplit = DMS.split("-")   
    d = int(DMSSplit[0])
    m = int(DMSSplit[1])
    sd = int(DMSSplit[2])
    dec = 0.0
    if d >= 0:
        dec1 = d + float(m)/60 + float(sd)/3600
    else:
        dec1 = d - float(m)/60 - float(sd)/3600
    return dec1    