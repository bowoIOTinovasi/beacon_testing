import os
import re
import datetime

def detail_file(data):
    if data:
        split = data.split("\n")

        if len(split) > 1:
            for dt in split:
                if not "total" in dt:
                    print("")
                    print("Before   - ", dt)
                    remove_space = re.sub(' +', ' ', dt)
                    print("After    - ", remove_space)
                    dt_split_again = remove_space.split(" ")
                    if len(dt_split_again) > 1:
                        # for ddt in dt_split_again:
                            # print("-> ", ddt)
                        # result
                        reg = dt_split_again[0]
                        index = dt_split_again[1]
                        own0 = dt_split_again[2]
                        own1 = dt_split_again[3]
                        size = dt_split_again[4]
                        create_month = dt_split_again[5]
                        create_date = dt_split_again[6]
                        hour = dt_split_again[7]
                        file_name = dt_split_again[8]
                        print(create_date, create_month, hour)
                        print("=> ", dt_split_again)

filess = os.popen("ls -l").read()
detail_file(filess)


# print(filess)
