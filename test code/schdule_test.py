import requests
import json
import csv
import os
import schedule
import time
from datetime import date, datetime

def main():
    print(datetime.now())

# schedule.every().hour.at("15:00").do(main)
# schedule.every().hour.at("15:30").do(main)
# schedule.every().hour.at("16:20").do(main)
# schedule.every().hour.at("17:00").do(main)
# schedule.every().hour.at("17:06").do(main)
# schedule.every().hour.at("20:00").do(main)

schedule.every().hour.at("06:00").do(main)
schedule.every().hour.at("16:00").do(main)
schedule.every().hour.at("26:00").do(main)
schedule.every().hour.at("36:00").do(main)
schedule.every().hour.at("46:00").do(main)
schedule.every().hour.at("56:00").do(main)

main()

while 1:
    n = schedule.idle_seconds()
    print(n)
    if n is None:
        # no more jobs
        break
    elif n > 0:
        # sleep exactly the right amount of time
        time.sleep(n)
    schedule.run_pending()