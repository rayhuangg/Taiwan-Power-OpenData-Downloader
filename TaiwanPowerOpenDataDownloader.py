# -*- coding: utf-8 -*-

'''
    version: 2.1.2
    每十分鐘定時自動下載台電各機組發電量Open Data, 以及台電今日電力資訊, 並轉為Excel可讀取之csv檔案儲存
    待解決: 跨日23:50檔案跑到隔天去(偶發,台電資料上傳不及時)
'''

import traceback
import requests
import json
import csv
import os
import schedule
import time
import pandas as pd
from datetime import date, datetime


opendata_url   = "https://service.taipower.com.tw/data/opendata/apply/file/d006001/001.json" # 主要網址，20230621後將原本的txt檔案修改成json了，造成網址變更
percentage_url = "https://www.taipower.com.tw/d006/loadGraph/loadGraph/data/loadpara.json"


# =========== 創立資料夾 ===========
def create_folder():
    if not os.path.isdir('csv(big5)'):
        os.mkdir('csv(big5)')

    if not os.path.isdir('csv(utf-8)'):
        os.mkdir('csv(utf-8)')

    if not os.path.isdir('json'):
        os.mkdir('json')


# ===========下載txt並轉為json格式 ===========
def download_opendata():
    create_folder()
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
    res = requests.get(opendata_url, headers=headers)
    res.encoding = "utf-8-sig"

    print("status_code:", res.status_code, "| ", end=" ")

    # 下載成功才繼續執行
    if res.status_code == 200:
        # 利用json loads把檔案轉為json格式，並用dump格式化輸出至文件
        with open("json/001.json", "w", encoding='utf-8') as file:
            json_file = json.loads(res.text)
            json.dump(json_file, file, indent=4, ensure_ascii=False) # 不使用ascii編碼 才能顯示中文

    # 不是200的話則代表網路連線有錯誤，發出錯誤訊息等待下次連線
    else:
        raise requests.exceptions.ConnectionError


# =========== 下載使用率與預估供電能力  =============
def download_percentage():
    headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"}
    res = requests.get(percentage_url, headers=headers)

    if res.status_code == 200:
        curr_load = float(res.json()["records"][0]["curr_load"])
        maxi_sply_capacity = float(res.json()["records"][3]["real_hr_maxi_sply_capacity"])
        usage_percentage = f"{curr_load / maxi_sply_capacity:.1%}"
        return usage_percentage, maxi_sply_capacity


# ======= 去除名稱或數字內的括號字樣 ===========
def remove_brackets(obj):
    if "(" not in obj:
        return obj
    else:
        return obj[:obj.index("(")] # 從第一個字取到左括號位置


# =========== 建立標題列 ===========
def create_title_row_list():
    with open("json/001.json", "r", encoding='utf-8') as json_obj:
        json_data = json.load(json_obj)

    # 建立空白二維列表
    title = [[0,0,0,] for i in range(2*len(json_data["aaData"])+1)]
    # 在最前面添加標題欄位
    title[0] = ["能源別", "機組別", "機組容量"]

    for i in range(len(json_data["aaData"])):
        # 添加能源類別，並去除括號
        title[i*2+1][0] = remove_brackets(json_data["aaData"][i][0])

        # 添加發電機組名稱，若名字內有括號(含註解)便將其去除
        title[i*2+1][1] = remove_brackets(json_data["aaData"][i][1])

        # 添加機組容量，並去除括號
        title[i*2+1][2] = remove_brackets(json_data["aaData"][i][2])

        # 空白欄 (機組狀態)，留下空白以免被後方機組狀態覆蓋
        title[i*2+2] = ["", "", ""]

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

    # 先刪除下一排空白欄，再刪除小計欄，index反轉以便從最後面開始刪除，否則從前方刪除後面會遞補index便會亂掉
    for index in index_subtotal[::-1]:
        del title[index+1]
        del title[index]

    # 加入即時供電及使用率的標題欄位
    title.append(["", "", ""])  # 空白分隔欄
    title.append(["即時供電能力", "", ""])
    title.append(["使用率", "", ""])

    return title


#  =========== 每天建立一個新的csv檔案 ===========
def create_csv_file():
    today = date.today()
    filename = today.strftime("%Y_%m_%d")

    # 寫入標題欄，加入newline='' 才不會有多餘空白欄位
    with open(f"csv(utf-8)/{filename}.csv", "w", encoding='utf-8', newline='') as csvfile:
        title = create_title_row_list()
        writer = csv.writer(csvfile)
        writer.writerows(title)


