import os
import socket
import subprocess
from datetime import datetime

class globalFunction(object):
    '''
    Rangkuman berbagai fungsi universal yang sering di gunakan.

    CLASS   :globalFunction\n
    CONTOH  :
        import global_function
    
        gf = global_function.globalFunction("main_program")

        gf.dd()

        gf.timestamp()

        etc.
    '''
    def __init__(self, filename):
        self.filename = filename


    # debug--------------------------------------------------------------------------------------------------------------------------
    def dd(self, show):
        '''
        Untuk menampilkan print variable beserta datetime dan nama file yang sedang di eksekusi.

        FUNCTION    : dd(show)
        RESPONSE    : None
        RESP TYPE   : None

        1. show     : string yang ingin di tampilkan
        
        data = 10
        contoh      : dd(f"global variable {data}")
        '''
        print(f"{self.time_stamp()} - {self.filename} :: {show}")


    # datetime ----------------------------------------------------------------------------------------------------------------------
    def time_stamp_hour_only(self):
        '''
        Untuk mendapatkan tanggal dan waktu lengkap waktu sekarang dalam bentuk string.

        FUNCTION    : time_stamp()
        RESPONSE    : YY-MM-DD hh:01:01
        RESP TYPE   : string
        '''
        return datetime.now().strftime("%Y-%m-%d %H:01:01") 
    
    def time_stamp(self):
        '''
        Untuk mendapatkan tanggal dan waktu lengkap waktu sekarang dalam bentuk string.

        FUNCTION    : time_stamp()
        RESPONSE    : YY-MM-DD hh:mm:ss
        RESP TYPE   : string
        '''
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S") 

    def time_stamp_hour_only(self):
        '''
        Untuk mendapatkan tanggal dan jam waktu sekarang dalam bentuk string.

        FUNCTION    : time_stamp_hour_only()
        RESPONSE    : YY-MM-DD hh
        RESP TYPE   : string
        '''
        return datetime.now().strftime("%Y-%m-%d %H")
    
    def date_only(self):
        '''
        Untuk mendapatkan tanggal waktu sekarang dalam bentuk string.

        FUNCTION    : date_only()
        RESPONSE    : YY-MM-DD
        RESP TYPE   : string
        '''
        return datetime.now().strftime("%Y-%m-%d")

    def hour_only(self):
        '''
        Untuk mendapatkan jam waktu sekarang dalam bentuk string.

        FUNCTION    : hour_only()
        RESPONSE    : hh
        RESP TYPE   : string
        '''
        return datetime.now().strftime("%H")
    
    def minute_only(self):
        '''
        Untuk mendapatkan menit waktu sekarang dalam bentuk string.

        FUNCTION    : minute_only()
        RESPONSE    : mm
        RESP TYPE   : string
        '''
        return datetime.now().strftime("%M")
    
    def second_only(self):
        '''
        Untuk mendapatkan detik waktu sekarang dalam bentuk string.

        FUNCTION    : second_only()
        RESPONSE    : ss
        RESP TYPE   : string
        '''
        return datetime.now().strftime("%S")
    
    def minute_only_to_seconds(self):
        '''
        Untuk mendapatkan menit dalam satuan detik waktu sekarang dalam bentuk string.

        FUNCTION    : minute_only_to_seconds()
        RESPONSE    : ss
        RESP TYPE   : int
        '''
        minutes = datetime.now().strftime("%M")
        minute = int(minutes) * 60
        return minute
    
     
    # local datetime ----------------------------------------------------------------------------------------------------------------
    def time_stamp_local(self, timestamp):
        '''
        Untuk mendapatkan tanggal dan jam lengkap dengan input tanggal dan waktu dari local string.

        FUNCTION    : time_stamp_local(timestamp)
        RESPONSE    : YY-MM-DD hh:mm:ss
        RESP TYPE   : string

        1. timestamp    : berupa tanggal dan waktu dengan format YY-MM-DD hh:mm:ss
        '''
        str_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return str_datetime.strftime("%Y-%m-%d %H:%M:%S") 
    
    def time_stamp_hour_only_local(self, timestamp):
        '''
        Untuk mendapatkan tanggal dan jam dengan input tanggal dan waktu dari local string.

        FUNCTION    : time_stamp_hour_only_local(timestamp)
        RESPONSE    : YY-MM-DD hh
        RESP TYPE   : string

        1. timestamp    : berupa tanggal dan waktu dengan format YY-MM-DD hh:mm:ss
        '''
        str_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return str_datetime.strftime("%Y-%m-%d %H") 
    
    def date_only_local(self, timestamp):
        '''
        Untuk mendapatkan tanggal dengan input tanggal dan waktu dari local string.

        FUNCTION    : date_only_local(timestamp)
        RESPONSE    : DD
        RESP TYPE   : string

        1. timestamp    : berupa tanggal dan waktu dengan format YY-MM-DD hh:mm:ss
        '''
        str_datetime = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
        return str_datetime.strftime("%Y-%m-%d") 
    
    def time_stamp_local_to_datetime(self, timestamp):
        '''
        Untuk mengubah tanggal dan jam dalam bentuk string menjadi bentuk format datetime.

        FUNCTION    : time_stamp_local_to_datetime(timestamp)
        RESPONSE    : YY-MM-DD hh:mm:ss
        RESP TYPE   : datetime

        1. timestamp    : berupa tanggal dan waktu dengan format YY-MM-DD hh:mm:ss
        '''
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    

    # read write --------------------------------------------------------------------------------------------------------------------
    def write_log(self, name, content, mode="a"):
        '''
        Untuk membuat/menyimpan ke dalam file dengan ekstensi .log beserta tanggal dan waktu.

        FUNCTION    : write_log(name, content, mode="a")
        RESPONSE    : None
        RESP TYPE   : None

        1. name     : path file yang akan dibuat/disimpan contoh, name="test"
        2. content  : string yang akan di simpan didalam file
        3. mode     : default menggunakan mode append (a), mode write (w)
        '''
        f = open("{}.log".format(name), mode)
        f.write("{} - {}\n".format(self.time_stamp(), content))
        f.close()

    def write(self, name, content, mode="a"):
        '''
        Untuk membuat/menyimpan ke dalam file (basic).

        FUNCTION    : write(name, content, mode="a")
        RESPONSE    : None
        RESP TYPE   : None

        1. name     : path file yang akan dibuat/disimpan contoh, name="test.txt"
        2. content  : string yang akan di simpan didalam file
        3. mode     : default menggunakan mode append (a), mode write (w)
        '''
        f = open("{}".format(name), mode)
        f.write("{}".format(content))
        f.close()

    def read(self, name):
        '''
        Untuk membaca file (basic).

        FUNCTION    : read(name)
        RESPONSE    : any
        RESP TYPE   : string

        1. name     : path file yang akan dibaca contoh, name="test.txt"
        '''
        f = open(name, "r")
        res = f.read()
        return res
    

    # device info ------------------------------------------------------------------------------------------------------------------
    def ip_address(self):
        '''
        Untuk membaca ip address device.

        FUNCTION    : ip_address()
        RESPONSE    : 0.0.0.0
        RESP TYPE   : string
        '''
        try:
            hostname = socket.gethostname()
            ip = socket.gethostbyname(hostname)
            if ip:
                return ip
            else:
                return "0.0.0.0"

        except:
            return "0.0.0.0"
        
    def get_mac_address_ethernet(self, key="eth0"):
        '''
        Untuk mendapatkan macaddress ethernet.

        FUNCTION    : get_mac_address_ethernet(key)
        RESPONSE    : b0:7b:25:74:cc:9e
        TYPE RESP   : string
        
        1. key      : open terminal and type "ip a", check header ethernet ex: eth0, eno1
        2. example  : get_mac_address_ethernet("eth0")
        '''

        flag = None
        mac_address = None
        
        try:
            res = subprocess.run(['ip', 'a'], stdout=subprocess.PIPE)
            result = res.stdout.decode('utf-8')
            
            process = result.split("\n")
            for proc in process:
                if flag:
                    if "link/ether" in proc:
                        proc_split = proc.split(" ")
                        for ps in proc_split:
                            if ":" in ps:
                                mac_address = ps
                                break
                        break

                if key in proc:
                    flag = True    
        
        except Exception as e:
            print(f"get_mac_address_ethernet :: {e}")

        return mac_address
        
    def get_port_id(self):
        '''
        Untuk mendapatkan path port serial communication

        FUNCTION    : get_port_id() \n
        RESPONSE    : {"/dev/ttyUSB1": usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0}\n
        RESP TYPE   : object
        '''

        response = {}

        try:
            res = subprocess.run(['ls', '-l', '/dev/serial/by-id'], stdout=subprocess.PIPE)
            result = res.stdout.decode('utf-8')
            
            process = result.split("\n")
            for proc in process:
                if "lrwxrwxrwx" in proc:
                    split_data = proc.split(" ")
                    names = split_data[len(split_data) - 3]
                    ports = split_data[len(split_data) - 1]
                    port_parse = ports.split("/")
                    port_result = port_parse[len(port_parse) - 1]
                    detail_port = f"/dev/{port_result}"
                    response[detail_port] = names

        except Exception as e:
            print(f"get_port_id :: {e}")

        return response

    # files and folder -------------------------------------------------------------------------------------------------------------
    def list_file_in_folder(self, path, filter=".log"):
        '''
        Untuk mendapatkan list file didalam folder, dan respon berupa list.

        FUNCTION    : list_file_in_folder(path, filter=".log")          
        RESPONSE    : ["path/1.log", "path/2.log"]
        RESP TYPE   : list

        1. path     : untuk membaca path folder yang akan di baca file nya.
        2. filter   : default menggunakan ".log"
        '''
        all = []
        for (root, dirs, file) in os.walk(path):
            for f in sorted(file):
                if filter in f:
                    pth = f"{path}/{f}"
                    all.append(pth)
        return all
    
    def get_size(self, start_path = '.', unit = "mb"):
        '''
        Untuk mendapatkan size dalam folder.

        FUNCTION    : get_size(start_path = '.', unit = "mb")
        RESPONSE    : 100
        RESP TYPE   : float

        1. start_path  : "path folder yang ini di cek ukurannya" \n
        2. contoh      : get_size("/home/pi", unit="mb") \n
        3. response    : 100 (mb)
        '''
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(start_path):
            for f in filenames:
                fp = os.path.join(dirpath, f)
                # skip if it is symbolic link
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
        total_show = 0
        if unit == "mb":
            total_show = total_size / 1000000
        
        else:
            total_show = total_size / 1000

        return total_show # bytes
