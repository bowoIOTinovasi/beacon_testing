# import os
# import time
# import subprocess


# dt = [
#     "log/cp_2023-06-24.log",
#     "log/cp_2023-06-25.log",
#     "log/cp_2023-06-26.log",
#     "log/cp_2023-06-28.log",
#     "log/cp_2023-06-29.log",
#     "log/cp_2023-06-30.log",
#     "log/cp_2023-07-01.log",
#     "log/cp_2023-07-02.log",
#     "log/cp_2023-07-03.log",
#     "log/cp_2023-07-04.log",
#     "log/cp_2023-07-05.log",
#     "log/cp_2023-07-06.log"
# ]

# for d in dt:
#     print("------------------------------------------------")
#     print(d, "---------------------------------------------")
#     cmd = f"python test_main_local.py --file {d}"
#     process = subprocess.Popen(['python', 'test_main_local.py', '--file', str(d)])
#     exitCode=process.wait()


#     print(d, "---------------------------------------------")
#     print("------------------------------------------------")
#     time.sleep(1)


# ---------------------------------------------------------------------------------------------------------------------------------------------------
import time
import OPi.GPIO as GPIO

from getmac import get_mac_address


GPIO.setwarnings(False)
# GPIO.setboard(GPIO.ZERO)
GPIO.setmode(GPIO.BCM)

led_red = 17
led_green = 27
led_blue = 22

GPIO.setup(led_red, GPIO.OUT)
GPIO.setup(led_green, GPIO.OUT)
GPIO.setup(led_blue, GPIO.OUT)

while True:
    try:
        # GPIO.output(led_red, GPIO.LOW)
        # GPIO.output(led_green, GPIO.HIGH)
        # GPIO.output(led_blue, GPIO.HIGH)
        # time.sleep(1)
        GPIO.output(led_red, GPIO.HIGH)
        GPIO.output(led_green, GPIO.LOW)
        GPIO.output(led_blue, GPIO.HIGH)
        time.sleep(1)
        # GPIO.output(led_red, GPIO.HIGH)
        # GPIO.output(led_green, GPIO.HIGH)
        # GPIO.output(led_blue, GPIO.LOW)
        # time.sleep(1)

        eth_mac = get_mac_address()
        print(eth_mac)

    except Exception as e:
        print("--> ", e)

    except KeyboardInterrupt:
        break

# --------------------------------------------------------------------------------------------------------------------------------------------------------
# import paho.mqtt.client as mqttClient
# import time

# def on_message(client, userdata, msg):
#     try:
#         print("MSG---------> ", msg.payload.decode())
#         # data = msg.payload.decode()
#     except Exception as e:
#         print(f"Listener error -> {e}")

# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("Connected to broker")
#         global Connected                #Use global variable
#         Connected = True                #Signal connection 
#         client.subscribe("beacon/subscribe/02:81:a8:eb:23:cb")

#     else:
#         print("Connection failed")
 
# Connected = False   #global variable for the state of the connection
 
# broker_address= "interadsdev.com"
# port = 1883
# user = "admin01"
# password = "zJJ9M7sKCW"
 
# client = mqttClient.Client("Python")               #create new instance
# client.username_pw_set(user, password=password)    #set username and password
# client.on_connect = on_connect                      #attach function to callback
# client.on_message = on_message
# client.connect(broker_address, port=port)          #connect to broker
 
# client.loop_start()        #start the loop
 
# while Connected != True:    #Wait for connection
#     time.sleep(0.1)
 
# try:
#     while True:
 
#         value = "test--"
#         client.publish("beacon/publish",value)
#         time.sleep(5)
 
# except KeyboardInterrupt:
 
#     client.disconnect()
#     client.loop_stop()

# ---------------------------------------------------------------------------------------------------------------------------------------------------

# import global_function

# gf = global_function.globalFunction("Test")


# start_detected = "2023-07-20 11:00:05"
# end_detected = "2023-07-20 11:39:44"

# start = gf.time_stamp_local_to_datetime(start_detected)
# end = gf.time_stamp_local_to_datetime(end_detected)
# duration = end - start

# print(duration.seconds)