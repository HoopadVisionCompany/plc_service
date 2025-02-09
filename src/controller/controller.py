import sys
import os
import threading

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import time
from datetime import datetime
from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusSerialClient  # Docs: https://pymodbus.readthedocs.io/en/v3.6.9/index.html
from src.controller.logger_controller import ControllerLogger
from src.utils.patterns.singletons import SingletonMeta
from src.pin.service import PinCollectionCreator
from dotenv import load_dotenv

load_dotenv()

pin_factory = PinCollectionCreator()
pin_collection = pin_factory.create_collection()

class Controller(metaclass=SingletonMeta):
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
                --------------------------------------------------------------------------------------------------------------------
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
                        Controller IP -> str | NoneType : IP Address
                        Controller Port -> int | NoneType : Port Address
                        Controller Driver -> str | NoneType : Based on Serial Port Name ("/dev/ttyUSBx" on Ubuntu , 'COMx' on Windows)
                        Controller Unit -> int | NoneType : Based on Clients Number (Clients IDs)
                        Controller Count Pin IN -> int | NoneType : Number of Input Pins
                        Controller Count Pin Out -> int | NoneType : Number of Output Pins

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

                --------------------------------------------------------------------------------------------------------------------
                controller_event Dictionary Format:
                    controller_event = {'Controller ID':'',
                                        'Pin List': [],
                                        'Pin Type': [],
                                        'Pin ID': [],
                                        'Delay List': [],
                                        'Scenario': ''
                    }

                    Validation:
                        Controller ID -> str : UUID4 (Mongodb)
                        Pin List -> list : List[int] (0, 1, ..., 999)
                        Pin ID -> list : UUID4 (Mongodb)
                        Pin Type -> list : List[str] (Fixed Names: 'in' , 'out')
                        Delay List -> list : list[float] (in 'second' metric)
                        Scenarios -> str : Fixed Names ('Auto Alarm' , 'Auto Caller' , 'Auto Gate' , Manual Alarm ON' , 'Manual Alarm OFF', 'Manual Gate Open' , 'Manual Gate Close', 'Relay ON' , 'Relay OFF')
                        

                    Example:
                        controller_event = {'Controller ID': 'gtht6577gjd88f',
                                            'Pin List': [0,1,200],
                                            'Pin ID': ['dasfgdeg', 'f324f4f', 'hgh6h6h'],
                                            'Pin Type': [],
                                            'Delay List':[3,1.2,0.04],
                                            'Scenario': 'Auto Alarm'}

                        'Pin List': [0,1,200] -> 0 is Y0 or M0 Register (depends on PLC program) for Delta PLCs , 1 is Y1 or M1 Register (depends on PLC program) for Delta PLCs, 200 is M200 Register (must programmed on PLC) for Delta PLCs
                        'Delay List':[3,1.2,0.04] -> delay (second) between ON and OFF state of 0, 1, and 200 pins respectively
        """
    def __init__(self, controller_info):

        # Initialize logger
        self.controller = ControllerLogger()

        # Log the initialization
        self.controller.logger.info("................Controller initialized................")
        self.controller_info = controller_info

        self.lock = threading.Lock()        
        self.thread_controller_clients_definition = threading.Thread(target=self.controller_clients_definition, args=(controller_info,), daemon=True)
        self.thread_controller_clients_definition.start()
        # self.thread_controller_clients_definition.join()

    def controller_clients_definition(self, controller_info):
        with self.lock:
            self.clients_list, self.clients_protocol = self.controller_clients_creator(controller_info)
            self.controller_clients_initial_connector(self.clients_list, self.clients_protocol, controller_info)

    def controller_clients_creator(self, controller_info: dict):
        clients_list = {}
        clients_protocol = {}
        for controller_name, controller in controller_info.items():
            if controller['Controller Type'] == 'PLC Delta':
                if controller['Controller Protocol'] == 'Ethernet':
                    client = ModbusClient(host=controller['Controller IP'], port=controller['Controller Port'],
                                          timeout=3, unit_id=controller['Controller Unit'])
                    clients_list[controller['Controller ID']] = client
                    clients_protocol[controller['Controller ID']] = 'Ethernet'
                elif controller['Controller Protocol'] == 'Serial':
                    client = ModbusSerialClient(method="rtu", port=controller['Controller Driver'], stopbits=1,
                                                bytesize=8, parity="E", baudrate=9600, timeout=0.1)
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
        max_retries = int(os.getenv('CONTROLLER_RETRIES_NUM'))
        retry_delay = float(os.getenv('CONTROLLER_RETRIES_DELAY'))
        connected = False
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
                        connected = True
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
            if connected is False:
                print(f"Controller [{controller_name}] Client NOT connected after {max_retries} retries.")
            # t2 = datetime.now()
            # print(f"..........................elapsed time: {t2 - t1}")

    def controller_info_extractor(self, controller_event: dict):
        for controller_name, controller in self.controller_info.items():
            if controller['Controller ID'] == controller_event['Controller ID']:
                self.controller_info_name = controller_name
                self.controller_info_id = controller['Controller ID']
                self.controller_info_type = controller['Controller Type']
                self.controller_info_protocol = controller['Controller Protocol']
                self.controller_info_ip = controller['Controller IP']
                self.controller_info_port = controller['Controller Port']
                self.controller_info_driver = controller['Controller Driver']
                self.controller_info_unit = controller['Controller Unit']
                self.controller_info_cpi = controller['Controller Count Pin IN']
                self.controller_info_cpo = controller['Controller Count Pin OUT']

    def controller_client_connector(self, client):
        max_retries = int(os.getenv('CONTROLLER_RETRIES_NUM'))
        retry_delay = float(os.getenv('CONTROLLER_RETRIES_DELAY'))
        connected = False
        retries = 0
        while retries < max_retries:
            try:
                if self.controller_client_type_selector(self.controller_info_protocol, client):
                    print(f"Controller [{self.controller_info_name}] Client Connected")
                    connected = True
                    break
                else:
                    print(
                        f"Retrying to connect to controller [{self.controller_info_name}]... ({retries + 1}/{max_retries})")
                    retries += 1
                    time.sleep(retry_delay)
            except Exception as e:
                print(
                    f"Retrying to connect to controller [{self.controller_info_name}]... ({retries + 1}/{max_retries})")
                print(f"Exception: {e}")
                retries += 1
                time.sleep(retry_delay)
        if connected is False:
            print(f"Controller [{self.controller_info_name}] Client NOT connected after {max_retries} retries.")

    def controller_register_creator(self, controller_event: dict):
        registers_list = []
        if self.controller_info_id == controller_event['Controller ID']:
            if self.controller_info_type == 'PLC Delta':
                for pin in controller_event['Pin List']:
                    if self.controller_info_protocol == 'Ethernet':
                        registers_list.append(pin + 2048)
                    elif self.controller_info_protocol == 'Serial':
                        registers_list.append(pin + 2048)
            else:
                print(
                    f"Register Address for Controller \033[1m[{controller['Controller Type']}]\033[0m is Not Defined!")
                registers_list = None
        print(f'{registers_list=}')
        return registers_list
        
    def controller_button_state(self, scenario, write_status, read_status):
        # Function to simulate XOR Gate
        def XOR(A, B):
            return A ^ B

        # Function to simulate NOT Gate
        def NOT(A):
            return not A

        # Function to simulate XNOR Gate
        def XNOR(A, B):
            return NOT(XOR(A, B))

        # Function to simulate NOR Gate
        def NOR(A, B):
            return NOT(A or B)

        button_single = None
        button_dual_set= None
        button_dual_reset = None

        if scenario in ['Auto Alarm', 'Auto Caller']:
            button_single = XNOR(write_status, read_status) 
        elif scenario in ['Manual Alarm ON', 'Relay ON']:
            button_single = write_status and read_status
        elif scenario in ['Manual Alarm OFF', 'Relay OFF']:
            button_single = NOR(write_status, read_status)
        elif scenario in ['Auto Gate']:
            button_dual_set = write_status and read_status
            button_dual_reset = NOT(button_dual_set)
            ##! Think about auto close!
        elif scenario in ['Manual Gate Open']:
            button_dual_set = write_status and read_status
            button_dual_reset = NOT(button_dual_set)
        elif scenario in ['Manual Gate Close']:
            button_dual_reset = write_status or read_status
            button_dual_set = NOT(button_dual_reset)

        return {"button_single":button_single, "button_dual_set":button_dual_set, "button_dual_reset":button_dual_reset}

    def controller_button_to_db(self, button_states, pin_id):
        result = pin_collection.update_badge(button_states, pin_id)
        print(f"update_badge result is: [{result}]")
        print(f"‌Button States of pin [{pin_id}] is: [{button_states}]")

    def controller_output_control(self, client_unit: int, client, pin: int, register: int, write_status: bool):
        retries = int(os.getenv('CONTROLLER_RETRIES_NUM'))
        delay = float(os.getenv('CONTROLLER_RETRIES_DELAY'))
        try:
            operation_completed = False
            for attempt in range(retries):
                if self.controller_info_protocol == 'Ethernet':
                    write_coil = client.write_single_coil(register, write_status)
                elif self.controller_info_protocol == 'Serial':
                    write_coil = client.write_coil(register, write_status)
                else:
                    return None
                if write_coil:
                    time.sleep(delay)  # Give some time for the PLC to process the command
                    read_value = client.read_coils(address=register, count=1, slave=client_unit).bits[0]  # see mixin.py in the site-packages: /home/hoopad/.HBOX/plc_service/venv/lib/python3.8/site-packages/pymodbus/client/mixin.py
                    if read_value == write_status:  # Must be checked for Ethernet: client.read_coils(address=register, count=1, slave=client_unit).bits[0]
                        operation_completed = True
                        print(
                            f"[✔] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> Set [{write_status}]")
                        return True  # Must be modified
                    elif read_value == write_status:
                        print(
                            f"[...] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{write_status}] -> Retrying to Set...([read_coil] Attempt {attempt + 1}/{retries})")
                        self.controller_client_connector(client)
                else:
                    print(
                        f"[...] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{write_status}] -> Retrying to Set...([write_coil] Attempt {attempt + 1}/{retries})")
                    self.controller_client_connector(client)
            if operation_completed is False:
                print(
                    f"[✘] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{write_status}]")
                return False  # Must be modified
        except Exception as e:
            # pass
            print(
                f"[✘] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{write_status}]")
            print(f"Exception: {e}")
            return False  # Must be modified

    def controller_scenario(self, controller_event: dict, client_registers, client):
        for idx, register in enumerate(client_registers):
            if controller_event['Scenario'] in ['Auto Alarm', 'Auto Caller']:
                pin_on_duration = controller_event['Delay List'][idx]
                control_result_on = self.controller_output_control(client_unit=self.controller_info_unit, client=client,
                                                                   pin=controller_event['Pin List'][idx],
                                                                   register=register, write_status=True)
                button_states = self.controller_button_state(scenario=controller_event['Scenario'], write_status=True, read_status=control_result_on)
                print(f"Output Control Result is [{control_result_on}] for [{controller_event['Scenario']}] Scenario")
                self.controller_button_to_db(button_states=button_states, pin_id=controller_event['Pin ID'][idx])

                ##! Must used in thread or programmed on controller -----------------------------------------------------
                time.sleep(pin_on_duration) 
                control_result_off = self.controller_output_control(client_unit=self.controller_info_unit,
                                                                    client=client,
                                                                    pin=controller_event['Pin List'][idx],
                                                                    register=register, write_status=False)
                button_states = self.controller_button_state(scenario=controller_event['Scenario'], write_status=False, read_status=control_result_off)
                self.controller_button_to_db(button_states=button_states, pin_id=controller_event['Pin ID'][idx])
                print(f"Output Control Result [ON] is [{control_result_on}] and [OFF] is [{control_result_off}] after [{pin_on_duration}] delay for [{controller_event['Scenario']}] Scenario")
                ##!--------------------------------------------------------------------------------------------------------

            elif controller_event['Scenario'] in ['Auto Gate', 'Manual Alarm ON', 'Manual Gate Open', 'Relay ON']:
                control_result = self.controller_output_control(client_unit=self.controller_info_unit, client=client,
                                                                pin=controller_event['Pin List'][idx],
                                                                register=register, write_status=True)
                button_states = self.controller_button_state(scenario=controller_event['Scenario'], write_status=True, read_status=control_result)
                self.controller_button_to_db(button_states=button_states, pin_id=controller_event['Pin ID'][idx])
                print(f"Output Control Result is [{control_result}] for [{controller_event['Scenario']}] Scenario")

            elif controller_event['Scenario'] in ['Manual Alarm OFF', 'Manual Gate Close', 'Relay OFF']:
                control_result = self.controller_output_control(client_unit=self.controller_info_unit, client=client,
                                                                pin=controller_event['Pin List'][idx],
                                                                register=register, write_status=False)
                button_states = self.controller_button_state(scenario=controller_event['Scenario'], write_status=False, read_status=control_result)
                self.controller_button_to_db(button_states=button_states, pin_id=controller_event['Pin ID'][idx])
                print(f"Output Control Result is [{control_result}] for [{controller_event['Scenario']}] Scenario")

            else:
                print(f"Scenario is not defined. Write its code 🙂")

    def controller_action(self, controller_event: dict):
        self.controller_info_extractor(controller_event)
        client_registers = self.controller_register_creator(controller_event)
        client = self.clients_list[self.controller_info_id]
        self.controller_scenario(controller_event, client_registers, client)

    def update_controller_info(self, data: dict):
        controller_name = data["name"]
        del data["name"]
        self.controller_info[controller_name] = data
        print("i guess i updated the controller info", self.controller_info)


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

        controller_event_1 = {'Controller ID': 10,
                              'Pin List': [0, 1, 2],
                              'Pin Type': [],
                              'Scenario': ''
                              }

        controller_event_2 = {'Controller ID': 20,
                              'Pin List': [0, 1],
                              'Pin Type': [],
                              'Scenario': ''
                              }

        controller_event_3 = {'Controller ID': 30,
                              'Pin List': [0, 1],
                              'Pin Type': [],
                              'Scenario': ''
                              }

        events = [controller_event_1, controller_event_2, controller_event_3]

        controller = Controller(controller_info)
        for event in events:
            controller.controller_register_creator(controller_info, event)

    elif test_type == 2:
        # controller_info = {
        #             'Delta PLC': {'Controller ID': 10,
        #                             'Controller Type': 'PLC Delta',
        #                             'Controller Protocol': 'Ethernet', 
        #                             'Controller IP': '192.168.10.5', 
        #                             'Controller Port': 502, 
        #                             'Controller Driver': None, 
        #                             'Controller Unit': 1, 
        #                             'Controller Count Pin IN': 8, 
        #                             'Controller Count Pin OUT': 3},

        #             'PLC دلتا': {'Controller ID': 30,
        #                             'Controller Type': 'PLC Delta',
        #                             'Controller Protocol': 'Serial', 
        #                             'Controller IP': None, 
        #                             'Controller Port': None, 
        #                             'Controller Driver': "/dev/ttyUSB0", 
        #                             'Controller Unit': 1, 
        #                             'Controller Count Pin IN': 8, 
        #                             'Controller Count Pin OUT': 4}                                    
        #                             }
        controller_info = {
            'PLC دلتا': {'Controller ID': 30,
                         'Controller Type': 'PLC Delta',
                         'Controller Protocol': 'Serial',
                         'Controller IP': None,
                         'Controller Port': None,
                         'Controller Driver': "/dev/ttyUSB0",
                         'Controller Unit': 1,
                         'Controller Count Pin IN': 8,
                         'Controller Count Pin OUT': 4}
        }

        controller_event_1 = {'Controller ID': 30,
                              'Pin List': [0, 10, 100],
                              'Pin ID': ['ID0', 'ID10', 'ID100'],
                              'Pin Type': [],
                              'Delay List': [1, 1, 1],
                              'Scenario': 'Manual Alarm ON'
                              }

        controller_event_2 = {'Controller ID': 10,
                              'Pin List': [10, 20, 30],
                              'Pin ID': ['ID10', 'ID20', 'ID30'],
                              'Pin Type': [],
                              'Delay List': [100, 200, 300],
                              'Scenario': 'Relay OFF'
                              }

        events = [controller_event_1]
        controller = Controller(controller_info)
        for event in events:
            controller.controller_action(event)
