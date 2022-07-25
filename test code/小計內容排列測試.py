# %%
# -*- coding: utf-8 -*-

import requests
import json
import csv
import os
import schedule
import time


percentage_url = "https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadpara.json"



# 下載使用率與預估供電能力
def download_percentage():
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
    res = requests.get(percentage_url, headers=headers)

    if res.status_code == 200:
        curr_load = float(res.json()["records"][0]["curr_load"])
        maxi_sply_capacity = float(res.json()["records"][3]["real_hr_maxi_sply_capacity"])
        usage_percentage = round(curr_load / maxi_sply_capacity, 2)
        return usage_percentage, maxi_sply_capacity


# ======= 去除機組名稱的(註xx)字樣 ===========
def remove_annotation(obj):
    if "註" in obj:
            index = obj.index("註")
            new_name = obj[:index-1] # 從第一個字取到註位置前一個字(括號)
            return new_name
    else:
        return obj


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
        title[i*2+1][1] = remove_annotation(json_data["aaData"][i][1])

        # if "註" in json_data["aaData"][i][1]:
        #     name = json_data["aaData"][i][1]
        #     index = name.index("註")
        #     new_name = name[:index-1] # 從第一個字取到註位置前一個字(括號)
        #     title[i*2+1][1] = new_name
        # else:
        #     title[i*2+1][1] = json_data["aaData"][i][1]

        title[i*2+1][2] = json_data["aaData"][i][2]  # 添加機組容量
        title[i*2+2] = ["", "", ""]                  # 空白欄 (機組狀態)，留下空白以免被後方機組狀態覆蓋

    # TODO 資料填入時要注意這個空白
    title.append(["", "", ""]) # 加入機組與小計的分隔欄


    # ========== 將小計欄位統整至列表最後 ==========
    # 記下小計項目的index
    index_subtotal = []
    for index, item in enumerate(title):
        if "小計" in item:
            index_subtotal.append(index)

    # 將上面的index項目依序添加至最後一欄，先添加再刪除順序才不會亂掉
    for index in index_subtotal:
        title.append(title[index])

    # 先刪除下一排空白欄，再刪除小計欄，index反轉以便從最後面開始刪除
    for index in index_subtotal[::-1]:
        del title[index+1]
        del title[index]

    # 加入即時供電及使用率的標題欄位
    # TODO　注意這空白
    title.append(["", "", ""])  # 空白分隔欄
    title.append(["即時供電能力", "", ""])
    title.append(["使用率", "", ""])

    return title




# 新增當下數據至列表中
def append_current_data_into_list():
    pass
csv_content = create_title_row_list()

with open("json/001.json", "r", encoding='utf-8') as json_obj:
    json_data = json.load(json_obj)

csv_content[0].append(json_data[""][-5:]) # 目前時間，日期不紀錄

only_name_list = [[csv_content[i][0], csv_content[i][1]] for i in range(len(csv_content))]
for i in range(len(json_data["aaData"])):
    # 先存下機組發電量及狀態
    power_value = json_data["aaData"][i][3]
    power_status = json_data["aaData"][i][5]

    # 查找機組名稱在csv的第幾橫列
    title = [json_data["aaData"][i][0], remove_annotation(json_data["aaData"][i][1])]
    content_index = only_name_list.index(title)

    print(content_index)

    # 寫入資料
    csv_content[content_index].append(power_value)
    if content_index <= 347: # 只有機組內容才要加入狀態，小計不用(347:小計前最後一筆資料位置)
        csv_content[content_index+1].append(power_status)

usage_percentage, maxi_sply_capacity = download_percentage()
csv_content[-2].append(maxi_sply_capacity)
csv_content[-1].append(usage_percentage)


# append_current_data_into_list()