import json
import random
import xlsxwriter

wifi = False

list_file = [
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 00.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 07.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 08.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 09.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 10.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 11.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 12.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 13.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 14.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 15.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 16.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 17.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 18.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 19.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 20.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 21.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 22.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-05 23.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 00.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 01.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 02.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 06.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 07.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 08.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 09.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 10.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 11.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 12.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 13.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 14.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 15.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 16.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 17.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 18.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 19.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 20.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 21.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 22.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-06 23.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 05.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 06.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 07.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 08.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 09.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 10.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 11.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 12.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 13.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 14.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 15.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 16.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 17.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 18.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 19.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 20.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 21.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 22.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-07 23.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 00.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 05.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 06.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 07.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 08.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 09.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 10.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 11.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 12.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 13.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 14.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 15.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 16.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 17.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 18.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 19.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 20.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 21.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 22.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-08 23.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 00.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 05.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 06.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 07.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 08.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 09.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 10.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 11.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 12.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 13.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 14.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 15.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 16.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 17.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 18.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 19.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 20.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 21.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 22.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-09 23.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-10 00.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-10 05.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-10 06.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-10 07.log",
"/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-08-10 08.log"
]

# excel
workbook = xlsxwriter.Workbook('result_convert_beacon_0_wfi_{}.xlsx'.format(random.randint(1,100)))

worksheet = workbook.add_worksheet()
worksheet.write(0, 0, "No")
worksheet.write(0, 1, "Datetime")
worksheet.write(0, 2, "Total")
worksheet.write(0, 3, "A")
worksheet.write(0, 4, "B")
worksheet.write(0, 5, "C")
row = 0
count = 0

last_date = ""
for files in list_file:
    try:
        f = open(f"{files}", "r")
        result = f.read()

        if result:
            result_data = result.split("\n")
            result_process_data = result_data[0]
            raw_dt, data = result_process_data.split(" - ")
            
            convert = json.loads(data)
            # print(data)
            
            datetimes_res = convert["date_time"]
            date_time = datetimes_res.replace("cp_", "")
            
            if wifi:
                total_wifi = convert["total_wifi"]
                # dwelling_wifi = convert["dwelling_wifi"]
                dwelling_wifiA = convert["dwelling_count_wifi"][0]
                dwelling_wifiB = convert["dwelling_count_wifi"][1]
                dwelling_wifiC = convert["dwelling_count_wifi"][2]
            
            else:
                total_wifi = convert["total_ble"]
                dwelling_wifiA = convert["dwelling_count_ble"][0]
                dwelling_wifiB = convert["dwelling_count_ble"][1]
                dwelling_wifiC = convert["dwelling_count_ble"][2]

            print(date_time, " - ", total_wifi, " - ", dwelling_wifiA, dwelling_wifiB, dwelling_wifiC)

            simple_datetime = date_time[0:10] # 2023-07-06 18
            print(simple_datetime)
            if simple_datetime != last_date:
                row+=1
                count = 0

            row+=1
            count+=1
            worksheet.write(row, 0, count)
            worksheet.write(row, 1, date_time)
            worksheet.write(row, 2, total_wifi)
            worksheet.write(row, 3, dwelling_wifiA)
            worksheet.write(row, 4, dwelling_wifiB)
            worksheet.write(row, 5, dwelling_wifiC)

            last_date = simple_datetime

    except Exception as e:
        print("Error :: ", e)

workbook.close()