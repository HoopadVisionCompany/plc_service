
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import time
from datetime import datetime
from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusSerialClient
from logger_controller import ControllerLogger
from utils.patterns.singletons import SingletonMeta

class Controller(metaclass=SingletonMeta):
    def __init__(self, controller_info):
        """
        Controller Docs (Autor: Mohammadreza Asadi G.)

            Delta PLCs Controller (Ubuntu Installation Guide):

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
                        $ lsusb
                            - Find the USB device info. for example:
                                Bus 001 Device 005: ID 1a86:7523 QinHeng Electronics HL-340 USB-Serial adapter
                            - The idVendor is "1a86" and idProduct is 7523

                        $ sudo nano /etc/udev/rules.d/50-ttyusb.rules
                        - Add this line in the file and save (Note: use the idVendor and idProduct of the previous step):
                            SUBSYSTEM=="tty", ATTRS{idVendor}=="1a86", ATTRS{idProduct}=="7523", GROUP="dialout", MODE="0666"

                Ethernet PLCs:
                    - Python Packages Installation:
                        $ pip install pyModbusTCP

                - Run the Test Code:
                    $ python3 PLC.py

                - Modbus PLC Registers Address:

                        MEMORY BIT
                    PLC Address	Modbus Address
                        M0	002049 (for Ethernet PLCs it starts at 002048)
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

                        
            Input Data Format (for the initialization of all kind of controllers):

                controller_info Dictionary Format:
                    controller_info = {
                                'Controller Name': {'Controller ID': '',
                                                    'Controller Type':'',
                                                    'Controller Protocol':'', 
                                                    'Controller IP':'', 
                                                    'Controller Port':'', 
                                                    'Controller Driver':'', 
                                                    'Controller Unit':'', 
                                                    'Controller Count Pin IN':'', 
                                                    'Controller Count Pin OUT':''}                                              
                                }

                    Validation:
                        Controller Name -> str : Arbitrary Name
                        Controller ID -> str : UUID4 (Mongodb)
                        Controller Type -> str : Fixed Names (PLC Delta, PLC Siemens, Micro-controller, Arduino, Raspberry Pi, Relay Module)
                        Controller Protocol -> str : Fixed Names (Ethernet, Serial)
                        Controller IP -> str/NoneType : IP Address
                        Controller Port -> int/NoneType : Port Address
                        Controller Driver -> str/NoneType : Based on Serial Port Name ("/dev/ttyUSBx" on Ubuntu , 'COMx' on Windows)
                        Controller Unit -> int/NoneType : Based on Clients Number (Clients IDs)
                        Controller Count Pin IN -> int/NoneType : Number of Input Pins
                        Controller Count Pin Out -> int/NoneType : Number of Output Pins

                    Example:
                    controller_info = {
                                'Delta PLC': {'Controller ID': 'ghg256gjd88f',
                                              'Controller Type': 'PLC Delta',
                                              'Controller Protocol': 'Ethernet', 
                                              'Controller IP': '192.168.10.5', 
                                              'Controller Port': 502, 
                                              'Controller Driver': None, 
                                              'Controller Unit': 1, 
                                              'Controller Count Pin IN': 8, 
                                              'Controller Count Pin OUT': 4},

                                 'bluepill': {'Controller ID': 'gtht6577gjd88f',
                                              'Controller Type': 'ARM Micro-controller',
                                              'Controller Protocol': 'Serial', 
                                              'Controller IP': None, 
                                              'Controller Port': None, 
                                              'Controller Driver': "/dev/ttyUSB0", 
                                              'Controller Unit': 2, 
                                              'Controller Count Pin IN': 10, 
                                              'Controller Count Pin OUT': 10},

                                'ماژول رله': {'Controller ID': 'pjho090909jkkd',
                                              'Controller Type': 'Relay Module',
                                              'Controller Protocol': 'Ethernet', 
                                              'Controller IP': '192.168.1.16', 
                                              'Controller Port': 8080, 
                                              'Controller Driver': None, 
                                              'Controller Unit': None, 
                                              'Controller Count Pin IN': 0, 
                                              'Controller Count Pin OUT': 4}                                              
                                }                   

                controller_event Dictionary Format:
                    controller_event = {'Controller ID':'',
                                        'Pin List': [],
                                        'Pin Type': [],
                                        'Scenario': ''
                    }
        """
        # Initialize logger
        self.controller = ControllerLogger()

        # Log the initialization
        self.controller.logger.info("................Controller initialized................")

        self.controller_info = controller_info
        self.clients_list, self.clients_protocol = self.controller_client_creator(controller_info)
        self.controller_client_connector(self.clients_list, self.clients_protocol, controller_info)

    def controller_client_creator(self, controller_info: dict):
        clients_list = {}
        clients_protocol = {}
        for controller_name, controller in controller_info.items():
            if controller['Controller Type'] == 'PLC Delta':
                if controller['Controller Protocol'] == 'Ethernet':
                    client = ModbusClient(host=controller['Controller IP'], port=controller['Controller Port'], timeout=3, unit_id=controller['Controller Unit'])
                    clients_list[controller['Controller ID']] = client
                    clients_protocol[controller['Controller ID']] = 'Ethernet'
                elif controller['Controller Protocol'] == 'Serial':
                    client = ModbusSerialClient(method="rtu", port=controller['Controller Driver'], stopbits=1, bytesize=8, parity="E", baudrate=9600, timeout=0.1)
                    clients_list[controller['Controller ID']] = client
                    clients_protocol[controller['Controller ID']] = 'Serial'
            else:
                print(f"Controller [{controller_name}] Client is Not Defined!")
                clients_list[controller['Controller ID']] = None
                clients_protocol[controller['Controller ID']] = None
        return clients_list, clients_protocol

    def controller_client_type_selector(self, client_protocol: str, client):
        if client_protocol == 'Ethernet':
            return client.open()
        elif client_protocol == 'Serial':
            return client.connect()
        else:
            return None

    def controller_clients_initial_connector(self, clients_list: dict, clients_protocol: list, controller_info: dict):
        max_retries = 1 # MUST ADDED TO .ENV
        retry_delay = 0.1 # MUST ADDED TO .ENV
        created = False
        name_counter = 0
        controller_names = list(controller_info.keys())
        for controller_id, client in clients_list.items():
            controller_name = controller_names[name_counter]
            name_counter += 1
            retries = 0
            # t1 = datetime.now()
            while retries < max_retries:
                try:
                    if self.controller_client_type_selector(clients_protocol[controller_id], client):
                        print(f"Controller [{controller_name}] Client Connected")
                        created = True
                        break
                    else:
                        print(f"Retrying to connect to controller [{controller_name}]... ({retries + 1}/{max_retries})")
                        retries += 1
                        time.sleep(retry_delay)
                except Exception as e:
                    print(f"Retrying to connect to controller [{controller_name}]... ({retries + 1}/{max_retries})")
                    print(f"Exception: {e}")
                    retries += 1
                    time.sleep(retry_delay)
            if created is False:
                print(f"Controller [{controller_name}] Client NOT connected after {max_retries} retries.")
            # t2 = datetime.now()
            # print(f"..........................elapsed time: {t2 - t1}")

    def controller_client_connector(self, controller_event: dict):
        pass

    def controller_register_creator(self, controller_event: dict):
        registers_list = []
        for controller in self.controller_info.values():
            if controller['Controller ID'] == controller_event['Controller ID']:
                if controller['Controller Type'] == 'PLC Delta':
                    for pin in controller_event['Pin List']:
                        if controller['Controller Protocol'] == 'Ethernet':
                            self.controller_info_pin = pin
                            registers_list.append(self.controller_info_pin + 2048)                           
                        elif controller['Controller Protocol'] == 'Serial':
                            self.controller_info_pin = pin
                            registers_list.append(self.controller_info_pin + 2049)
                            
                else:
                    print(f"Register Address for Controller \033[1m[{controller['Controller Type']}]\033[0m is Not Defined!")
                    registers_list = None
        print(f'{registers_list=}')
        return registers_list

    def controller_info_extractor(self, controller_event: dict):
        for controller_name, controller in controller_info.items():
            if controller['Controller ID'] == controller_event['Controller ID']:
                self.controller_info_name =  controller_name
                self.controller_info_id =  controller['Controller ID']
                self.controller_info_type =  controller['Controller Type']
                self.controller_info_protocol=  controller['Controller Protocol']
                self.controller_info_ip =  controller['Controller IP']
                self.controller_info_port =  controller['Controller Port']
                self.controller_info_driver =  controller['Controller Driver']
                self.controller_info_unit =  controller['Controller Unit']
                self.controller_info_cpi =  controller['Controller Count Pin IN']
                self.controller_info_cpo =  controller['Controller Count Pin OUT']

    def controller_output_control(self, client_unit: int, client, register: int, status: bool):
        retries = 3     # MUST ADDED TO .ENV
        delay = 0.25    # MUST ADDED TO .ENV
        try:
            operation_completed = False
            for attempt in range(retries):
                if self.controller_info_protocol == 'Ethernet':
                    write_coil = client.write_single_coil(register, status)
                elif self.controller_info_protocol == 'Serial':
                    write_coil = client.write_coil(register, status)
                else:
                    return None
                if write_coil:
                    time.sleep(delay)  # Give some time for the PLC to process the command
                    read_value = client.read_coils(register, client_unit)  # Read back the coil value to verify - What is 1 ?!
                    if read_value is not None and read_value[0] == True:
                        operation_completed = True
                        print(f"[✔] Controller [{self.controller_info_name}] -> Output Pin [{self.controller_info_pin}] -> Register [{register}] -> Set [{status}]")
                        return True # Must be modified
                    else:
                        print(f"[...] Controller [{self.controller_info_name}] -> Output Pin [{self.controller_info_pin}] -> Register [{register}] -> NOT Set [{status}] -> Retrying to Set...([read_coil] Attempt {attempt + 1}/{retries})")
                        self.controller_client_connector()
                else:
                        print(f"[...] Controller [{self.controller_info_name}] -> Output Pin [{self.controller_info_pin}] -> Register [{register}] -> NOT Set [{status}] -> Retrying to Set...([write_coil] Attempt {attempt + 1}/{retries})")
            if operation_completed is False:
                print(f"[✘] Controller [{self.controller_info_name}] -> Output Pin [{self.controller_info_pin}] -> Register [{register}] -> NOT Set [{status}]")
                return False # Must be modified
        except Exception as e:
            # pass
            print(f"[✘] Controller [{self.controller_info_name}] -> Output Pin [{self.controller_info_pin}] -> Register [{register}] -> NOT Set [{status}]")         
            print(f"Exception: {e}")
            return False # Must be modified
 

    def controller_action(self, controller_event: dict):
        self.controller_info_extractor(controller_event)
        client_registers = self.controller_register_creator(controller_event)
        client = self.clients_list[self.controller_info_id]
        for register in client_registers:
            if controller_event['Scenario'] == 'Auto Alarm':
                pass
            elif controller_event['Scenario'] == 'Auto Caller':
                pass
            elif controller_event['Scenario'] == 'Auto Open':
                pass
            elif controller_event['Scenario'] == 'Manual Alarm ON':
                pass
            elif controller_event['Scenario'] == 'Manual Alarm OFF':
                pass
            elif controller_event['Scenario'] == 'Manual Open':
                pass
            elif controller_event['Scenario'] == 'Manual Close':
                pass
            elif controller_event['Scenario'] == 'Relay ON':
                self.controller_output_control(client_unit=self.controller_info_unit, client=client, register=register, status=True)
                # print(f'Relay ON for register {register}')
            elif controller_event['Scenario'] == 'Relay OFF':
                self.controller_output_control(client_unit=self.controller_info_unit, client=client, register=register, status=False)
                # print(f'Relay OFF for register {register}')


