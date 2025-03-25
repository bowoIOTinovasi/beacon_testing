# mac_address = "02:81:82:c7:66:62" # prep jkt 1
# mac_address = "02:81:3f:50:3a:63" # prep jkt 2
# mac_address = "02:81:af:d0:fc:e9" # prep jkt 3
# mac_address = "9C:9C:1F:CA:29:D8" # beacon beakas central park Gunawarman
# mac_address = "02:81:29:61:76:f8" # beacon new final 1
# mac_address = "b8:27:eb:51:7e:24" # beacon raspberry pi + gsm
# mac_address = "02:81:a8:eb:23:cb" # opi indoor tracking
mac_address = "02:81:29:61:76:f8"

# main.py
hardware = True
sender_active = True

opi_device = True # True = orange pi | False = raspberry pi
indoortracking_mode = False



# --------------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------------
# --------------------------------------------------------------------------------------------------------------------------------------------------------------



# untuk menampung AP
all_ap = []


# untuk menampung data raw BLE
tag_ble = []
raw_ble = []
raw_ble_busy = False
send_indoor_tracking = {}


# untuk trigger kirim hasil count
send_datetime = "2023-01-01 01:01:01"
send_total_wifi = 0
send_total_ble = 0
send_dwelling_wifi = 0
send_dwelling_ble = 0
send_data = False
send_dwelling_count_wifi = [0,0,0]
send_dwelling_count_ble = [0,0,0]

# installation date
installation_date = ""

# untuk menampung wifi dan ble data hasil count
wifi_ble_count_list = []


# set point untuk menentukan titik frame wifi (3 dbm - grey area)
# lingkaran kecil untuk WIFI
min_sp_small = 10
max_sp_small = 65
# lingkaran besar untuk WIFI
min_sp_big = 65
max_sp_big = 80


# set point untuk menentukan titik frame ble (0 dbm - grey area)
# lingkaran kecil untuk BLE
min_spb_small = 30
max_spb_small = 70
# lingkaran besar untuk WIFI
min_spb_big = 70
max_spb_big = 100


# timeout kirim data ke server satuan (detik)
trigger_sending = 60


# trigger count (menit)
trigger_count = 60


# mqtt config default
# mqtt_server = "go.interads.co.id"
# mqtt_server = "mqtt.staging.inovasi.top"
mqtt_server = "mqtt.inovasiadiwarna.com"
port = 1883


# format setting
setting = {}


# flag for connection
mqtt_connection = False
connection_selected = "LAN"
registered = False

# checker 
beacon_checker = ""