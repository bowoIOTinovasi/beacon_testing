import os 
import sys
import time
import json
import threading
import globals
import random
import xlsxwriter
from datetime import datetime

class process():
    def __init__(self):
        self.last_hour = 0

        keyss = "12"
        # self.ref_name = "log/mac_raw_2023-06-30 {}.txt".format(keyss)
        self.ref_name = "log/mac_raw_2023-07-07 08.log"

        # excel
        names = self.ref_name.replace(".log", ".xlsx")
        self.workbook = xlsxwriter.Workbook(names)
        self.worksheet = self.workbook.add_worksheet()
        self.worksheet.write(0, 0, "No")
        self.worksheet.write(0, 2, "MAC")
        self.worksheet.write(0, 3, "dBm")

        self.all_mac = {}
        self.serials = []

        self.histoy_mac = ""
        self.histoy_mac_rssi = []

    def run(self):
        print("Start Process")
        self.main()
        time.sleep(1)

    def time_stamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
    
    def date_only(self):
        return datetime.now().strftime("%Y-%m-%d") 
    
    def hour_only(self):
        return datetime.now().strftime("%H")
    
    def time_to_datetime(self, date):
        conv =  datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
        return conv.strftime("%H")

    def write(self, name, datetime, content, mode="a"):
        f = open("{}.log".format(name), mode)
        f.write("{} - {}\n".format(datetime, content))
        f.close()

    def main(self):
        try:
            f = open(self.ref_name, "r")
            raw_seri = f.read()
            raw_serial = raw_seri.split('\n')

            if raw_serial:
                for dt in raw_serial:
                    try:
                        self.serials.append(dt)

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
                                
                                if mac != "" and rssi > 0:
                                    rssi_saved = rssi

                                    if self.histoy_mac == mac:
                                        self.histoy_mac_rssi.append(rssi)
                                    
                                    elif self.histoy_mac != mac:
                                        if self.histoy_mac_rssi:
                                            # self.histoy_mac_rssi.sort()
                                            # mid = len(self.histoy_mac_rssi) // 2
                                            # res = (self.histoy_mac_rssi[mid] + self.histoy_mac_rssi[~mid]) / 2
                                            # rssi_saved = int(res)
                                            rssi_saved = min(self.histoy_mac_rssi)

                                            print("RSSI LIST    -> ", self.histoy_mac_rssi)
                                            print("RSSI RES     -> ", rssi_saved)

                                            # reset penampung rssi
                                            self.histoy_mac_rssi = []
                                            self.histoy_mac_rssi.append(rssi)

                                    if mac in self.all_mac:
                                        dt = []
                                        dt = self.all_mac[mac]
                                        dt.append(rssi_saved)
                                        self.all_mac[mac] = dt
                                        # print(">", dt)
                                    else:
                                        dt = []
                                        dt.append(rssi_saved)
                                        self.all_mac[mac] = dt
                                        # print("", dt)

                                self.histoy_mac = mac
                    except Exception as e:
                        print("Error -> ", e)



        except Exception as e:
            # remove data yang random/acak
            # globals.raw_serial.remove(dt)

            print("Process Error :: main ", e)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print("Process Error :: main ",exc_type, fname, exc_tb.tb_lineno)
            return None
        
    def filters(self):
        row = 0
        for dd in self.all_mac:
            print("--------------------")
            print(dd)
            
            row+=1
            self.worksheet.write(row, 0, row)

            if dd in globals.klampis:
                cf = self.workbook.add_format({'bg_color': 'red'})
                self.worksheet.write(row, 1, dd, cf)
                
            else:
                self.worksheet.write(row, 1, dd)
            
            col = 2
            for dt in self.all_mac[dd]:
                print(dt)
                if dt >= globals.min_sp_small and dt < globals.max_sp_small:
                    cf = self.workbook.add_format({'bg_color': 'green'})
                    self.worksheet.write(row, col, dt, cf)
                elif dt >= globals.min_sp_big and dt < globals.max_sp_big:
                    cf = self.workbook.add_format({'bg_color': 'yellow'})
                    self.worksheet.write(row, col, dt, cf)
                else:
                    self.worksheet.write(row, col, dt)


                col+=1

            print("")
        
        self.workbook.close()


if __name__ == "__main__":
    dt = process()
    dt.main()
    dt.filters()