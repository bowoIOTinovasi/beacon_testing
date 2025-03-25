import sys
import os
import json
import time
import serial
import threading
import subprocess

import globals
import global_function

import sniff_process
import sniff_sender

if globals.hardware:
    if globals.opi_device:                                                              # use orange pi zero (LAN + WiFi)
        import OPi.GPIO as GPIO

    else:                                                                               # use raspberry pi (LAN + WiFi + GSM)
        import RPi.GPIO as GPIO                     


class main_program(object):
    '''
    main_program menghandle semua task, dan main_program memiliki beberapa thread (child) :
    
    1. sniff_process    (bertugas sebagai pemroses semua data)
    2. sniff_sender     (bertugas sebagai pengirim dan penerima data)
    3. globals          (bertugas sebagai penyambung antara main dan child)

    task :
        -- menghandle komunikasi dengan sensor
        -- menyimpan semua data yang didapat dari sensor ke 
            -- folder log/wifi
            -- folder log/ble
        -- menjaga agar thread tetapi bekerja
        -- menyimpan dan membaca semua configurasi
        -- mengendalikan i/o untuk LED indikator
            -- PINK     : setting
            -- GREEN    : connected
            -- RED      : not connected
    '''


    def __init__(self):
        ''' init global variable '''
        self.gf = global_function.globalFunction("main_program")                        # init global function
        self.process = sniff_process.process(threading.currentThread())                 # init process
        self.sender = sniff_sender.sender_and_receiver(threading.currentThread())       # init sender

        self.raw_data = None

        self.enable_setting = True                                                      # case beacon 1 setting terpencet trus = False | hanya case case tertentu saja ini di disable
        self.setting_device = False                                                     # flag untuk mengetahui jika dalam keadaan SETTING, variable True
        self.timeout_setting = 0                                                        # timeout ini berfungsi untuk membatasi durasi setting, untuk mencegah jika button selalu tertekan (keadaan mode setting)
        self.time_check_child = 0                                                       # variable ini berfungsi untuk menjeda fungsi chld watchdog
        self.check_serial = 0                                                           # variable ini berfungsi untuk menonaktifkan debug serial. jika lebih dari 500 baris maka debug akan berhenti
        self.flag_delay_sending_data = 0                                                # variable ini untuk memberikan jeda saat kirim datetime dan connection

        self.ap_name = "config/list_accesspoint"                                        # path untuk penampungan AP
        self.installation_name = "config/installation_date"                             # path untuk menampung datetime instalasi
        self.indoor_tracking_tag = "config/list_tag_ble"                                # path untuk menampung list macaddress TAG

        # globals.mac_address = self.gf.get_mac_address_ethernet()                        # ambil mac address dan replace variable yang ada di globals
        self.gf.dd(f"MAC - {globals.mac_address}")
        ''''''


        ''' catatan '''
        #new - RED (PA01) , GREEN (PA00) , BLUE (PA03) , RESETSIM800 (PA02) , ENABLEESP(PA14) 
        #new - self.led_red = 17 , self.led_green = 27 , self.led_blue = 22 , self.reset_esp = 11
        ''''''
        
 
        ''' untuk membedakan antara type raspberry atau orange pi '''
        if globals.opi_device:                                                          # config pin i/o orange pi
            # old (Opi)
            self.led_red = 17
            self.led_green = 27
            self.led_blue = 22
            self.reset_esp = 15
        
        else:                                                                           # config pin i/o raspberry pi
            # new (Rpi)
            self.led_red = 17
            self.led_green = 27
            self.led_blue = 22
            self.reset_esp = 23
            self.reset_gsm = 24
        ''''''


        ''' panggil fungi-fungsi '''
        self.connect_sensor()                                                           # activate communikasi ke sensor via serial
        time.sleep(5)
        self.setup_hardware()                                                           # activate drive i/o 
        self.read_accesspoint()                                                         # read list accesspoint
        self.read_setting()                                                             # read setting
        self.read_installation_date()                                                   # read installation date
        self.read_indoor_tracking_tag()                                                 # read read_indoor_tracking_tag
        self.start_all_thread()                                                         # activate all thread (child)
        ''''''

        self.gf.dd("Setup Done")



    def main(self):
        '''
        Fungsi ini digunakan untuk mengontrol semua looping dan bertugas sebagai leader.

        FUNCTION    : main()
        RESPONSE    : None
        TYPE RESP   : None
        '''

        self.gf.dd("Start Main")

        while True:                                                                     # loop forever
            
            ''' Watch dog untuk thread (child) '''
            self.time_check_child+=1
            if self.time_check_child > 2500:                                            # jika looping sudah mencapai 2500x / setara 5 menit maka akan menjalankan fungsi wwatchdog() untuk cek thread
                self.time_check_child = 0
                self.watchdog()                                                         # jika ada thread yang off/problem, maka fungsi ini akan mereset dan menyalakan thread tersebut.
            ''''''

            
            ''' read dan simpan data dari sensor '''
            raw = self.get_value()

            try:
                if str(raw) != "" or str(raw) != None:                                  # fungsi ini memastikan bawah data yang dikirim tidak ada noise / tidak kosong

                    if self.check_serial < 500 and globals.hardware:                    # kondisi ini berfungsi untuk menampilkan serial untuk memastikan bawah komunikasi antara miniPC dan sensor berjalan dengan baik.
                        self.gf.dd(f"raw - {raw}")
                        self.check_serial += 1                                          # loop ini akan berjalan selama 500x saja. setelah itu akan keluar dari kondisi ini.
                        
                        # debug only
                        self.gf.dd(f"server:{globals.mqtt_server} - min_wf:{globals.min_sp_small} - max_wf:{globals.max_sp_small} - min_ble:{globals.min_spb_small} - max_ble:{globals.max_spb_small}")
                    
                    log_Wifi = "log/wifi/mac_{}".format(self.gf.time_stamp_hour_only()) # ini generate path berdasarkan tanggal dan jam saja.
                    log_ble = "log/ble/mac_{}".format(self.gf.time_stamp_hour_only())   

                    if "Beacon Checker" in str(raw):
                        split_data = raw.split(",")
                        split_ = split_data[2].replace("RSSI=", "")
                        globals.beacon_checker = split_
                        self.gf.dd(f"Checker - {raw} - {globals.beacon_checker}")
                    
                    if "ADDR" in str(raw) and "RSSI" in str(raw) and "SSID" in str(raw):    # header ADDR melambangkan data dari WiFi (counting mode)  
                        self.gf.write_log(log_Wifi, "{}".format(str(raw.replace("\n", ""))))
                    
                    elif "BEAC" in str(raw) and "RSSI" in str(raw):                     # header BEAC melambangkan data Beacon WiFi, dan ini disimpan dalam bentuk list yang
                        try:                                                            # yang selanjutnya akan di baca setiap kali booting. supaya kita bisa block AP yang terdeteksi
                            split_data = raw.split(',')                                 # ini berlaku hanya untuk (counting mode)
                            split_ = split_data[0].split("=")
                            mac = split_[1]
                            if not mac in globals.all_ap:
                                if len(mac) >= 16:
                                    globals.all_ap.append(mac)
                                    save = json.dumps(globals.all_ap)
                                    self.gf.write_log(self.ap_name, save, "w")
                        
                        except Exception as e:
                            pass

                    elif "BLE" in str(raw) and "RSSI" in str(raw):                      # header BLE melambangkan data dari BLE (counting mode) dan (indoor tracking)
                        self.gf.write_log(log_ble, "{}".format(str(raw.replace("\n", ""))))

                        if globals.indoortracking_mode:                                 # jika mode indoor tracking, data juga di simpan di global variable agar bisa di proses secara realtime di thread sniff_process
                            globals.raw_ble.append("{} - {}".format(self.gf.time_stamp(), str(raw.replace("\n", ""))))
                    
                    elif "SETTING" in str(raw) and self.enable_setting:                 # header SETTING melambangkan jika kondisi sensor sedang dalam testing.
                        self.timeout_setting = 0

                        self.setting_device = True
                        self.gf.dd("SETTING TIME!")
                        
                        send = "00"
                        if globals.mqtt_connection:                                     # generate code untuk sensor
                            send = f"11"                                                # 11 koneksi aktif semua (internet + mqtt)
                        else:
                            send = f"10"                                                # 10 koneksi aktif dan mqtt off (ada internet + no mqtt)
                        
                        self.flag_delay_sending_data += 1
                        if self.flag_delay_sending_data > 0 and self.flag_delay_sending_data <= 2:  # kondisi ini digunakan untuk menjeda agar saat pengiriman data tidak tabrakan
                            self.raw_data.write(bytes(send, 'utf-8'))                   # kirim code connection ke sensor
                            time.sleep(0.2)

                        elif self.flag_delay_sending_data > 5 and self.flag_delay_sending_data <= 7:
                            datetime_string = f"dt={self.gf.time_stamp()}"              # kirim datetime ke sensod
                            self.raw_data.write(bytes(datetime_string, 'utf-8'))
                            time.sleep(0.2)
                        
                        else:
                            self.flag_delay_sending_data = 0                            # reset counting
                        
                    if self.setting_device:                                             # kondisi ini default nya True, tetapi setelah 200x loop akan False jika kondisi SETTING hilang (ini mencegah jika operasional lupa pencet button setting)
                        if "SignalA=-" in str(raw):                                     # trigger untuk simpan set point WiFi A (terlihat) - SignalA=-54
                            try:
                                sig_re = str(raw).replace('SignalA=-', '')
                                sig_rep = int(sig_re) 
                                self.gf.dd(f"{str(raw)}")
                                if sig_rep != globals.max_sp_small:
                                    self.gf.write('config/signal_a.log', sig_rep, "w")
                                    globals.max_sp_big = sig_rep                        # replace config yang di globals

                            except:
                                pass    

                        elif "SignalB=-" in str(raw):                                   # trigger untuk simpan set point WiFi B (terhitung) - SignalB=-31
                            try:
                                sig_re = str(raw).replace('SignalB=-', '')
                                sig_rep = int(sig_re) 
                                self.gf.dd(f"{str(raw)}")
                                if sig_rep != globals.max_sp_small: 
                                    self.gf.write('config/signal_b.log', sig_rep, "w")
                                    globals.max_sp_small = sig_rep                      # replace config yang di globals

                            except:
                                pass

                        elif "SignalABLE=-"in str(raw):                                 # trigger untuk simpan set point BLE A (terlihat) - SignalABLE=-99
                            try:
                                sig_re = str(raw).replace('SignalABLE=-', '')
                                sig_rep = int(sig_re) 
                                self.gf.dd(f"{str(raw)}")
                                if sig_rep != globals.max_spb_big: 
                                    self.gf.write('config/signal_a_ble.log', sig_rep, "w")
                                    globals.max_spb_big = sig_rep                       # replace config yang di globals

                            except:
                                pass

                        elif "SignalBBLE=-"in str(raw):                                 # trigger untuk simpan set point BLE B (terhitung) - SignalBBLE=-31
                            try:
                                sig_re = str(raw).replace('SignalBBLE=-', '')
                                sig_rep = int(sig_re) 
                                self.gf.dd(f"{str(raw)}")
                                if sig_rep != globals.max_spb_small: 
                                    self.gf.write('config/signal_b_ble.log', sig_rep, "w")
                                    globals.max_spb_small = sig_rep                     # replace config yang di globals

                            except:
                                pass

                        elif "IDA" in str(raw):                                         # untuk simpan data install date - IDA =2023-07-06 19:20:37.
                            try:
                                sig_re = str(raw).replace('IDA=', '')
                                sig_rep = int(sig_re) 
                                self.gf.dd(f"{str(raw)}")
                                if sig_rep != globals.installation_date: 
                                    self.gf.write('config/installation_date.log', sig_rep, "w")
                                    globals.installation_date = sig_rep                 # replace config yang di globals

                            except:
                                pass

                        self.timeout_setting += 1
                        if self.timeout_setting > 200:                                  # loop and counting untuk disable setting (case jika lupa reset button setting )
                            self.setting_device = False

                self.led_state()
            
            except Exception as e:
                if "device disconnected or multiple access on port" in str(e):
                    self.connect_sensor()

                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                self.gf.dd(f"main :: {exc_type} - {fname} - {exc_tb.tb_lineno} - {exc_obj}")
            
            except KeyboardInterrupt:
                self.gf.dd("Start Process")
                break
            ''''''

            time.sleep(0.05)



    def setup_hardware(self):
        '''
        Fungsi ini digunakan untuk mengontrol hardware, digunakan untuk setup input ataupun output.

        FUNCTION    : setup_hardware()
        RESPONSE    : None
        TYPE RESP   : None
        '''

        if globals.hardware:
            GPIO.setwarnings(False)
            GPIO.setmode(GPIO.BCM)

            GPIO.setup(self.led_red, GPIO.OUT)
            GPIO.setup(self.led_green, GPIO.OUT)
            GPIO.setup(self.led_blue, GPIO.OUT)
            GPIO.setup(self.reset_esp, GPIO.OUT)

            time.sleep(1)
            GPIO.output(self.reset_esp, GPIO.LOW)
            self.drive_led("red")                                                       # default led saat pertama kali menyala RED
            time.sleep(2)
            GPIO.output(self.reset_esp, GPIO.HIGH)

            if not globals.opi_device:                                                  # kondisi jika device menggunakan Rpi dan ini berfungsi untuk reset GSM module
                GPIO.setup(self.reset_gsm, GPIO.OUT)
                time.sleep(1)
                GPIO.output(self.reset_gsm, GPIO.LOW)
                time.sleep(2)
                GPIO.output(self.reset_gsm, GPIO.HIGH)



    def drive_led(self, color="red"):
        '''
        Fungsi ini digunakan untuk mengontrol led.

        FUNCTION    : drive_led(color)
        RESPONSE    : None
        TYPE RESP   : None
        
        1. color = red, green, blue, pink, off
        '''
        if globals.hardware:
            if color == "red":
                GPIO.output(self.led_red, GPIO.LOW)
                GPIO.output(self.led_green, GPIO.HIGH)
                GPIO.output(self.led_blue, GPIO.HIGH)
            
            elif color == "green":
                GPIO.output(self.led_red, GPIO.HIGH)
                GPIO.output(self.led_green, GPIO.LOW)
                GPIO.output(self.led_blue, GPIO.HIGH)

            elif color == "blue":
                GPIO.output(self.led_red, GPIO.HIGH)
                GPIO.output(self.led_green, GPIO.HIGH)
                GPIO.output(self.led_blue, GPIO.LOW)

            elif color == "pink":
                GPIO.output(self.led_red, GPIO.LOW)
                GPIO.output(self.led_green, GPIO.HIGH)
                GPIO.output(self.led_blue, GPIO.LOW)
            
            elif color == "off":
                GPIO.output(self.led_red, GPIO.HIGH)
                GPIO.output(self.led_green, GPIO.HIGH)
                GPIO.output(self.led_blue, GPIO.HIGH)



    def led_state(self):
        '''
        Fungsi ini digunakan untuk mengontrol led sesuai koneksi mqtt.

        FUNCTION    : led_state()
        RESPONSE    : None
        TYPE RESP   : None
        '''

        if globals.hardware:
            if self.setting_device:                                                     # jika kondisi setting aktif. warna direct ke PINK
                self.drive_led("pink")

            else:                                                                       # selain kondisi setting, di sesuaikan dengan mqtt connection
                if globals.mqtt_connection:
                    self.drive_led("green")
                
                else:
                    self.drive_led("red")



    def connect_sensor(self):
        '''
        Fungsi ini berfungsi untuk mengubungnkan serial.

        FUNCTION    : connect_sensor(show)
        RESPONSE    : None
        RESP TYPE   : None
        
        pada alur ini ada 2 step untuk mengoneksikan device :
        1. cari path serial
        2. mengoneksokan serial
        '''

        if globals.hardware:
            while self.raw_data == None:
                find_serial = self.gf.get_port_id()                                         # 1. cari path serial
                
                for seri in find_serial:
                    self.gf.dd(f"Serial USB :: {seri} :: {find_serial[seri]}")

                    # if "Silicon_Labs_CP2102_USB" in find_serial[seri]:                      # type serial ESP32
                    if "usb-1a86_USB_Single_Serial_562B012422-if00" in find_serial[seri] or "usb-Silicon_Labs_CP2102_USB" in find_serial[seri]:
                        try:
                            self.gf.dd(f"Try to connect sensor :: {seri} :: {find_serial[seri]}")
                            self.raw_data = serial.Serial(                                  # 2. mengoneksikan serial
                                seri,
                                baudrate=115200,
                                timeout=1
                            )
                            self.raw_data.reset_input_buffer()
                            time.sleep(3)

                        except Exception as e:
                            self.gf.dd(f"connect_sensor > {e}")

                time.sleep(1)
        


    def get_value(self):
        '''
        Fungsi ini digunakan untuk membaca serial yang diterima.

        FUNCTION    : get_value()
        RESPONSE    : any
        TYPE RESP   : string
        '''

        try:
            if globals.hardware:
                if self.raw_data != None:
                    receiver = self.raw_data.readline().decode('ascii')
                    return receiver
                return "-"
            
            else:
                return None
        
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            self.gf.dd(f"get_value :: {exc_type} - {fname} - {exc_tb.tb_lineno} - {exc_obj}")
            return None
        


    def read_setting(self):
        '''
        Fungsi ini digunakan untuk membaca config read setting dan update ke variable globals.

        FUNCTION    : read_setting()
        RESPONSE    : None
        TYPE RESP   : None
        '''

        try:
            dd = self.gf.read("config/setting.json")                                    # baca setting, setting ini di write oleh sniff_sender dari mqtt
            if dd:
                self.gf.dd(f"config > {dd}")

                procc = json.loads(dd)                                                  # share hasil pembacaan ke globals variable
                globals.mqtt_server = procc["data"]["mqtt_server"]                      
                globals.trigger_sending = procc["data"]["interval"]
                globals.min_sp_small = procc["data"]["wifi"]["min_small_frame"]
                globals.max_sp_small = procc["data"]["wifi"]["max_small_frame"]
                globals.min_spb_small = procc["data"]["ble"]["min_small_frame"]
                globals.max_spb_small = procc["data"]["ble"]["max_small_frame"]
            
            # ee = self.gf.read('config/signal_a.log')                                    # baca wifi config signal A - terlihat
            # if ee:
            #     globals.max_sp_big = int(ee)

            # ff = self.gf.read('config/signal_b.log')                                    # baca wifi config signal B - terhitung
            # if ff:
            #     globals.max_sp_small = int(ff)

            # eee = self.gf.read('config/signal_a_ble.log')                               # baca config ble signal A - terlihat
            # if eee:
            #     globals.max_spb_big = int(eee)

            # fff = self.gf.read('config/signal_b_ble.log')                               # baca config ble signal B - terhitung
            # if fff:
            #     globals.max_spb_small = int(fff)
                

            
            # self.gf.dd(f"A={ee} - B={ff}")
                            

        except Exception as e:
            self.gf.dd(f"read_setting :: {e}")
    


    def read_accesspoint(self):
        '''
        Fungsi ini digunakan untuk membaca config read accesspoint dan update ke variable globals.

        FUNCTION    : read_accesspoint()
        RESPONSE    : None
        TYPE RESP   : None
        '''

        dt = self.gf.read("{}.log".format(self.ap_name))
        if dt:
            try:
                if " - " in dt:
                    split = dt.split(" - ")
                    globals.all_ap = json.loads(split[1])

                    self.gf.dd(f"Load AP > {globals.all_ap}")
                    
            except Exception as e:
                self.gf.dd(f"read_accesspoint :: {e}")



    def read_installation_date(self):
        '''
        Fungsi ini digunakan untuk membaca config installation date dan update ke variable globals.

        FUNCTION    : read_installation_date()
        RESPONSE    : None
        TYPE RESP   : None
        '''
        try:
            dt = self.gf.read("{}.log".format(self.installation_name))    
            if dt != "":
                globals.installation_date = dt
                self.gf.dd(f"installation_date :: {dt}")

        except Exception as e:
            self.gf.dd(f"read_installation_date :: {e}")



    def read_indoor_tracking_tag(self):
        '''
        Fungsi ini digunakan untuk membaca config indoor tracking dan update ke variable globals.

        FUNCTION    : read_indoor_tracking_tag()
        RESPONSE    : None
        TYPE RESP   : None
        '''

        try:
            dt = self.gf.read("{}.log".format(self.indoor_tracking_tag))    
            if dt != "":
                globals.tag_ble = json.loads(dt)
                self.gf.dd(f"tag BLE :: {dt}")

        except Exception as e:
            self.gf.dd(f"read_indoor_tracking_tag :: {e}")



    def start_all_thread(self):
        '''
        Fungsi ini digunakan untuk menyalakan semua child, dan dibaca hanya 1x diawal saja.

        FUNCTION    : start_all_thread()
        RESPONSE    : None
        TYPE RESP   : None
        '''

        self.process.start()
        if globals.sender_active:
            self.sender.start()



    def watchdog(self):
        '''
        Fungsi ini digunakan untuk menjaga agar child tetap aktif

        FUNCTION    : watchdog()
        RESPONSE    : None
        TYPE RESP   : None
        '''

        self.gf.dd(f"watchdog - process={self.process.is_alive()}, sender={self.sender.is_alive()}")
        
        if not self.process.is_alive():                                                 # jika proses == False, maka akan di reactivate
            self.process = sniff_process.process(
                threading.currentThread()
            )
            self.process.start()
        
        if globals.sender_active:                                                       # jika sender == False, maka akan di reactivate
            if not self.sender.is_alive():
                self.sender = sniff_sender.sender_and_receiver(
                    threading.currentThread()
                )
                self.sender.start()



    def change_gsm_config(self):
        '''
        Fungsi ini digunakan untuk mengubah configurasi GSM. terletak di /etc/ppp/peers/rnet

        FUNCTION    : change_gsm_config()
        RESPONSE    : True / False
        TYPE RESP   : boolean
        '''

        ''' variable flag '''
        serial_id_selected = None
        save_serial_config = []
        flag_serial = False
        path_rnet = "/etc/ppp/peers/rnet"
        ''''''

        ''' check serial, khusus GSM menggunankan FTDI '''
        check_serial_port = self.gf.get_port_id()                                       # check serial port 
        if check_serial_port:
            for seri in check_serial_port:                              
                if "FTDI" in check_serial_port[seri]:                                   # cari yang FTDI / yang lainnya jika menggunakan USB selain FTDI
                    serial_id_selected = seri                                           # tampung di variable lalu di proses diloop selanjutnya
                    break
        ''''''

        ''' jika serial path serial sudah dapat, open rnet dan ganti serial '''
        if serial_id_selected:
            # read from file rnet
            res = subprocess.run(['sudo', 'cat', path_rnet], stdout=subprocess.PIPE)    # ambil data rnet     
            result = res.stdout.decode('utf-8')                                         
            process = result.split("\n")                                                # split data by enter
            for proc in process:                                                        
                if flag_serial:                                                         # jika saat loop sudah menemukan "Serial Port", maka flag ini akan aktif, dan ganti port nya
                    save_serial_config.append(serial_id_selected)
                    flag_serial = False                                                 # jika sudah menemukan, maka flag tersebut di ubah ke False lagi
                
                else:
                    save_serial_config.append(proc)                                     # tampung semua hasil split di list variable
                    
                if "Serial Port" in proc:                                               # filter untuk aktifasi flag_serial
                    flag_serial = True
            
            final = '\n'.join(save_serial_config)                                       # ubah variable list ke string \n
            
            # write to file rnet
            self.gf.write(path_rnet, final, "w")                                        # write file 
            
            return True
        
        else:
            return False
        ''''''

if __name__ == "__main__":
    main = main_program()
    main.main()
    GPIO.cleanup() 