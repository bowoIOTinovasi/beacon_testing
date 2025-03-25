import os 
import sys
import time
import json
import threading
import globals
from datetime import datetime

class process():
    def __init__(self):
        self.last_hour = 0

        keyss = "12"
        self.names = "log/mac_raw_2023-06-30 {}.txt".format(keyss)

    def run(self):
        print("Start Process")
        self.main()
        time.sleep(1)

    def time_stamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    
    def time_stamp_details(self):
        return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3] 
    
    def date_only(self):
        return datetime.now().strftime("%Y-%m-%d") 
    
    def hour_only(self):
        return datetime.now().strftime("%H")
    
    def time_to_datetime_hour(self, date):
        conv =  datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return conv.strftime("%H")
    
    def time_to_datetime(self, date):
        return datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    
    def range_datetime(self, first, second):
        return abs((first - second).total_seconds())

    def write(self, name, datetime, content, mode="a"):
        f = open("{}.txt".format(name), mode)
        f.write("{} - {}\n".format(datetime, content))
        f.close()

    def filters(self):
        for mac in globals.all_mac:
            param_count_small = 0 
            param_start_big = False

            for rssi in globals.all_mac[mac]:
            
                if rssi >= globals.min_sp_big and rssi < globals.max_sp_big and param_start_big == True:
                    param_count_small = 0
                    param_start_big = False

                if rssi >= globals.min_sp_big and rssi < globals.max_sp_big and param_start_big == False:
                    param_start_big = True
                
                if rssi >= globals.min_sp_small and rssi < globals.max_sp_small:
                    
                    if param_start_big:
                        param_count_small += 1
                        
                        if not mac in globals.result_all_mac and param_count_small > 1:
                            globals.total_wifi += 1

                            globals.result_all_mac.append(mac)
                        
                            print("")
                            print("WiFi = ", globals.total_wifi)
                            print("Mac -> ", mac)
                            print("")

    def main(self):
        try:
            # mac_result = "log/klampis mac_result_{}_{}".format(keyss, self.date_only())

            f = open(self.names, "r")
            raw_seri = f.read()
            raw_serial = raw_seri.split('\n')

            if raw_serial:
                for dt in raw_serial:
                    get_date = dt.split(" - ")
                    split_data = dt.split(',')
                    
                    if len(split_data) > 3:
                        raw_date_time = split_data[0].split(" - ")
                        date_time = raw_date_time[0]
                        
                        if "ADDR=" in split_data[0] and "RSSI=" in split_data[2]:
                            split_ = split_data[0].split("=")
                            mac = split_[1]

                            split__ = split_data[2].split("=")
                            rssi_negatif = split__[1][0:3]
                            if rssi_negatif:
                                try:
                                    rssi_ = int(rssi_negatif) * -1
                                    rssi = int(rssi_)
                                except:
                                    pass
                        
                            if rssi > 0 and mac != "":
                                if mac in globals.all_mac:                                    
                                    dt = []
                                    dt = globals.all_mac[mac]
                                    dt.append(rssi)
                                    globals.all_mac[mac] = dt
                                
                                else:
                                    dt = []
                                    dt.append(rssi)
                                    globals.all_mac[mac] = dt

                self.filters()

        except Exception as e:
            # remove data yang random/acak
            # globals.raw_serial.remove(dt)

            print("Process Error :: main ", e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Process Error :: main ",exc_type, fname, exc_tb.tb_lineno)
            return None
        

if __name__ == "__main__":
    dt = process()
    dt.main()