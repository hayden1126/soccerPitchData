import requests
import json
#import datetime
import re
from bs4 import BeautifulSoup
from datetime import datetime
import zlib
import glob
import os
import shutil

def duplicate_data(data, times):
    output = []
    for i in range(times):
        for ele in data:
            output.append(ele)
    
    return output

def download_files(url, headers):
    #download the file into memory
    res = requests.get(url, headers=headers)

    json_file = json.loads(res.text)
    json_file = duplicate_data(json_file, 300)
    json_data= json.dumps(json_file, indent=4, sort_keys=True, ensure_ascii=False)
    #print(json_data)
    currentTime = datetime.now()
    x= open("./data/raw/soccer_pitches_data_raw" + "_" + currentTime.isoformat() + ".json","w")
    x.write(json_data)
    x.close()

def read_jsondata_from_file(url):
    x= open(get_latest_file_in_directory(url)[0])
    print(x)
    data = json.load(x)
    return data




def get_latest_file_in_directory(path, mode="m"):
    files = os.listdir(path)
    paths = [os.path.join(path, basename) for basename in files]
    if mode == "c":
        return [max(paths, key=os.path.getctime), (max(paths, key=os.path.getctime).split(path))[-1]]
    else:
        return [max(paths, key=os.path.getmtime), (max(paths, key=os.path.getmtime).split(path))[-1]]

    # list_of_files = glob.glob('/path/to/folder/*') # * means all if need specific format then *.csv
    # latest_file = max(list_of_files, key=os.path.getmtime)
    # print(latest_file)

def move_final_file_from_cached_folder(cachedFolderPath, destFolderPath):
    latestCachedFilePath = get_latest_file_in_directory(cachedFolderPath)
    os.rename(latestCachedFilePath[0], destFolderPath+latestCachedFilePath[-1])
    # os.replace(latestCachedFilePath[0], destFolderPath+latestCachedFilePath[-1])

def remove_cached_files(cachedFolderPath):
    # latestCachedFilePath = get_latest_file_in_directory(cachedFolderPath)

    for root, dirs, files in os.walk(cachedFolderPath):
        for f in files:
            os.unlink(os.path.join(root, f))
        for d in dirs:
            shutil.rmtree(os.path.join(root, d))