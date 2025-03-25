import os 
import sys
import time
import json
import threading
import statistics

import globals
import global_function

class process(threading.Thread):
    '''
    class ini memiliki beberapa logic.
    
    1. logic untuk counting mode
    2. logic untuk indoor tracking mode

    task :
    -- logic untuk counting mode
        -- standby dan cek kondisi jika ada pergantian jam (semisal dari jam 8 ke jam 9) - "check_data_before_process()".
        -- jika ada pergantian jam, maka akan ada pengecekan di folder "log/ble dan log/wifi", jika file yang ada di folder tersebut  
            belum ada di folder "log/ble_result dan log/wifi_result", maka check_data_before_process() memberikan respon berupa list 
            file yang belum ada di folder "log/ble_result dan log/wifi_result.
        -- setelah mendapatkan list file yang belum terproses, langkah selanjutnya membaca file (log) dan di pilah-pilah sesuai
            mac-address (unique)
        -- selanjutnya data di loop untuk dipilah lagi sebanyak 2x
            -- filter berdasarkan RSSI
            -- filter bedasarkan durasi
        -- finish
    
    -- logic untuk indoor tracking
        -- standby dan hanya BLE saja yang bekerja.
        -- jika ada tag yang sudah di daftarkan dan melintas di area beacon, maka tag tersebut akan di record.
        -- finish
    '''
    
    def __init__(self, parent):
        ''' init global variable '''
        threading.Thread.__init__(self)

        self.gf = global_function.globalFunction("process")                             # init global function
        
        self.parent = parent
        self.pass_counting_noise = 3600                                                 # filter duration untuk proses tiap jam 60 menit, lebih dari value ini akan di abaikan
        
        self.menit_trigger_count = 1                                                    # variable ini terhubung dengan kapan counting di mulai. kalau valuenya 1, 60 * 1 (menit ke 60 dengan dikurangi 10 second "50 - 60")
        ''''''



    def run(self):
        '''
        Fungsi ini bagian dari threading.Thread, jika main di activate, maka run ini akan tertrigger, dan akan looping hingga parent off.

        FUNCTION    : run()
        RESPONSE    : None
        TYPE RESP   : None
        '''
        self.gf.dd("Start Process")
        time.sleep(3)

        while self.parent.is_alive():
            self.main()
            time.sleep(2)
        self.gf.dd("Kill Process")



    def main(self):
        '''
        Fungsi ini digunakan sebagai pemrosesan utama (forever loop), loop ini akan destroy jika parent (main.py) sudah tidak aktif.

        FUNCTION    : main()
        RESPONSE    : None
        TYPE RESP   : None
        '''

        if not globals.indoortracking_mode:                                             # kondisi jika ada di mode counting
            list_wifi = self.check_data_before_process()                                # check pergantian jam dan cek folder result
            
            count_total_wifi = 0                                                        # untuk menampung total counting
            count_total_ble = 0
            list_mac_wifi = []                                                          # untuk menampung list mac address yang tercounting
            list_mac_ble = []
            obj_mac_wifi = {}                                                           # untuk menampung list mac address with  start and end duration
            obj_mac_ble = {} 
            dwelling_wifi= 0                                                            # untuk menampung dwelling time (median)
            dwelling_wifi_mean = 0                                                      # untuk menampung dwelling time (avg)
            dwelling_ble = 0
            dwelling_ble_mean = 0
            dwelling_count_wifi = []                                                    # untuk menampung dwelling count [0, 0, 0] 
            dwelling_count_ble = []

            if list_wifi:                                                               
                for list_wifi_file in list_wifi:                                        # jika terdapat file yang belum terproses, maka looping ini akan berjalan
                    list_wifi_sorted = self.sort_data_and_save_to_variable_wifi(list_wifi_file) # keterangan ada di dalam fungsi
                    count_total_wifi, list_mac_wifi, obj_mac_wifi, dwelling_wifi, dwelling_wifi_mean = self.count_wifi(list_wifi_sorted, list_wifi_file, list_wifi)    
                    dwelling_count_wifi, _ = self.get_dwelling_count(obj_mac_wifi)

                    # generate datetime
                    clean0 = list_wifi_file.replace("log/wifi/", "")
                    clean1 = clean0.replace(".log", f":{self.gf.minute_only()}:{self.gf.second_only()}")
                    date_time = clean1.replace("mac_", "")

                    # generate name and save wifi result
                    nam = list_wifi_file.replace("log/wifi/", "log/wifi_result/")
                    name = nam.replace(".log", "")
                    content = {
                        "date_time": date_time,
                        "total_wifi": count_total_wifi,
                        "dwelling_wifi": dwelling_wifi,
                        "dwelling_wifi_mean": dwelling_wifi_mean,
                        "dwelling_count_wifi": dwelling_count_wifi,
                        "list_wifi": list_mac_wifi
                    }
                    content_time = {
                        "duration": obj_mac_wifi
                    }
                    self.gf.write_log(name, json.dumps(content), "w")
                    self.gf.write_log(name, json.dumps(content_time))

                    # send data
                    clean0 = list_wifi_file.replace("log/wifi/", "")
                    keys = clean0.replace(".log", "")
                    # globals.wifi_count_list.append(content)
                    
                    # ----------------------------------------------------------------------------------------------------------

                    try:
                        list_ble_file = list_wifi_file.replace("log/wifi/", "log/ble/")
                        list_ble_sorted = self.sort_data_and_save_to_variable_ble(list_ble_file) # keterangan ada di dalam fungsi
                        count_total_ble, list_mac_ble, obj_mac_ble, dwelling_ble, dwelling_ble_mean = self.count_ble(list_ble_sorted)    
                        dwelling_count_ble, _ = self.get_dwelling_count(obj_mac_ble)
                        # self.gf.dd(f"")
                        # self.gf.dd(f"BLE > {list_ble_file} - {count_total_ble} = {list_mac_ble}")
                        # self.gf.dd(f"")

                        # generate datetime
                        clean0 = list_ble_file.replace("log/ble/", "")
                        clean1 = clean0.replace(".log", f":01:01")
                        date_time = clean1.replace("mac_", "")

                        # generate name and save wifi result
                        nam = list_ble_file.replace("log/ble/", "log/ble_result/")
                        name = nam.replace(".log", "")
                        content = {
                            "date_time": date_time,
                            "total_ble": count_total_ble,
                            "dwelling_ble": dwelling_ble,
                            "dwelling_ble_mean": dwelling_ble_mean,
                            "dwelling_count_ble": dwelling_count_ble,
                            "list_ble": list_mac_ble
                        }
                        content_time = {
                            "duration": obj_mac_ble
                        }
                        self.gf.write_log(name, json.dumps(content), "w")
                        self.gf.write_log(name, json.dumps(content_time))

                    except Exception as e:
                        self.gf.dd(f"main :: {e}")
                        count_total_ble = 0
                        dwelling_ble = 0

                    # send data
                    clean0 = list_ble_file.replace("log/ble/", "")
                    keys = clean0.replace(".log", "") 

                    sv = {
                        "count_wifi": count_total_wifi,
                        "count_ble": count_total_ble,
                        "date_time": date_time,
                        "dwelling_ble": dwelling_ble,
                        "dwelling_wifi": dwelling_wifi,
                        "dwelling_count_wifi": dwelling_count_wifi,
                        "dwelling_count_ble": dwelling_count_ble
                    }
                    globals.wifi_ble_count_list.append(sv)

                    globals.send_data = True

                    globals.send_total_wifi = count_total_wifi
                    globals.send_total_ble = count_total_ble
                    globals.send_dwelling_wifi = dwelling_wifi
                    globals.send_dwelling_ble = dwelling_ble
                    globals.send_datetime = date_time
                    globals.send_dwelling_count_wifi = list(dwelling_count_wifi)
                    globals.send_dwelling_count_ble = list(dwelling_count_ble)

                    time.sleep(10)

        else:

            self.indoor_tracking_mode()
            time.sleep(1)



    def check_data_before_process(self):
        '''
        Fungsi ini digunakan untuk check jika ada pergantian jam maka script akan 
        berjalan untuk membaca list file pada folder ble/wifi, dan membandingkan 
        jika didalam folder log/ble_result dan log/wifi_result tidak ada, maka 
        file tersebut akan di masukkan kedalam list_files untuk response.

        FUNCTION    : check_data_before_process()
        RESPONSE    : ["log/wifi/xxx.log"]
        TYPE RESP   : list
        '''

        list_files = []

        wifi_result = self.gf.list_file_in_folder("log/wifi_result")                    # check file di folder ble_result/wifi_result (result)
        try:
            if wifi_result:                                                             # ini kondisi saat folder result sudah ada isinya
                list_wifis = self.gf.list_file_in_folder("log/wifi")                    # check file di folder log wifi/ble (raw)
                if len(list_wifis) > 0:
                    for log_wifi in list_wifis:                                         
                        # change path header
                        log_file_wifi = log_wifi.replace("log/wifi", "log/wifi_result") # sesuaikan nama agar mudah dalam membandingkan
                        if not log_file_wifi in wifi_result:                            # jika sama maka diabaikan, jika beda maka di simpan di list_files
                            
                            convert = self.menit_trigger_count * 60
                            convert_min = convert - 10
                            if self.gf.minute_only_to_seconds() >= convert_min and self.gf.minute_only_to_seconds() <= convert: # menit ke 59 dengan toleransi 10 second
                                if not self.gf.time_stamp_hour_only() in log_wifi:      # kondisi ini digunakan untuk meghidari file log yang masih berjalan / masih berjalan dijam tersebut.
                                    self.gf.dd(f"BLE -> {log_wifi}")
                                    list_files.append(log_wifi)                         # simpan path yang tidak ada dalam result

            else:                                                                       # ini kondisi saat folder kosong, kalau saat folder kosong, file yang ada di log wifi/ble langsung dilist semua. tanpa menunggu perpindahan jam.
                list_wifis = self.gf.list_file_in_folder("log/wifi")                    
                if len(list_wifis) > 0:# simpan path yang tidak ada dalam result
                    for log_wifi in list_wifis:
                        if not self.gf.time_stamp_hour_only() in log_wifi:              # kondisi ini digunakan untuk meghidari file log yang masih berjalan / masih berjalan dijam tersebut.
                            self.gf.dd(f"WiFi -> {log_wifi}")
                            list_files.append(log_wifi)                                 # simpan path yang tidak ada dalam result
                            
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.gf.dd(f"check_data_before_process :: try 1 :: {exc_type} - {fname} - {exc_tb.tb_lineno} - {exc_obj}")

        return list_files
    


    def sort_data_and_save_to_variable_wifi(self, list_wifi_name):
        '''
        Fungsi ini bertugas untuk membaca isi file .log, dan memilah isi serta memasukkan hasilnya 
        kedalam bentuk object.

        FUNCTION    : sort_data_and_save_to_variable_wifi(list_wifi_name)
        RESPONSE    : {"macaddress": [{"dt": "YYYY-MM-DD hh:mm:ss", "rssi": 10}, {"dt": "YYYY-MM-DD hh:mm:ss", "rssi": 20}]}
        TYPE RESP   : object

        1. list_wifi_name    : path file yang akan di process (.log)
        '''

        result_wifi = {}

        self.gf.dd(f"Wifi Name - {list_wifi_name}")
        read_data = self.gf.read(list_wifi_name)                                        # baca file .log
        if read_data:
            data_split_by_enter = read_data.split("\n")                                 # data di pisahkan berdasarkan enter \n
            for data in data_split_by_enter:
                base_data = data.split(" - ")                                           # pisahkan juga (datetime - ADDRxx,RSSIxx) berdasarkan "-" untuk mengambil datetime dan data
                date_time_from_data = base_data[0]                                      # ambil reverensi datetime saat data diperoleh

                mac_address_from_data = None                                            # init var untuk tampung mac
                rssi_from_data = None                                                   # init var untuk tampung rssi
                
                
                split_base_data = data.split(",")                                       # pisahkan berdasarkan ",". ini bertujuan untuk mengambil MAC dan RSSI
                try:
                    if "ADDR=" in split_base_data[0] and "RSSI=" in split_base_data[2]: # check berdasarkan header, jika keduanya ada, lanjut process
                        split_mac = split_base_data[0].split("=")                       # split untuk ambil mac 
                        mac = split_mac[1]
                        if len(mac) >= 16:                                              # pastikan ada 16 digit
                            mac_address_from_data = mac

                        split_rssi = split_base_data[2].split("=")                      # split ambil rssi
                        rssi_negatif = split_rssi[1][0:3]
                        if rssi_negatif:
                            try:
                                rssi_neg = int(rssi_negatif) * -1                       # ubah dari nilai negatif ke positif
                                rssi_from_data = int(rssi_neg)
                            
                            except:
                                rssi_from_data = ""
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    self.gf.dd(f"sort_data_and_save_to_variable_wifi :: inside loop :: {exc_type} - {fname} - {exc_tb.tb_lineno} - {split_base_data}")
                    pass


                
                if date_time_from_data and mac_address_from_data and rssi_from_data:    # jika semua data lengkap, maka masuk proses selanjutnya
                    dump_data = []
                    save_data = {
                        "dt": date_time_from_data,
                        "rssi": rssi_from_data
                    }
                    if not mac_address_from_data in result_wifi:
                        dump_data.append(save_data)
                        result_wifi[mac_address_from_data] = dump_data
                    
                    else:
                        dump_data = result_wifi[mac_address_from_data]
                        dump_data.append(save_data)
                        result_wifi[mac_address_from_data] = dump_data

        return result_wifi
    
        

    def sort_data_and_save_to_variable_ble(self, list_ble_name):
        '''
        Fungsi ini bertugas untuk membaca isi file .log, dan memilah isi serta memasukkan hasilnya 
        kedalam bentuk object.

        FUNCTION    : sort_data_and_save_to_variable_ble(list_ble_name)
        RESPONSE    : {"macaddress": [{"dt": "YYYY-MM-DD hh:mm:ss", "rssi": 10}, {"dt": "YYYY-MM-DD hh:mm:ss", "rssi": 20}]}
        TYPE RESP   : object

        1. list_ble_name    : path file yang akan di process (.log)
        '''

        result_ble = {}

        self.gf.dd(f"ble Name - {list_ble_name}")
        read_data = self.gf.read(list_ble_name)                                         # baca file .log
        if read_data:
            data_split_by_enter = read_data.split("\n")                                 # data di pisahkan berdasarkan enter \n
            for data in data_split_by_enter:
                base_data = data.split(" - ")                                           # pisahkan juga (datetime - ADDRxx,RSSIxx) berdasarkan "-" untuk mengambil datetime dan data
                date_time_from_data = base_data[0]                                      # ambil reverensi datetime saat data diperoleh

                mac_address_from_data = None                                            # init var untuk tampung mac
                rssi_from_data = None                                                   # init var untuk tampung rssi
                
                
                split_base_data = data.split(",")                                       # pisahkan berdasarkan ",". ini bertujuan untuk mengambil MAC dan RSSI
                try:
                    if "BLE=" in split_base_data[0] and "RSSI=" in split_base_data[1]:  # check berdasarkan header, jika keduanya ada, lanjut process
                        split_mac = split_base_data[0].split("=")                       # split untuk ambil mac 
                        mac = split_mac[1]
                        if len(mac) >= 16:                                              # pastikan ada 16 digit
                            mac_address_from_data = mac

                        split_rssi = split_base_data[1].split("=")                      # split ambil rssi
                        rssi_negatif = split_rssi[1][0:3]
                        if rssi_negatif:
                            try:
                                rssi_neg = int(rssi_negatif) * -1                       # ubah dari nilai negatif ke positif
                                rssi_from_data = int(rssi_neg)
                            
                            except:
                                rssi_from_data = ""
                except Exception as e:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    self.gf.dd(f"sort_data_and_save_to_variable_ble :: inside loop :: {exc_type} - {fname} - {exc_tb.tb_lineno} - {split_base_data}")
                    pass

                
                if date_time_from_data and mac_address_from_data and rssi_from_data:    # jika semua data lengkap, maka masuk proses selanjutnya
                    dump_data = []
                    save_data = {
                        "dt": date_time_from_data,
                        "rssi": rssi_from_data
                    }
                    if not mac_address_from_data in result_ble:
                        dump_data.append(save_data)
                        result_ble[mac_address_from_data] = dump_data
                    
                    else:
                        dump_data = result_ble[mac_address_from_data]
                        dump_data.append(save_data)
                        result_ble[mac_address_from_data] = dump_data

        return result_ble
        
    
    def count_wifi(self, list_wifi_sorted, list_wifi_file, list_wifi):
        '''
        Fungsi ini berfungsi sebagai counting dan menentukan apakah mac tersebut masuk 
        kreiteria atau tidak :
        
        adapun kriteria yang ditanamkan adalah :
            -- jika mac address powernya kurang dari batas B (terhitung)
            -- dan data yang di proses dibandingkan dengan jam sebelumnya, semisal yang mau 
                di proses jam 4, maka data jam 3 akan di baca dahulu, lalu data jam 4 dibandingkan 
                jika di jam 4 ada data yang dari jam 3, lalu durasinya di tambahkan. jika durasi 
                lebih dari > set point (variable pass_counting_noise) maka di abaikan.

        FUNCTION    : count_wifi(list_wifi_sorted, list_wifi_file, list_wifi)
        RESPONSE    : 0, ["mac1", "mac2"], {"mac_address": {"start": "2023-08-24 07:00:14", 
                        "end": "2023-08-24 07:52:57", "duration": 3163, "final_duration": 3163}, 0, 0
        TYPE RESP   : int, list, object, int, int (multiple response)

        1. list_wifi_sorted     : list mac_address yang sudah di urutkan dan dirapikan dari fungsi 
                                    sort_data_and_save_to_variable_ble()
        2. list_wifi_file       : log file yang sedang di process saat ini
        3. list_wifi            : list log file yang sudah terrecord di folder log wifi/ble
        '''

        try:
            obj_mac_wifi = {}
            list_mac_wifi = []
            count_total_wifi = 0
            list_duration_wifi = []
            dwelling_time = 0
            dwelling_time_mean = 0
            list_mac = []

            # --------------------------------------------------------------------------------------------------------------------------------
            
            list_prev_data = {}                                                         # untuk menampung durasi
            index_file = list_wifi.index(list_wifi_file)                                # fungsi untuk mencari urutan index list berapa file yang di process

            if index_file > 0:                                              
                file_name = list_wifi[index_file - 1]                                   # fungsi untuk mengambil result 1 jam sebelum file yang di process
                file_name_result = file_name.replace("wifi/", "wifi_result/")           # samakan nama agar mudah untuk membandingkan
                f = open(f"{file_name_result}", "r")    
                result = f.read()                                                       # baca file 1 jam sebelum file yang di process

                if result:                  
                    result_data = result.split("\n")
                    result_process_data = result_data[1]
                    _, data = result_process_data.split(" - ")
                    
                    convert = json.loads(data)
                    list_mac = convert["duration"]                                      # ambil durasi dari file result untuk di tambahkan dengan durasi jam yang akan di proses
                    
                    if list_mac:
                        for mac in list_mac:
                            duration = list_mac[mac]["duration"]
                            
                            if not mac in list_prev_data and duration:
                                list_prev_data[mac] = duration                          # simpan semua durasi dalam bentu object dengan key mac-address
            
            # --------------------------------------------------------------------------------------------------------------------------------

            if list_wifi_sorted:                                                        # baca list jam yang akan di proses dan sudah di urutkan sebelumnya

                ''' FILTER 1 ----------------------------------------------------------------------------------------------------------'''
                for mac_address in list_wifi_sorted:                                    # loop untuk filter berdasarkan lingkaran B (terehitung)
                    for detail in list_wifi_sorted[mac_address]:            
                        date_time = detail["dt"]
                        rssi = int(detail["rssi"])

                        # no filter A and B using small only
                        if rssi >= globals.min_sp_small and rssi < globals.max_sp_small:    # jika power (rssi) masuk diantara configurasi
                            if not mac_address in list_mac_wifi:                            # simpan mac (unique)
                                list_mac_wifi.append(mac_address)

                ''' FILTER 2 ----------------------------------------------------------------------------------------------------------'''
                for mac_address in list_wifi_sorted:                                        # loop untuk mencari durasi dan di tambahkan durasi dari jam sebelumnya          
                    start_detected = None
                    end_detected = None

                    for detail in list_wifi_sorted[mac_address]:
                        date_time = detail["dt"]
                        rssi = int(detail["rssi"])

                        # save start detected and end detected
                        if mac_address in list_mac_wifi:
                            if not start_detected:
                                start_detected = date_time
                            end_detected = date_time

                    if start_detected and end_detected:
                        try:
                            final_duration = 0
                            duration = 0
                            start = self.gf.time_stamp_local_to_datetime(start_detected)
                            end = self.gf.time_stamp_local_to_datetime(end_detected)
                            result = end - start
                            duration = result.seconds

                            # durasi di sum
                            if mac_address in list_prev_data:
                                dur = list_prev_data[mac_address]
                                final_duration = int(dur) + int(duration)
                                
                            else:
                                final_duration = int(duration)
                            
                            if final_duration <= self.pass_counting_noise:                  # jika total durasi melebihi set point. maka di abaikan (1 jam)
                                count_total_wifi += 1
                                list_duration_wifi.append(final_duration)

                            else:
                                list_mac_wifi.remove(mac_address)

                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            self.gf.dd(f"count_wifi :: duration :: {exc_type} - {fname} - {exc_tb.tb_lineno}")
                            final_duration = 0

                        save = {
                            "start": start_detected,
                            "end": end_detected,
                            "duration": duration,
                            "final_duration": final_duration
                        }
                        obj_mac_wifi[mac_address] = save

                if list_duration_wifi:
                    try:
                        list_duration_wifi.sort()
                        calculate_with_med = statistics.median(list_duration_wifi)
                        dwelling_time = int(calculate_with_med)
                        calculate_with_mean = statistics.mean(list_duration_wifi)
                        dwelling_time_mean = int(calculate_with_mean)

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        self.gf.dd(f"count_wifi :: dwelling :: {exc_type} - {fname} - {exc_tb.tb_lineno}")
                        duration = 0

            return count_total_wifi, list_mac_wifi, obj_mac_wifi, dwelling_time, dwelling_time_mean
        

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.gf.dd(f"count_wifi :: {exc_type} - {fname} - {exc_tb.tb_lineno}")
            return None
        
    def count_ble(self, list_ble_sorted):
        '''
        Fungsi ini berfungsi sebagai counting dan menentukan apakah mac tersebut masuk kreiteria atau 
        tidak, untuk BLE konsepnya hampir sama dengan WiFi yang membedakan, ble tidak di bandingkan 
        dengan jam sebelumnya.
        
        adapun kriteria yang ditanamkan adalah :
            -- jika mac address powernya kurang dari batas B (terhitung)
            -- jika durasi ble lebih dari set point maka akan di abaikan

        FUNCTION    : count_ble(list_ble_sorted)
        RESPONSE    : 0, ["mac1", "mac2"], {"mac_address": {"start": "2023-08-24 07:00:14", 
                        "end": "2023-08-24 07:52:57", "duration": 3163, "final_duration": 3163}, 0, 0
        TYPE RESP   : int, list, object, int, int (multiple response)

        1. list_wifi_sorted     : list mac_address yang sudah di urutkan dan dirapikan dari fungsi 
                                    sort_data_and_save_to_variable_ble()
        2. list_wifi_file       : log file yang sedang di process saat ini
        3. list_wifi            : list log file yang sudah terrecord di folder log wifi/ble
        '''

        try:
            obj_mac_ble = {}
            list_mac_ble = []
            count_total_ble = 0
            list_duration_ble = []
            dwelling_time = 0
            dwelling_time_mean = 0

            if list_ble_sorted:

                ''' FILTER 1 ----------------------------------------------------------------------------------------------------------'''
                for mac_address in list_ble_sorted:
                    for detail in list_ble_sorted[mac_address]:
                        date_time = detail["dt"]
                        rssi = int(detail["rssi"])
                        
                        if rssi >= globals.min_spb_small and rssi <= globals.max_spb_small:
                            if not mac_address in list_mac_ble:
                                list_mac_ble.append(mac_address)
                                # count_total_ble += 1
                
                ''' FILTER 2 ----------------------------------------------------------------------------------------------------------'''
                for mac_address in list_ble_sorted:
                    start_detected = None
                    end_detected = None

                    for detail in list_ble_sorted[mac_address]:
                        date_time = detail["dt"]
                        rssi = int(detail["rssi"])

                        # save start detected and end detected
                        if mac_address in list_mac_ble:
                            if not start_detected:
                                start_detected = date_time
                            end_detected = date_time

                    if start_detected and end_detected:
                        try:
                            start = self.gf.time_stamp_local_to_datetime(start_detected)
                            end = self.gf.time_stamp_local_to_datetime(end_detected)
                            result = end - start
                            duration = result.seconds

                            if duration <= self.pass_counting_noise:                        # jika total durasi melebihi set point. maka di abaikan (1 jam)
                                count_total_ble += 1
                                
                                list_duration_ble.append(duration)

                            else:
                                list_mac_ble.remove(mac_address)

                        except Exception as e:
                            exc_type, exc_obj, exc_tb = sys.exc_info()
                            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                            self.gf.dd(f"count_ble :: duration :: {exc_type} - {fname} - {exc_tb.tb_lineno}")
                            duration = 0

                        save = {
                            "start": start_detected,
                            "end": end_detected,
                            "duration": duration,
                            "final_duration": 0
                        }
                        obj_mac_ble[mac_address] = save

                if list_duration_ble:
                    try:
                        list_duration_ble.sort()
                        calculate_with_med = statistics.median(list_duration_ble)
                        calculate_with_mean = statistics.mean(list_duration_ble)
                        dwelling_time = int(calculate_with_med)
                        dwelling_time_mean = int(calculate_with_mean)
                    
                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        self.gf.dd(f"count_ble :: dwelling :: {exc_type} - {fname} - {exc_tb.tb_lineno}")
                        duration = 0

            return count_total_ble, list_mac_ble, obj_mac_ble, dwelling_time, dwelling_time_mean

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.gf.dd(f"count_ble :: {exc_type} - {fname} - {exc_tb.tb_lineno}")
            return None

    def get_dwelling_count(self, obj_mac):
        '''
        Untuk membedakan beberapa tingkat, karena untuk mendapatkan dwelling time waktu 
        terlalu susah, sehingga kita mengubah konsep dwelling time menjadi dwelling count
        
        ada 3 tingkat :
            -- layer 1      : 0 detik   -   30 detik    (A)
            -- layer 2      : 31 detik  -   5 menit     (B)
            -- layer 3      : 5 menit   -   1 jam       (C)
        
        Jadi dengan 3 tingkat tersebut kita bandingkan, berapa total mac yang terdeteksi 
        selama durasi A (layer 1), dan berapa total mac yang terdeteksi selama durasi B (layer 2), dst.

        FUNCTION    : get_dwelling_count(obj_mac)
        RESPONSE    : [0,0,0]
        TYPE RESP   : list

        1. obj_mac  : object dari hasil sorting dan counting (hasil akhir)
        '''

        layer_1 = [0, 30, "A"]
        layer_2 = [31, 300, "B"]
        layer_3 = [301, 3600, "C"]

        dwelling_count = []
        total = 0
        all_data = {}

        try:
            if obj_mac:
                for mac in obj_mac:
                    duration = obj_mac[mac]["duration"]
                    final_duration = obj_mac[mac]["final_duration"]

                    if final_duration <= self.pass_counting_noise:
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
                                    
            for dw in sorted(all_data.keys()):
                dwelling_count.append(len(all_data[dw]))
            total = sum(dwelling_count)

            if len(dwelling_count) < 1:
                dwelling_count = [0,0,0]
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.gf.dd(f"get_dwelling_count :: {exc_type} - {fname} - {exc_tb.tb_lineno}")
            return [0,0,0], total

        return dwelling_count, total

    def delete_log(self, max_size=600, max_count_deleted=1):
        '''
        Fungsi ini untuk memonitor berapa besar file log yang tersimpan.
        jika sudah melebihi "max_size" maka akan di kurangi 

        FUNCTION    : delete_log(max_size=default(600mb), max_count_deleted=default(1))
        RESPONSE    : None
        TYPE RESP   : None

        1. max_size             : 600 (mb)
        2. max_count_deleted    : tiap melebihi 600mb, berapa tanggal yang akan di hapus. 
                                jika 1 maka 1 tanggal aja yang di hapus. (1 tanggal = 24 file)
        '''

        # check file
        base_log = "log"
        base_path = ["log/ble", "log/wifi"]
        ble_result = "log/ble_result"
        wifi_result = "log/wifi_result"

        # check size
        size_ble = self.gf.get_size(base_log)
        self.gf.dd(f"Size : {size_ble}")

        if size_ble > max_size:
            for path in base_path:
                count_deleted = 0
                list_unique = []

                list_file = self.gf.list_file_in_folder(path)
                for dt in list_file:
                    path_date, _ = dt.split(" ")

                    if not path_date in list_unique:
                        list_unique.append(path_date)

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
                                    self.gf.dd(f"Delete base folder : {file_deleted} ; result : {repl}")

                                else:
                                    repl = file_deleted.replace(path, ble_result)
                                    os.remove(repl)
                                    self.gf.dd(f"Delete base folder : {file_deleted} ; result : {repl}")

                            size_ble = self.gf.get_size(base_log)
                            self.gf.dd(f"Size : {size_ble}")

                    count_deleted += 1

    
    def indoor_tracking_mode(self):
        '''
        Fungsi ini untuk mendeteksi TAG yang sudah didaftarkan.
        indoor tracking hanya memproses BLE saja. untuk wifi diabaikan.
        dan hanya mac-address yang sudah di daftarkan yang di simpan.

        FUNCTION    : indoor_tracking_mode()
        RESPONSE    : None
        TYPE RESP   : None

        1. max_size             : 600 (mb)
        2. max_count_deleted    : tiap melebihi 600mb, berapa tanggal yang akan di hapus. 
                                jika 1 maka 1 tanggal aja yang di hapus. (1 tanggal = 24 file)
        '''

        if len(globals.raw_ble) > 0:
            raw_ble = list(globals.raw_ble)

            globals.raw_ble = []

            try:
                for ble in raw_ble:
                    base_data = ble.split(" - ")
                    date_time_from_data = base_data[0]
                    mac_address_from_data = None
                    rssi_from_data = None
                    
                    
                    split_base_data = ble.split(",")
                    try:
                        if "BLE=" in split_base_data[0] and "RSSI=" in split_base_data[1]:
                            split_mac = split_base_data[0].split("=")
                            mac = split_mac[1]
                            if len(mac) >= 16:
                                mac_address_from_data = mac

                            split_rssi = split_base_data[1].split("=")
                            rssi_negatif = split_rssi[1][0:3]
                            if rssi_negatif:
                                try:
                                    rssi_neg = int(rssi_negatif) * -1
                                    rssi_from_data = int(rssi_neg)
                                
                                except:
                                    rssi_from_data = ""

                        if date_time_from_data and mac_address_from_data and rssi_from_data:
                            if int(rssi_from_data) <= globals.max_spb_small:
                                
                                filters = mac_address_from_data.upper()
                                if filters in globals.tag_ble:
                                    save = {
                                        "dt": date_time_from_data,
                                        "rssi": rssi_from_data
                                    }

                                    if mac_address_from_data in globals.send_indoor_tracking:
                                        dt = []
                                        dt = list(globals.send_indoor_tracking[mac_address_from_data])
                                        dt.append(save)
                                        globals.send_indoor_tracking[mac_address_from_data] = dt

                                    else:
                                        dt = []
                                        dt.append(save)
                                        globals.send_indoor_tracking[mac_address_from_data] = dt
                                
                                    nam = self.gf.time_stamp_hour_only()
                                    name_it = f"log/indoor_tracking/mac_{nam}"
                                    self.gf.write_log(name_it, json.dumps(globals.send_indoor_tracking))

                        self.gf.dd(f"indoor_tracking :: result :: {globals.send_indoor_tracking}")

                    except Exception as e:
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        self.gf.dd(f"indoor_tracking_mode :: inside loop :: {exc_type} - {fname} - {exc_tb.tb_lineno} - {split_base_data}")
                        pass
            
            except Exception as e:
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.gf.dd(f"indoor_tracking_mode :: {exc_type} - {fname} - {exc_tb.tb_lineno}")
            