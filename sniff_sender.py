import os
import time
import json
import threading
import paho.mqtt.client as mqtt
import string
import random

import globals
import global_function

class sender_and_receiver(threading.Thread):
    '''
    class ini berfungsi untuk mengirim secara periodic dan untuk menerima configurasi dari server
    teknologi yang dipakai untuk mengirimkan data menggunakan MQTT (qos0)

    task :
    -- kirim log secara periodic (sesuai configurasi interval)
    -- terima configurasi dari server (VPN on / off)
    '''
    
    def __init__(self, parent):
        threading.Thread.__init__(self)

        ''' init global var '''
        self.parent = parent
        self.counting_trigger = 0
        self.count_mqtt_connection = 0
        self.count_mqtt_disconnect = 0
        self.gf = global_function.globalFunction("sender_and_receiver")
        ''''''

        ''' config default '''
        self.mqtt_server = globals.mqtt_server
        self.port = globals.port
        ''''''

        ''' action untuk membedakan perintah dari server '''
        self.event_new_beacon = "new_beacon"
        self.event_beacon_registered = "beacon_registered"
        
        self.event_publish_data = "send_data"
        self.event_config = "config"
        self.event_config_filter = "/config/beacon/filter"
        self.event_upload_log = "/get/upload_scan"

        self.event_device_status = "device_status"
        ''''''

        ''' untuk control VPN ON or OFF '''
        self.event_activate_vpn = "/config/vpn/on"
        self.event_deactivate_vpn = "/config/vpn/off"
        ''''''

        ''' topic untuk connect dan stanby kirim dan terima data '''
        self.topic_publish = "beacon/publish"
        self.topic_subscribe = [
            f"beacon/subscribe/{globals.mac_address}"
        ]
        ''''''

        ''' random client name '''
        self.client_name = f"ib:ea:{globals.mac_address}:co:nn{self.id_generator()}"
        ''''''

        ''' config and connect to broker '''
        self.mqtt_sub_pub = mqtt_config(
            self.mqtt_server,
            self.port,
            "admin01",
            "zJJ9M7sKCW",
            self.client_name, 
            self.topic_subscribe
        )
        ''''''

        globals.send_datetime = self.gf.time_stamp_hour_only()
     

    def run(self):
        self.gf.dd("Start Sender")
        time.sleep(3)

        while self.parent.is_alive():
            
            ''' connect mqtt '''
            if not self.mqtt_sub_pub.connected:
                self.mqtt_sub_pub.connect_client()
                self.count_mqtt_connection+=1
                if self.count_mqtt_connection > 3:
                    self.count_mqtt_connection = 0
                    globals.mqtt_connection = False
                
                ''' trigger break and eksekusi lagi via main '''
                self.count_mqtt_disconnect += 1
                self.gf.dd(f"\n run :: count_mqtt_disconnect - {self.count_mqtt_disconnect} \n")
                if self.count_mqtt_disconnect > 60:
                    self.gf.dd(f"\n run :: break {self.count_mqtt_disconnect} \n")
                    break
                ''''''

            else:
                self.count_mqtt_connection = 0
                globals.mqtt_connection = True

            ''''''
            

            ''' kondisi jika device belum di registrasi '''
            if globals.registered:
                ''' send data periodic sesuai interval dan send data perhitungan '''
                if not globals.send_data:
                    # for sending data
                    self.counting_trigger += 1
                    if self.counting_trigger > globals.trigger_sending:
                        self.counting_trigger = 0
                        
                        self.gf.dd(f"Sending data to server : {globals.mqtt_server} - device status")
                        send_format = {
                                "action": self.event_device_status,
                                "data": {
                                "id": f"{globals.mac_address}",
                                "timestamp": self.gf.time_stamp(),
                                "checker": globals.beacon_checker,
                            }
                        }
                        send = json.dumps(send_format)
                        self.mqtt_sub_pub.send_message(self.topic_publish, send)
                        
                        globals.beacon_checker = ""
                        
                        send_formats = {
                            "action": self.event_publish_data,
                            "data": {
                                "id": f"{globals.mac_address}",
                                "timestamp": self.gf.time_stamp(),
                                "ip": self.gf.ip_address(),
                                "dt": globals.send_datetime,
                                "total_wifi": globals.send_total_wifi,
                                "total_ble": globals.send_total_ble,
                                "dwelling_wifi": globals.send_dwelling_wifi,
                                "dwelling_ble": globals.send_dwelling_ble,
                                "dwelling_count_wifi": globals.send_dwelling_count_wifi,
                                "dwelling_count_ble": globals.send_dwelling_count_ble
                                # "installation_date": globals.installation_date,
                                # "indoor_tracking": globals.send_indoor_tracking
                            }
                        }
                        sends = json.dumps(send_formats)
                        self.gf.dd(f"now data update :: {sends}")

                else:
                    ''' send data jika mendapat triger dari "sniff_process.py" '''

                    self.counting_trigger = 0
                    self.gf.dd(f"Result -> {globals.send_data}, {globals.wifi_ble_count_list}")

                    globals.send_data = False

                    if globals.wifi_ble_count_list:
                        for dt in globals.wifi_ble_count_list:
                            # self.gf.dd(f"DT -> {dt}")
                            self.gf.dd(f"Sending data to server : {globals.mqtt_server} - trigger by sniff_process.py")

                            send_format = {
                                "action": self.event_publish_data,
                                "data": {
                                    "id": f"{globals.mac_address}",
                                    "timestamp": self.gf.time_stamp(),
                                    "ip": self.gf.ip_address(),
                                    "dt": dt["date_time"],
                                    "total_wifi": dt["count_wifi"],
                                    "total_ble": dt["count_ble"],
                                    "dwelling_wifi": dt["dwelling_wifi"],
                                    "dwelling_ble": dt["dwelling_ble"],
                                    "dwelling_count_wifi": dt["dwelling_count_wifi"],
                                    "dwelling_count_ble": dt["dwelling_count_ble"]
                                    # "installation_date": globals.installation_date,
                                    # "indoor_tracking": globals.send_indoor_tracking
                                }
                            }
                            send = json.dumps(send_format)
                            self.mqtt_sub_pub.send_message(self.topic_publish, send)
                            globals.send_indoor_tracking = {}
                            time.sleep(5)
                            self.gf.dd(f"Send periodic count -> {send}")
                        globals.wifi_ble_count_list = []
                ''''''
            else:
                self.gf.dd(f"Sending data to server : {globals.mqtt_server} as 'New Device'")
                send_format = {
                    "action": self.event_new_beacon,
                    "data": {
                        "id": f"{globals.mac_address}",
                        "ip": self.gf.ip_address(),
                        "connection": "LAN"
                    }
                }
                send = json.dumps(send_format)
                self.mqtt_sub_pub.send_message(self.topic_publish, send)
                time.sleep(5)                

            ''' untuk menampung command / setting dari server '''
            if self.mqtt_sub_pub.messages != None:
                self.gf.dd("Receive data from server - {}".format(self.mqtt_sub_pub.messages))
                try:
                    respon_from_mqtt = json.loads(self.mqtt_sub_pub.messages)
                    if respon_from_mqtt:
                        # jika yang dikirim berupa configurasi
                        action = respon_from_mqtt["action"]

                        if action == self.event_config:
                            # save
                            self.gf.write("config/setting.json", self.mqtt_sub_pub.messages, "w")

                            self.gf.dd("Save Setting - Done")

                            # share
                            globals.mqtt_server = respon_from_mqtt["data"]["mqtt_server"]
                            globals.trigger_sending = respon_from_mqtt["data"]["interval"]
                            
                            globals.min_sp_small = respon_from_mqtt["data"]["wifi"]["min_small_frame"]
                            globals.max_sp_small = respon_from_mqtt["data"]["wifi"]["max_small_frame"]
                            globals.min_spb_small = respon_from_mqtt["data"]["ble"]["min_small_frame"]
                            globals.max_spb_small = respon_from_mqtt["data"]["ble"]["max_small_frame"]
                            
                        elif action == self.event_activate_vpn:
                            os.system("./start_vpn.sh")
                        
                        elif action == self.event_deactivate_vpn:
                            os.system("sudo tmux kill-session -t ovpn")
                            self.gf.dd("Kill tmux ovpn")
                            time.sleep(1)
                            os.system("sudo killall openvpn")
                            self.gf.dd("Kill all ovpn")
                            # pass

                        elif action == self.event_beacon_registered:
                            globals.registered = True


                except Exception as e:
                    self.gf.dd("sniff_sender.py - ", e)

                self.mqtt_sub_pub.messages = None
            
            time.sleep(1)
            ''''''

        globals.mqtt_connection = False
        self.gf.dd("Kill Sender")
    


    def id_generator(self, size=6, chars=string.ascii_uppercase + string.digits):
        '''
        untuk generate random id 6 digit.

        FUNCTION    : id_generator(size=6, chars=string.ascii_uppercase + string.digits)
        RESPONSE    : ksaKD0
        TYPE RESP   : string
        '''

        return ''.join(random.choice(chars) for _ in range(size))