# ===========讀取現有資料轉為列表 ===========
def get_csv_content():
    today = date.today()
    filename = today.strftime("%Y_%m_%d")
    with open(f"csv(utf-8)/{filename}.csv", "r", newline='', encoding='utf-8') as csvfile:
        current_content = list(csv.reader(csvfile))

    return current_content


# =========== 新增當下數據至列表中 ===========
def append_current_data_into_list():
    csv_content = get_csv_content()

    with open("json/001.json", "r", encoding='utf-8') as json_obj:
        json_data = json.load(json_obj)

    # 平常測試時若已有此時刻的資料，便跳過不寫入
    if csv_content[0][-1] == json_data[""][-5:]:
        print("duplicate data, skip download")
        return None, None

    csv_content[0].append(json_data[""][-5:]) # 目前時間，日期不紀錄

    # 建立只有能源別+機組別的列表，以便後方查找位置
    only_name_list = [[csv_content[i][0], csv_content[i][1]] for i in range(len(csv_content))]
    for i in range(len(json_data["aaData"])):

        # 先存下機組發電量及狀態
        power_value  = json_data["aaData"][i][3]
        power_status = json_data["aaData"][i][5]

        # 查找機組名稱在csv的第幾橫列
        title = [remove_brackets(json_data["aaData"][i][0]), remove_brackets(json_data["aaData"][i][1])]
        content_index = only_name_list.index(title)

        # 寫入資料
        csv_content[content_index].append(remove_brackets(power_value))
        if content_index <= 347:  # 只有機組內容才要加入狀態，小計不用(347:小計前的最後一筆資料index)
            csv_content[content_index+1].append(power_status)

    # 寫入即時供電及使用率
    usage_percentage, maxi_sply_capacity = download_percentage()
    csv_content[-2].append(maxi_sply_capacity) # 倒數第二欄
    csv_content[-1].append(usage_percentage)   # 倒數第一欄

    return csv_content, json_data[""][-11:] # 回傳填入的list內容及時間


#  =========== 填入內容資料 ===========
def fill_in_latest_content():
    today = date.today()
    filename = today.strftime("%Y_%m_%d")
    content, download_name = append_current_data_into_list() # 放在外面先行抓取資料 否則open新的csv後便會被覆蓋
    # 若是重複時間(空資料)的話便不寫入，直接跳過結束程式
    if content == None:
        return

    # 寫入utf8版本
    with open(f"csv(utf-8)/{filename}.csv", "w", encoding='utf-8', newline='') as csvfile_utf8:
        writer = csv.writer(csvfile_utf8)
        writer.writerows(content)

    # 將utf8版本用pandas轉為excel格式
    csv_file_path = f"csv(utf-8)/{filename}.csv"
    df = pd.read_csv(csv_file_path)
    excel_file_path = f"csv(big5)/{filename}.xlsx"
    df.to_excel(excel_file_path, index=False)

    print(f"download {download_name} data .....done")


#  =========== 整體程式入口 ===========
def main():
    # 印出現在時間
    now = datetime.now()
    current_time = now.strftime("%m%d_%H:%M:%S")
    print(current_time,"| ", end="")

    try:
        today = date.today()
        filename = today.strftime("%Y_%m_%d")

        # 檢查是否已存在今日的csv檔案，是的話便僅添加資料，否則新創立csv
        if os.path.isfile(f"csv(utf-8)/{filename}.csv"):
            download_opendata()
            fill_in_latest_content()
        else:
            download_opendata()
            create_csv_file()
            fill_in_latest_content()

    except Exception as e:
        traceback.print_exc()


# 設定定時器，每小時的x7分各自執行一次
schedule.every().hour.at("07:00").do(main)
schedule.every().hour.at("17:00").do(main)
schedule.every().hour.at("27:00").do(main)
schedule.every().hour.at("37:00").do(main)
schedule.every().hour.at("47:00").do(main)
schedule.every().hour.at("57:00").do(main)

# 只執行按下執行的第一次 馬上下載資料以供確認
main()

# 利用schedule.idle_seconds()計算與下次任務間隔時間，以提供sleep秒數，應比較不會占用資源
while 1:
    n = schedule.idle_seconds()
    time.sleep(n)
    schedule.run_pending()