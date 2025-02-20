from pymodbus.client import ModbusSerialClient
from pyModbusTCP.client import ModbusClient
import logging
from datetime import datetime
import time
import json

# Function to create a JSON file with status
def create_json_file(status):
    # Define the data to be written to the JSON file
    data = {
        "status": status
    }

    # Specify the filename
    filename = 'status.json'

    # Write the data to the JSON file
    with open(filename, 'w') as json_file:
        json.dump(data, json_file, indent=4)
       
# ----------------------------------------------  Set up logging configuration for PLC -----------------------------------------

logger = logging.getLogger(__name__)
try:
    logging.basicConfig(filename='./src/controller/plc_test_log.log',
                        level=logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    log_message = f"................Log Started................"
    logger.info(log_message)
    print(log_message)
except Exception as e:
    print(f"PLC Logging Exception -> {e}")    
# ---------------------------------------------------------------------------------------------------------------

class PLC:
    def __init__(self, plc_protocol="Serial", plc_ip="192.168.10.13", plc_port=502, plc_com="/dev/ttyUSB0"):
        """
        Ubuntu Installation Guide (Autor: Mohammadreza Asadi G.):

        Serial PLCs:
            - Python Packages Installation:
                $ pip install pymodbus
                $ pip install pyserial

            - RS485 Driver Download (Extract): https://roboeq.ir/files/id/3923/name/Windows-CH340-Driver.zip
            - If wine is not installed:
                $ sudo apt install wine

            - RS485 Driver Installation (in the extracted dir):
                $ wine SETUP.exe

            - Install driver using default option in the GUI

            - Driver Checking (/dev/ttyUSB0):
                $ ls /dev/tty*

            - Permissions Access:
                $ sudo chmod a+rw /dev/ttyUSB0

            - Permanent Permissions Access:
                $ sudo nano /etc/udev/rules.d/50-ttyusb.rules
                - Add this line in the file and save:
                    SUBSYSTEM=="tty", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001", GROUP="dialout", MODE="0666"

        Ethernet PLCs:
            - Python Packages Installation:
                $ pip install pyModbusTCP

        - Run the Code:
            $ python3 PLC.py

	
	- Modbus PLC Registers Address:
	
			MEMORY BIT	
		PLC Address	Modbus Address
			M0	002049
			M1	002050
			M2	002051
			M3	002052
			M4	002053
			M5	002054
			M6	002055
			M7	002056
			M8	002057
			M9	002058
			|	|
			|	|
			|	|
			|	|
			M1535	003584

        """
        global logger
        self.plc_protocol = plc_protocol
        ## PLC Address Register (Lookup Table)
        self.plc_address_serial = {
                                        1:2049,
                                        2:2051,
                                        3:2053,
                                        4:2055,
                                        5:2057,
                                        6:2059                                       
                                        }
        
        self.plc_address_ethernet = {
                                        1:2048,
                                        2:2050,
                                        3:2052,
                                        4:2054,
                                        5:2056,
                                        6:2058                                      
                                        }  
              
        if plc_protocol == "Serial":
            try:
                # self.client = ModbusSerialClient(method="rtu", port=plc_com, stopbits=1, bytesize=8, parity="N", baudrate=9600)
                self.client = ModbusSerialClient(method="rtu", port=plc_com, stopbits=1, bytesize=8, parity="E", baudrate=9600, timeout=0.1)
                log_message = "Serial Client Initialized Successfully:"
                logger.info(log_message)
                log_message = f"Client -> {self.client}"
                logger.info(log_message)   
            except Exception as e:
                log_message = "Serial Client Not Initialized:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)   
                             
        elif plc_protocol == "Ethernet":
            try:
                self.client = ModbusClient(host=plc_ip, port=plc_port, timeout=3, unit_id=2)
                log_message = "Ethernet Client Initialized Successfully:"
                logger.info(log_message)
                log_message = f"Client -> {self.client}"
                logger.info(log_message)                    
            except Exception as e:
                log_message = f"Ethernet Client Not Initialized:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)
    
    def plc_open_client(self):
        max_retries = 5
        retry_delay = 3
        created = False
        
        if self.plc_protocol == "Serial":
            retries = 0
            t1 = datetime.now()
            while retries < max_retries:
                try:
                    if self.client.connect():
                        log_message = "Serial Client Opened Successfully"
                        logger.info(log_message)  
                        print("Serial Client Opened Successfully")
                        created = True
                        break
                    else:
                        log_message = f"Serial Client Not Opened -> retrying to connect...({retries+1}/{max_retries})"
                        logger.warning(log_message)  
                        print(f"Serial Client Not Opened -> retrying to connect...({retries+1}/{max_retries})")
                        retries += 1
                        time.sleep(retry_delay)
                except Exception as e:
                    log_message = f"Serial Client Not Opened -> retrying to connect...({retries+1}/{max_retries})"
                    logger.error(log_message)
                    log_message = f"Serial Client Connection Error: {e}"
                    logger.error(log_message)    
                    print(f"Serial Client Connection Error: {e}")
                    retries += 1
                    time.sleep(retry_delay)
            if created is False:       
                log_message = f"Serial Client NOT Created!!!"
                logger.error(log_message)
            t2 = datetime.now()
            print(f"..........................elapsed time: {t2 - t1}")
                                   
        elif self.plc_protocol == "Ethernet":
            retries = 0
            t1 = datetime.now()
            while retries < max_retries:
                try:
                    if self.client.open():
                        log_message = "Ethernet Client Opened Successfully"
                        logger.info(log_message)  
                        print("Ethernet Client Opened Successfully")
                        created = True
                        break
                    else:
                        log_message = f"Ethernet Client Not Opened -> retrying to connect...({retries+1}/{max_retries})"
                        logger.warning(log_message)  
                        print(f"Ethernet Client Not Opened -> retrying to connect...({retries+1}/{max_retries})")
                        retries += 1
                        time.sleep(retry_delay)
                except Exception as e:
                    log_message = f"Ethernet Client Not Opened -> retrying to connect...({retries+1}/{max_retries})"
                    logger.error(log_message)
                    log_message = f"Ethernet Client Connection Error: {e}"
                    logger.error(log_message)    
                    print(f"Ethernet Client Connection Error: {e}")
                    retries += 1
                    time.sleep(retry_delay)
            if created is False:       
                log_message = f"[Ethernet Client NOT Created!!!"
                logger.error(log_message)
            t2 = datetime.now()
            print(f"..........................elapsed time: {t2 - t1}")                  
    
    def plc_output_on(self, output_number):
        retries = 2
        delay = 0.1
        devices = {
                    1: "Hall Light",
                    2: "TV",
                    3: "Air Condition",
                    4: "Kitchen Light",
                    5: "Curtain",
                    6: "Parking Door"
                    }
        
        if self.plc_protocol == "Serial":
            register_address = self.plc_address_serial[output_number] - 1
            # register_address = 2049
            try:
                opened = False
                for attempt in range(retries):
                    if self.client.write_coil(register_address, True, unit=1): # Write the coil
                        log_message = f"Serial PLC Coil {register_address} [{devices[output_number]}] Written True Succsessfully"
                        logger.info(log_message)
                        opened = True
                        # time.sleep(delay)  # Give some time for the PLC to process the command
                        # read_value = self.client.read_coils(register_address, 1, unit=1) # Read back the coil value to verify
                        # print(f"----------------------{read_value}--------------------")
                        # if read_value is not None and read_value[0] == True:
                        #     opened = True
                        #     log_message = f"{devices[output_number]} is ON..."
                        #     logger.info(log_message)
                        #     print(log_message)
                        #     return True 
                        # else:
                        #     log_message = f"{devices[output_number]} is Not ON -> Retrying to On...(Attempt {attempt+1}/{retries})"
                        #     logger.warning(log_message)
                        #     print(log_message)
                    else:
                        log_message = f"Serial PLC Coil {register_address} [{devices[output_number]}] Failed to Write -> Retrying to write on coil {register_address}...(Attempt {attempt+1}/{retries})"
                        logger.warning(log_message)
                        print(log_message)
                if opened is False:
                    log_message = f"{devices[output_number]} is Not ON"
                    logger.error(log_message)
                    print(log_message)
                    return False                
            except Exception as e:
                log_message = f"PLC Serial Problem:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)       
        
        elif self.plc_protocol == "Ethernet":
            register_address = self.plc_address_ethernet[output_number]
            try:
                opened = False
                for attempt in range(retries):
                    if self.client.write_single_coil(register_address, True): # Write the coil
                        log_message = f"Ethernet PLC Coil {register_address} [{devices[output_number]}] Written True Succsessfully"
                        logger.info(log_message)
                        time.sleep(delay)  # Give some time for the PLC to process the command
                        read_value = self.client.read_coils(register_address, 1) # Read back the coil value to verify
                        if read_value is not None and read_value[0] == True:
                            opened = True
                            log_message = f"{devices[output_number]} is ON..."
                            logger.info(log_message)
                            print(log_message)
                            return True 
                        else:
                            log_message = f"{devices[output_number]} is Not ON -> Retrying to On...(Attempt {attempt+1}/{retries})"
                            logger.warning(log_message)
                            print(log_message)
                    else:
                        log_message = f"Ethernet PLC Coil {register_address} [{devices[output_number]}] Failed to Write -> Retrying to write on coil {register_address}...(Attempt {attempt+1}/{retries})"
                        logger.warning(log_message)
                        print(log_message)
                if opened is False:
                    log_message = f"{devices[output_number]} is Not ON"
                    logger.error(log_message)
                    print(log_message)
                    return False                
            except Exception as e:
                log_message = f"PLC Ethernet Problem:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)

    def plc_output_off(self, output_number):
        retries = 2
        delay = 0.1
        devices = {
                    1: "Hall Light",
                    2: "TV",
                    3: "Air Condition",
                    4: "Kitchen Light",
                    5: "Curtain",
                    6: "Parking Door"
                    }
        
        if self.plc_protocol == "Serial":
            register_address = self.plc_address_serial[output_number] - 1
            try:
                opened = False
                for attempt in range(retries):
                    if self.client.write_coil(register_address, False, unit=1): # Write the coil
                        log_message = f"Serial PLC Coil {register_address} [{devices[output_number]}] Written False Succsessfully"
                        logger.info(log_message)
                        opened = True
                        # time.sleep(delay)  # Give some time for the PLC to process the command
                        # read_value = self.client.read_coils(register_address, 1) # Read back the coil value to verify
                        # if read_value is not None and read_value[0] == False:
                        #     opened = True
                        #     log_message = f"{devices[output_number]} is OFF..."
                        #     logger.info(log_message)
                        #     print(log_message)
                        #     return True 
                        # else:
                        #     log_message = f"{devices[output_number]} is Not OFF -> Retrying to OFF...(Attempt {attempt+1}/{retries})"
                        #     logger.warning(log_message)
                        #     print(log_message)
                    else:
                        log_message = f"Serial PLC Coil {register_address} [{devices[output_number]}] Failed to Write -> Retrying to write on coil {register_address}...(Attempt {attempt+1}/{retries})"
                        logger.warning(log_message)
                        print(log_message)
                if opened is False:
                    log_message = f"{devices[output_number]} is Not OFF"
                    logger.error(log_message)
                    print(log_message)
                    return False                
            except Exception as e:
                log_message = f"PLC Serial Problem:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)       
        
        elif self.plc_protocol == "Ethernet":
            register_address = self.plc_address_ethernet[output_number]
            try:
                opened = False
                for attempt in range(retries):
                    if self.client.write_single_coil(register_address, False): # Write the coil
                        log_message = f"Ethernet PLC Coil {register_address} [{devices[output_number]}] Written False Succsessfully"
                        logger.info(log_message)
                        time.sleep(delay)  # Give some time for the PLC to process the command
                        read_value = self.client.read_coils(register_address, 1) # Read back the coil value to verify
                        if read_value is not None and read_value[0] == False:
                            opened = True
                            log_message = f"{devices[output_number]} is OFF..."
                            logger.info(log_message)
                            print(log_message)
                            return True 
                        else:
                            log_message = f"{devices[output_number]} is Not OFF -> Retrying to OFF...(Attempt {attempt+1}/{retries})"
                            logger.warning(log_message)
                            print(log_message)
                    else:
                        log_message = f"Ethernet PLC Coil {register_address} [{devices[output_number]}] Failed to Write -> Retrying to write on coil {register_address}...(Attempt {attempt+1}/{retries})"
                        logger.warning(log_message)
                        print(log_message)
                if opened is False:
                    log_message = f"{devices[output_number]} is Not OFF"
                    logger.error(log_message)
                    print(log_message)
                    return False                
            except Exception as e:
                log_message = f"PLC Ethernet Problem:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)

    def plc_input_on(self, input_number, status, unit, option='r2'):
        if option == 'w':
            # address = input_number + 101025
            address = input_number
            result = self.client.write_register(address, status, unit)
            print(f"{result=}")
            # print(result.registers[0])
            # if result.isError():
            #     print("Input Error")
            # else:
            #     print(f"Input Changed")
            # self.client.close()
        elif option == 'r':
            result = self.client.read_holding_registers(input_number, status, unit)
            print(result)
            print(result.registers)
            print(result.registers[0])
        elif option == 'r2':
            result = self.client.read_input_registers(input_number, status, unit)
            print(result)
        
            
if __name__ == "__main__":
    P = PLC(plc_protocol="Serial")
    P.plc_open_client()
    # status = P.plc_output_on(1)
    # print(status)
    # time.sleep(5)
    # status = P.plc_output_off(1)
    # print(status)

    P.plc_input_on(6097, 50, unit=1, option='w')
    # status = P.plc_output_on(6)
    # time.sleep(0.7)
    # P.plc_input_on(6097, 1, unit=1, option='r')
    status = P.plc_output_on(6)
    print(status)
