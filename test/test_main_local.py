import json
import time
import serial
import threading
from datetime import datetime
import argparse

import globals
import sniff_process
import sniff_count
import sniff_sender

class main_program(object):
    def __init__(self):
        self.setup()

        globals.running_local = True
        self.ap_name = "config/list_accesspoint"

    def setup(self):
        print("Setup")
        
        parser = argparse.ArgumentParser(description='File name')
        parser.add_argument('-f', '--file', type=str, required=False, help='File name')

        # Parse command line arguments
        args = parser.parse_args()

        # Extract argument values
        namess = args.file  # Convert ticker to uppercase

        globals.prefix = "data_cp_"
        self.names = f"{namess}" # log/cp_2023-06-08.log
        # self.connect_sensor()

        self.process = sniff_process.process(threading.currentThread())
        self.counts = sniff_count.count(threading.currentThread())
        self.sender = sniff_sender.sender_and_receiver(threading.currentThread())

        print("Setup Done")

    def connect_sensor(self):
        try:
            self.raw_data = serial.Serial(
                '/dev/ttyUSB0',
                baudrate=115200,
                timeout=1
            )
            self.raw_data.reset_input_buffer()
            time.sleep(3)
        except Exception as e:
            print("main.py::connect_sensor > ", e)

            self.raw_data = serial.Serial(
                '/dev/ttyUSB1',
                baudrate=115200,
                timeout=1
            )
            self.raw_data.reset_input_buffer()
            time.sleep(3)
        


    def get_value(self):
        try:
            receiver = self.raw_data.readline().decode('ascii')
            return receiver
        
        except Exception as e:
            print("Main Error :: get_value ", e)
            return None
        
    def time_stamp(self):
        if not globals.running_local:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 
        
        else:
            dd = datetime.strptime(globals.datetime_local, "%Y-%m-%d %H:%M:%S")
            return dd

    def date_only(self):
        if not globals.running_local:
            return datetime.now().strftime("%Y-%m-%d %H") 

        else:
            dd = datetime.strptime(globals.datetime_local, "%Y-%m-%d %H:%M:%S")
            return dd.strftime("%Y-%m-%d %H") 
        
    def write(self, name, content, mode="a"):
        f = open("{}.log".format(name), mode)
        f.write("{} - {}\n".format(self.time_stamp(), content))
        f.close()

    def read(self, name):
        f = open(name, "r")
        res = f.read()
        return res
    
    def read_setting(self):
        try:
            dd = self.read("config/setting.json")
            if dd:
                print("Config > ", dd)

                procc = json.loads(dd)

                # share
                globals.mqtt_server = procc["data"]["mqtt_server"]
                globals.trigger_sending = procc["data"]["interval"]
                
                globals.min_sp_small = procc["data"]["wifi"]["min_small_frame"]
                globals.max_sp_small = procc["data"]["wifi"]["max_small_frame"]
                globals.min_sp_big = procc["data"]["wifi"]["min_big_frame"]
                globals.max_sp_big = procc["data"]["wifi"]["max_big_frame"]
                
                globals.min_spb_small = procc["data"]["ble"]["min_small_frame"]
                globals.max_spb_small = procc["data"]["ble"]["max_small_frame"]
                globals.min_spb_big = procc["data"]["ble"]["min_big_frame"]
                globals.max_spb_big = procc["data"]["ble"]["max_big_frame"]
        
        except Exception as e:
            print("main.py::read setting > ", e)
    
    def read_accesspoint(self):
        dt = self.read("{}.log".format(self.ap_name))
        if dt:
            try:
                if " - " in dt:
                    split = dt.split(" - ")
                    globals.all_ap = json.loads(split[1])
                    print()
                    print("Load AP > ", globals.all_ap)
                    print()
                    

            except Exception as e:
                print("main.py::64 > ", e)

    def start_all_thread(self):
        # thread child
        self.process.start()
        self.counts.start()
        # self.sender.start()

    def watchdog(self):
        if not self.process.is_alive():
            self.process = sniff_process.process(threading.currentThread())
            self.process.start()
        
        if not self.counts.is_alive():
            self.counts = sniff_count.count(threading.currentThread())
            self.counts.start()

        if not self.sender.is_alive():
            self.sender = sniff_sender.sender_and_receiver(threading.currentThread())
            self.sender.start()

    def main(self):
        # read accesspoint
        self.read_accesspoint()

        # read setting
        self.read_setting()

        # start all child beacon
        self.start_all_thread()

        f = open(self.names, "r")
        raw_seri = f.read()
        raw_serial = raw_seri.split('\n')
        for raw in raw_serial:
            try:
                if str(raw) != "" or str(raw) != None:
                    dd = str(raw).split(" - ")
                    globals.datetime_local = dd[0]

                    
                    if "ADDR" in str(raw) and "RSSI" in str(raw) and "SSID" in str(raw):
                        # print(">> ", raw)
                        globals.raw_serial.append(str(raw))
                        # self.write(mac_raw, "{}".format(str(raw.replace("\n", ""))))
                    
                    elif "BEAC" in str(raw) and "RSSI" in str(raw):
                        split_data = raw.split(',')
                        split_ = split_data[0].split("=")
                        mac = split_[1]
                        if not mac in globals.all_ap:
                            globals.all_ap.append(mac)
                            # write mac here
                            save = json.dumps(globals.all_ap)
                            # self.write(self.ap_name, save, "w")

                    elif "BLE" in str(raw) and "RSSI" in str(raw):
                        # print("BLEE > ", str(raw))
                        globals.raw_serial.append(str(raw))
                        # self.write(mac_raw, "{}".format(str(raw.replace("\n", ""))))

                    elif "SSID" in str(raw) and "PASS" in str(raw):
                        split_data = raw.split(',')
                        split_ssid = split_data[0].split("=")
                        ssid = split_ssid[1]

                        split_pass = split_data[1].split("=")
                        password = split_pass[1]


                    # else:
                        # if str(raw) != None or str(raw) != "":
                        #     self.write(mac_raw, "{}".format(str(raw.replace("\n", ""))))
            
            except Exception as e:
                # if "device disconnected or multiple access on port" in str(e):
                    # self.connect_sensor()

                print("main.py::main ", e)

            time.sleep(0.001)

if __name__ == "__main__":
    main = main_program()
    main.main()