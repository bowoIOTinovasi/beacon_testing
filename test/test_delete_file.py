import os
import time
import json
import global_function

gf = global_function.globalFunction("test_delete_file")

count_deleted = 0
max_count_deleted = 1
list_unique = []

# check file
base_log = "log"
base_path = ["log/ble", "log/wifi"]
ble_result = "log/ble_result"
wifi_result = "log/wifi_result"

max_size = 400

while True:
    # check size
    size_ble = gf.get_size(base_log)
    print(size_ble)

    if size_ble > max_size:

        for path in base_path:
            count_deleted = 0
            list_unique = []

            list_file = gf.list_file_in_folder(path)
            for dt in list_file:
                path_date, _ = dt.split(" ")

                if not path_date in list_unique:
                    list_unique.append(path_date)

            # print(json.dumps(list_file, indent=4))
            # print(json.dumps(list_unique, indent=4))

            for date in list_unique:
                for file_deleted in list_file:
                    if count_deleted < max_count_deleted:
                        if date in file_deleted:
                            # base folder
                            os.remove(file_deleted)

                            # result folder
                            if "wifi" in path:
                                repl = file_deleted.replace(path, wifi_result)
                                os.remove(repl)
                                print("=>", file_deleted, " - ", repl)

                            else:
                                repl = file_deleted.replace(path, ble_result)
                                os.remove(repl)
                                print("->", file_deleted, " - ", repl)

                        size_ble = gf.get_size(base_log)
                        print(size_ble)
                        break

                count_deleted += 1
    
    time.sleep(1)