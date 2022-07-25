#%%

import requests
import json
import csv
import os
import schedule
import time
from datetime import date, datetime


percentage_url = "https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadpara.json"

def download_percentage():
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
    res = requests.get(percentage_url, headers=headers)

    if res.status_code == 200:
        curr_load = float(res.json()["records"][0]["curr_load"])
        maxi_sply_capacity = float(res.json()["records"][3]["real_hr_maxi_sply_capacity"])
        usage_percentage = round(curr_load / maxi_sply_capacity, 2)
        print("usage_percentage", usage_percentage)
        print("maxi_sply_capacity",maxi_sply_capacity)
        # return usage_percentage

download_percentage()
# %%
