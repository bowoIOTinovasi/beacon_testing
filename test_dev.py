# get port usb address -----------------------------------------------------------------------------------------------------
import subprocess

def get_port_id():
    '''
    FUNCTION    : get_port_id() \n
    RESPONSE    : {"/dev/ttyUSB1": usb-Silicon_Labs_CP2102_USB_to_UART_Bridge_Controller_0001-if00-port0}\n
    TYPE RESP   : object
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

# port_data = get_port_id()
# print("PORT     = ", port_data)
# print("-----------------------------------------")

# get port usb address -----------------------------------------------------------------------------------------------------




# get mac address dev ------------------------------------------------------------------------------------------------------
import subprocess

def get_mac_address_ethernet(key):
    '''
    FUNCTION    : get_mac_address_ethernet(key)
    RESPONSE    : b0:7b:25:74:cc:9e
    TYPE RESP   : string
    
    ------------
    key - open terminal and type "ip a", check header ethernet ex: eth0, eno1
        example :
            get_mac_address_ethernet("eth0")
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


# mac_address_lan = get_mac_address_ethernet("eth0")
# print("MAC      = ", mac_address_lan)
# print("-----------------------------------------")

# get mac address dev ------------------------------------------------------------------------------------------------------



# get ganti file rnet ------------------------------------------------------------------------------------------------------
import subprocess
import global_function

gf = global_function.globalFunction("test_dev")

def change_gsm_config():
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
    check_serial_port = get_port_id()
    if check_serial_port:
        for seri in check_serial_port:
            if "FTDI" in check_serial_port[seri]:
                serial_id_selected = seri
                break
    ''''''

    ''' jika serial path serial sudah dapat, open rnet dan ganti serial '''
    if serial_id_selected:
        # read from file rnet
        res = subprocess.run(['sudo', 'cat', path_rnet], stdout=subprocess.PIPE)
        result = res.stdout.decode('utf-8')
        process = result.split("\n")
        for proc in process:
            if flag_serial:
                save_serial_config.append(serial_id_selected)
                flag_serial = False
            
            else:
                save_serial_config.append(proc)
                
            if "Serial Port" in proc:
                flag_serial = True
        
        final = '\n'.join(save_serial_config)
        
        # write to file rnet
        gf.write(path_rnet, final, "w")
        
        return True
    
    else:
        return False
    ''''''

rnet_config = change_gsm_config()
print(rnet_config)
# get ganti file rnet ------------------------------------------------------------------------------------------------------