class mqtt_config(object):
    ''' 
    class mqtt connect and disconnect 
    
    task :
        -- open connection
        -- sender
        -- receiver
        -- close connection
    '''
    def __init__(self, broker_address, port, username, password, client_name, topic_subscribe):
        self.broker_address= broker_address
        self.port = port
        self.user = username
        self.password = password
        self.client_name = client_name
        self.topic_subscribe = topic_subscribe

        # flag
        self.connected = False
        self.messages = None
        self.first_connect = True

        self.gf = global_function.globalFunction("mqtt_class")

    def connect_client(self):
        try:
            if self.first_connect:
                self.client = mqtt.Client(self.client_name, True, None)               #create new instance
                self.client.username_pw_set(self.user, password=self.password)    #set username and password
                self.client.on_connect = self.on_connect                      #attach function to callback
                self.client.on_message = self.on_message
                self.client.on_disconnect = self.on_disconnect
                self.client.connect(
                    host=self.broker_address, 
                    port=self.port
                )          #connect to broker
                
                self.client.loop_start()        #start the loop

                self.first_connect = False

            else:
                self.client.loop_start()        #start the loop

            loop = 0
            while self.connected != True:    #Wait for connection
                loop+=1
                if loop > 100:
                    break
                time.sleep(0.1)
        
        except Exception as e:
            self.gf.dd(f"Connect_client :: {e}")
            pass

    def on_message(self, client, userdata, msg):
        try:
            self.gf.dd(f"From Server > {msg.payload.decode()}")
            self.messages = msg.payload.decode()
        except Exception as e:
            self.gf.dd(f"Listener error -> {e}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            for topics in self.topic_subscribe:
                client.subscribe(topics)
                self.gf.dd(topics)

            self.gf.dd(f"Connected OK Returned code={rc}")
 
        else:
            self.gf.dd(f"Bad connection Returned code={rc}")


    def on_disconnect(self, client, userdata, rc):
        if rc != 0:
            self.connected = False
            self.gf.dd("Disconnected from broker")

    def disconnect_mqtt(self):
        self.client.disconnect()
        self.client.loop_stop()

    def send_message(self, topic, value):
        try:
            res = self.client.publish(topic, value)
            self.gf.dd(f"send_message :: {res} - topic={topic} - val={value}")
        except Exception as e:
            self.gf.dd(f"send_message :: error {e}")

            try:
                self.client.publish(topic, value)
                self.gf.dd(f"send_message again :: topic={topic} - val={value}")
            except Exception as e:
                self.gf.dd(f"send_message :: errors {e}")
                pass
        time.sleep(1)
