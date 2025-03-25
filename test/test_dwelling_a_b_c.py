import json
import random
import xlsxwriter

wifi = False
# list_file = [
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 06.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 07.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 08.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 09.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 10.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 11.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 12.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 13.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 14.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 15.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 16.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 17.log",
#     "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 18.log"
# ]
list_file = [
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 06.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 07.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 08.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 09.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 10.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 11.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 12.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 13.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 14.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 15.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 16.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 17.log",
    "/home/interads/Documents/interads/beacon/beacon_v2.1/main/log/ble_result/mac_2023-07-30 18.log"
]

# excel
workbook = xlsxwriter.Workbook('result_convert_beacon_{}.xlsx'.format(random.randint(1,100)))

worksheet = workbook.add_worksheet()
worksheet.write(0, 0, "No")
worksheet.write(0, 1, "Datetime")
worksheet.write(0, 2, "Total")
worksheet.write(0, 3, "Dwelling")
row = 0
count = 0

layer_1 = [0, 30, "A"]
layer_2 = [31, 300, "B"]
layer_3 = [301, 3600, "C"]

last_date = ""
for files in list_file:
    try:
        dwelling_count = []
        all_data = {}

        f = open(f"{files}", "r")
        result = f.read()

        if result:
            result_data = result.split("\n")
            result_process_data = result_data[1]
            raw_dt, data = result_process_data.split(" - ")
            
            
            convert = json.loads(data)
            list_mac = convert["duration"]
            
            if list_mac:

                for mac in list_mac:
                    duration = list_mac[mac]["duration"]

                    if wifi:
                        final_duration = list_mac[mac]["final_duration"]
                        
                        count += 1
                        # print(count, ". mac - ", mac, " - ", duration, " - ", final_duration)

                        if final_duration <= 3600:
                            if duration >= layer_1[0] and duration <= layer_1[1]:
                                if layer_1[2] in all_data:
                                    dt = []
                                    dt = list(all_data[layer_1[2]])
                                    dt.append(duration)
                                    all_data[layer_1[2]] = dt
                                
                                else:
                                    dt = []
                                    dt.append(duration)
                                    all_data[layer_1[2]] = dt

                            else:
                                if not layer_1[2] in all_data:
                                    dt = []
                                    all_data[layer_1[2]] = dt

                            if duration >= layer_2[0] and duration <= layer_2[1]:
                                if layer_2[2] in all_data:
                                    dt = []
                                    dt = list(all_data[layer_2[2]])
                                    dt.append(duration)
                                    all_data[layer_2[2]] = dt
                                
                                else:
                                    dt = []
                                    dt.append(duration)
                                    all_data[layer_2[2]] = dt
                            else:
                                if not layer_2[2] in all_data:
                                    dt = []
                                    all_data[layer_2[2]] = dt
                            
                            
                            if duration >= layer_3[0] and duration <= layer_3[1]:
                                if layer_3[2] in all_data:
                                    dt = []
                                    dt = list(all_data[layer_3[2]])
                                    dt.append(duration)
                                    all_data[layer_3[2]] = dt
                                
                                else:
                                    dt = []
                                    dt.append(duration)
                                    all_data[layer_3[2]] = dt
                            else:
                                if not layer_3[2] in all_data:
                                    dt = []
                                    all_data[layer_3[2]] = dt
                    
                    else:
                        count += 1
                        # print(count, ". mac - ", mac, " - ", duration, " - ", final_duration)

                        if duration >= layer_1[0] and duration <= layer_1[1]:
                            if layer_1[2] in all_data:
                                dt = []
                                dt = list(all_data[layer_1[2]])
                                dt.append(duration)
                                all_data[layer_1[2]] = dt
                            
                            else:
                                dt = []
                                dt.append(duration)
                                all_data[layer_1[2]] = dt
                        else:
                            if not layer_1[2] in all_data:
                                dt = []
                                all_data[layer_1[2]] = dt

                        if duration >= layer_2[0] and duration <= layer_2[1]:
                            if layer_2[2] in all_data:
                                dt = []
                                dt = list(all_data[layer_2[2]])
                                dt.append(duration)
                                all_data[layer_2[2]] = dt
                            
                            else:
                                dt = []
                                dt.append(duration)
                                all_data[layer_2[2]] = dt
                        else:
                            if not layer_2[2] in all_data:
                                dt = []
                                all_data[layer_2[2]] = dt
                        
                        
                        if duration >= layer_3[0] and duration <= layer_3[1]:
                            if layer_3[2] in all_data:
                                dt = []
                                dt = list(all_data[layer_3[2]])
                                dt.append(duration)
                                all_data[layer_3[2]] = dt
                            
                            else:
                                dt = []
                                dt.append(duration)
                                all_data[layer_3[2]] = dt
                        else:
                            if not layer_3[2] in all_data:
                                dt = []
                                all_data[layer_3[2]] = dt
                                    
        # print(json.dumps(all_data))
        for dw in sorted(all_data.keys()):
            # print(dw ," - ", all_data[dw], " - ", len(all_data[dw]))
            dwelling_count.append(len(all_data[dw]))

        total = sum(dwelling_count)
        print(total , " - ", dwelling_count)
        # print()

    except Exception as e:
        print("Error :: ", e)