if __name__ == '__main__':
    test_type = 2
    if test_type == 1:
        controller_info = {
                    'Delta PLC': {'Controller ID': 10,
                                    'Controller Type': 'PLC Delta',
                                    'Controller Protocol': 'Ethernet', 
                                    'Controller IP': '192.168.10.5', 
                                    'Controller Port': 502, 
                                    'Controller Driver': None, 
                                    'Controller Unit': 1, 
                                    'Controller Count Pin IN': 8, 
                                    'Controller Count Pin OUT': 3},

                        'bluepill': {'Controller ID': 20,
                                    'Controller Type': 'Micro-controller',
                                    'Controller Protocol': 'Serial', 
                                    'Controller IP': None, 
                                    'Controller Port': None, 
                                    'Controller Driver': "/dev/ttyUSB0", 
                                    'Controller Unit': 2, 
                                    'Controller Count Pin IN': 10, 
                                    'Controller Count Pin OUT': 10},

                    'PLC دلتا': {'Controller ID': 30,
                                    'Controller Type': 'PLC Delta',
                                    'Controller Protocol': 'Serial', 
                                    'Controller IP': None, 
                                    'Controller Port': None, 
                                    'Controller Driver': "/dev/ttyUSB0", 
                                    'Controller Unit': 1, 
                                    'Controller Count Pin IN': 8, 
                                    'Controller Count Pin OUT': 2},

                    'ماژول رله': {'Controller ID': 40,
                                    'Controller Type': 'Relay Module',
                                    'Controller Protocol': 'Ethernet', 
                                    'Controller IP': '192.168.1.16', 
                                    'Controller Port': 8080, 
                                    'Controller Driver': None, 
                                    'Controller Unit': None, 
                                    'Controller Count Pin IN': 0, 
                                    'Controller Count Pin OUT': 4}                                              
                    }
        
        controller_event_1 = {'Controller ID':10,
                            'Pin List': [0, 1, 2],
                            'Pin Type': [],
                            'Scenario': ''
        }    

        controller_event_2 = {'Controller ID':20,
                            'Pin List': [0, 1],
                            'Pin Type': [],
                            'Scenario': ''
        }  

        controller_event_3 = {'Controller ID':30,
                            'Pin List': [0, 1],
                            'Pin Type': [],
                            'Scenario': ''
        }

        events = [controller_event_1, controller_event_2, controller_event_3]
        
        controller = Controller(controller_info)
        for event in events:
            controller.controller_register_creator(controller_info, event)

    elif test_type == 2:
        controller_info = {
                    'Delta PLC': {'Controller ID': 10,
                                    'Controller Type': 'PLC Delta',
                                    'Controller Protocol': 'Ethernet', 
                                    'Controller IP': '192.168.10.5', 
                                    'Controller Port': 502, 
                                    'Controller Driver': None, 
                                    'Controller Unit': 1, 
                                    'Controller Count Pin IN': 8, 
                                    'Controller Count Pin OUT': 3},

                    'PLC دلتا': {'Controller ID': 30,
                                    'Controller Type': 'PLC Delta',
                                    'Controller Protocol': 'Serial', 
                                    'Controller IP': None, 
                                    'Controller Port': None, 
                                    'Controller Driver': "/dev/ttyUSB0", 
                                    'Controller Unit': 1000, 
                                    'Controller Count Pin IN': 8, 
                                    'Controller Count Pin OUT': 2}                                    
                                    }

        controller_event_1 = {'Controller ID':30,
                            'Pin List': [0, 1, 2],
                            'Pin Type': [],
                            'Scenario': 'Relay OFF'
        }

        events = [controller_event_1]
        controller = Controller(controller_info)
        for event in events:
            controller.controller_action(event)