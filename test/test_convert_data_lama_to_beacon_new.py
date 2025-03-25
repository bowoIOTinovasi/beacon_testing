import json
from tracemalloc import start
import xlsxwriter
import statistics
from datetime import datetime
import random
import time
import sys
import os

# excel
workbook = xlsxwriter.Workbook('sample_beacon_new_{}.xlsx'.format(random.randint(1,100)))
worksheet = workbook.add_worksheet()
worksheet.write(0, 0, "No")
worksheet.write(0, 1, "Datetime")
worksheet.write(0, 2, "MAC")
# worksheet.write(0, 3, "dBm")
# worksheet.write(0, 4, "Vendor")

list_file = [
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/raw/9C_9C_1F_CA_29_D8_beacon_data-2023-08-08.log"
]

row = 0
for source in list_file:

    print("------------------------------------------------------------------")
    print(source)
    print("------------------------------------------------------------------")
    time.sleep(1)

    # var 
    list_datetime_mac = []
    list_original = []
    count_reach = 0
    count_view = 0
    list_frequency = []
    list_dwelling_time = []
    group = {}


    # READ FILE-----------------------------------------------------------------------------------------------------
    f = open(f"{source}", "r")
    raw_data = f.read()
    parsing_by_line = raw_data.split("\n")
    # READ FILE-----------------------------------------------------------------------------------------------------

    def write(name, content, time_stamp, mode="a"):
        f = open("{}.log".format(name), mode)
        f.write("{} - {}\n".format(time_stamp, content))
        f.close()

    last_hour = ""
    list_ble = []

    # COMBINE WIFI-----------------------------------------------------------------------------------------------------
    for raws in parsing_by_line:
        if raws:
            split_raw = raws.split(" - ")
            if len(split_raw) > 0:
                dt = split_raw[2]
                to_json = json.loads(dt)

                # get string wifi
                datetimes = split_raw[0]
                gets = datetimes.split(" ")
                date_only = gets[0]
                hours = gets[1][0:2]
                date_hour_only = f"{date_only} {hours}"

                # datetimes = to_json["dt"]
                wifi = to_json["wifi"]
                ble = to_json["ble"]
                total_wifi = to_json["total_wifi"]
                total_ble = to_json["total_ble"]
                

                get_wifi_data = True

                if get_wifi_data:
                    # get mac wifi
                    try:
                        split_by_data = wifi.split(";")
                        for dt in split_by_data:

                            split_by_mac = dt.split("-")
                            if len(split_by_mac) > 0:
                                final_mac = split_by_mac[0]
                                powers = split_by_mac[1]

                                if int(powers) < 100:
                                    list_datetime_mac.append("{}={}".format(datetimes, final_mac))
                                    list_original.append(final_mac)

                                    str_datetime = "{}".format(datetimes)
                                    if not str_datetime in group:
                                        resu = final_mac
                                        group[str_datetime] = resu
                                    else:
                                        resu = group[str_datetime]+ ";" + final_mac
                                        group[str_datetime] = resu

                                    save = f"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/wifi/mac_{date_hour_only}"
                                    
                                    update_mac = ':'.join(final_mac[i:i+2] for i in range(0,12,2))
                                    content = f"ADDR={update_mac}, SSID=, RSSI=-{powers}, CH=12, FCTL=4000, DA=, SN=61595, HT=173+186"
                                    
                                    # print(update_mac, " - ", powers)
                                    write(save, content, datetimes)
                                    # print("-> ",check(final_mac))
                                    # row+=1
                                    # worksheet.write(row, 0, row)
                                    # worksheet.write(row, 1, datetimes)
                                    # worksheet.write(row, 2, final_mac)
                                    # worksheet.write(row, 3, powers)
                                    # worksheet.write(row, 4, check(final_mac))
                    except Exception as e:
                        # exc_type, exc_obj, exc_tb = sys.exc_info()
                        # fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        # print("main > ",exc_type, fname, exc_tb.tb_lineno)
                        # print("Error > ", e)
                        pass
                
                else:
                    
                    try:
                        split_by_data = ble.split(";")
                        for dt in split_by_data:

                            # 2023-07-21 09:04:42 - BLE=6a:15:cc:4e:e5:ef, RSSI=-73, NAME=

                            split_by_mac = dt.split("-")
                            if len(split_by_mac) > 0:
                                # if last_hour == hours:
                                final_mac = split_by_mac[0]
                                powers = split_by_mac[1]

                                if not final_mac in list_ble:
                                    list_ble.append(final_mac)

                                print(final_mac, " - ", powers)
                                
                                save = f"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble/mac_{date_hour_only}"
                                
                                update_mac = ':'.join(final_mac[i:i+2] for i in range(0,12,2))
                                content = f"BLE={update_mac}, RSSI=-{powers}, NAME="
                                
                                # print(update_mac, " - ", powers)
                                write(save, content, datetimes)

                                # else:
                                    
                                #     if len(list_ble) > 0:
                                #         save = f"log/cp_ble_{date_only}"                                    
                                #         # update_mac = ':'.join(final_mac[i:i+2] for i in range(0,12,2))
                                #         # content = f"BLE={len(list_ble)}"                                    
                                #         # write(save, content, datetimes)


                                #         # row+=1
                                #         # worksheet.write(row, 0, row)
                                #         # worksheet.write(row, 1, datetimes)
                                #         # worksheet.write(row, 2, len(list_ble))


                                #         list_ble = []
                                #         final_mac = split_by_mac[0]
                                #         list_ble.append(final_mac)

                                # # if hours == "23" or hours == 23:
                                # #     row+=1
                                # #     worksheet.write(row, 0, row)
                                # #     worksheet.write(row, 1, datetimes)
                                # #     worksheet.write(row, 2, len(list_ble))        

                                    

                                # last_hour = hours

                    except Exception as e:
                        pass
               

                    
                    
# workbook.close()