
import requests
import json
import csv
import os
import schedule
import time
from datetime import date, datetime


# ======= 建立標題列 ===========
def create_title_row_list():
    with open("json/001.json", "r", encoding='utf-8') as json_obj:
        json_data = json.load(json_obj)

    # 建立空白二維陣列
    title = [[0,0,0,] for i in range(2*len(json_data["aaData"])+1)]
    # 在最前面添加標題欄位
    title[0] = ["能源別", "機組別", "機組容量"]

    for i in range(len(json_data["aaData"])):
        # 添加能源類別
        title[i*2+1][0] = json_data["aaData"][i][0]

        # 添加發電機組名稱，若名字內有(註)便將其去除
        if "註" in json_data["aaData"][i][1]:
            name = json_data["aaData"][i][1]
            index = name.index("註")
            new_name = name[:index-1] # 從第一字取到註位置前一個字(括號)
            title[i*2+1][1] = new_name
        else:
            title[i*2+1][1] = json_data["aaData"][i][1]

        title[i*2+1][2] = json_data["aaData"][i][2]  # 添加機組容量
        title[i*2+2] = ["", "", ""]                  # 空白欄 (機組狀態)，留下空白以免被後方機組狀態覆蓋


    # ======= 將小計欄位統整至列表最後 ==========

    # 記下小計項目的index
    index_subtotal = []
    for index, item in enumerate(title):
        if "小計" in item:
            index_subtotal.append(index)

    # 將上面的index項目連同下一排的空白欄一起添加至最後一欄，先添加再刪除順序才不會亂掉
    for index in index_subtotal:
        title.append(title[index])
        title.append(title[index+1])

    # 先刪除下一排空白欄，再刪除小計欄，index反轉以便從最後面開始刪除
    for index in index_subtotal[::-1]:
        del title[index+1]
        del title[index]

    return title


create_title_row_list()