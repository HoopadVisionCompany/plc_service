import sys
import os
import threading
import json

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import time
from datetime import datetime
from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusSerialClient  # Docs: https://pymodbus.readthedocs.io/en/v3.6.9/index.html
from src.controller.logger_controller import ControllerLogger
from src.utils.patterns.singletons import SingletonMeta
from src.utils.controller_dict_creator import create_scenario_pin_dict
from src.pin.service import PinCollectionCreator
from src.subscriber.rabbitmq_publisher import rabbitmq_publisher
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
                    PLC Address	    Modbus Address
                        M0	        002049 (for Ethernet PLCs it starts at 002048 ?)
                        M1	        002050
                        M2	        002051
                        M3	        002052
                        M4	        002053
                        M5	        002054
                        M6	        002055
                        M7	        002056
                        M8	        002057
                        M9	        002058
                        |	        |
                        |	        |
                        |	        |
                        |	        |
                        M1535	    003584

                        DATA REGISTER	
                    PLC Address	    Modbus Address
                        D0	        404097
                        D1	        404098
                        D2	        404099
                        D3	        404100
                        D4	        404101
                        D5	        404102
                        D6	        404103
                        D7	        404104
                        D8	        404105
                        D9	        404106
                        |	        |
                        |	        |
                        |	        |
                        |	        |
                        D4095	    047616
                        
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
                                                    'Controller Count Pin OUT':'',
                                                    'Controller Pins:[]}                                              
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
                        Controller Pins -> list : List of Controller Pins

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
                                              'Controller Count Pin OUT': 4,
                                              'Controller Pins:[1,2]},

                                 'bluepill': {'Controller ID': 'gtht6577gjd88f',
                                              'Controller Type': 'ARM Micro-controller',
                                              'Controller Protocol': 'Serial', 
                                              'Controller IP': None, 
                                              'Controller Port': None, 
                                              'Controller Driver': "/dev/ttyUSB0", 
                                              'Controller Unit': 2, 
                                              'Controller Count Pin IN': 10, 
                                              'Controller Count Pin OUT': 10,
                                              'Controller Pins:[10,20,30]},

                                'ماژول رله': {'Controller ID': 'pjho090909jkkd',
                                              'Controller Type': 'Relay Module',
                                              'Controller Protocol': 'Ethernet', 
                                              'Controller IP': '192.168.1.16', 
                                              'Controller Port': 8080, 
                                              'Controller Driver': None, 
                                              'Controller Unit': None, 
                                              'Controller Count Pin IN': 0, 
                                              'Controller Count Pin OUT': 4,
                                              'Controller Pins:[4]}                                              
                                }          

                --------------------------------------------------------------------------------------------------------------------

                scenarios_info = {'Scenario 1': [{pin_info 1},{pin_info 2},...],
                                  'Scenario 2': [{pin_info 1},{pin_info 2},...],
                                   ...
                                  'Scenario N': [{pin_info 1},{pin_info 2},...]}                      

                Example:
                        scenarios_info = {'Auto Alarm': [{
                                            "_id": "5e572805-a061-4ac9-8e32-2d6f43bcac8c",
                                            "type": "in",
                                            "controller_id": "5d86a0b8-d789-4637-9c61-86617afe6808",
                                            "controller_unit": 1,
                                            "number": 0,
                                            "timer": 2000,
                                            "delay": 1,
                                            "button_dual_reset": None,
                                            "button_dual_set": None,
                                            "button_single": False
                                            },
                                            {
                                            "_id": "aef3c624-37ba-456f-98b3-3d3e9e2a0ac4",
                                            "type": "in",
                                            "controller_id": "5d86a0b8-d789-4637-9c61-86617afe6808",
                                            "controller_unit": 1,
                                            "number": 10,
                                            "timer": 2001,
                                            "delay": 1,
                                            "button_dual_reset": None,
                                            "button_dual_set": None,
                                            "button_single": False
                                            }],
                          'Auto Gate': [{
                                            "_id": "d0616f63-b321-48d7-bb5a-6744d865f44c",
                                            "type": "in",
                                            "controller_id": "5d86a0b8-d789-4637-9c61-86617afe6808",
                                            "controller_unit": 1,
                                            "number": 100,
                                            "timer": None,
                                            "delay": 1,
                                            "button_dual_reset": True,
                                            "button_dual_set": False,
                                            "button_single": None
                                            }]} 
                --------------------------------------------------------------------------------------------------------------------
                controller_event Dictionary Format:
                    controller_event = {'Controller ID':'',
                                        'Pin List': [],
                                        'Pin Type': [],
                                        'Pin ID': [],
                                        'Timer List': [],
                                        'Delay List': [],
                                        'Scenario': ''
                    }

                    Validation:
                        Controller ID -> str : UUID4 (Mongodb)
                        Pin List -> list : List[int] (0, 1, ..., 999)
                        Pin ID -> list : UUID4 (Mongodb)
                        Pin Type -> list : List[str] (Fixed Names: 'in' , 'out')
                        Timer List -> list | NoneType : List[int] (2000, 2001, ..., 2999)
                        Delay List -> list | NoneType : list[float] (in 'second' metric)
                        Scenarios -> str : Fixed Names ('Auto Alarm' , 'Auto Caller' , 'Auto Gate' , Manual Alarm ON' , 'Manual Alarm OFF', 'Manual Gate Open' , 'Manual Gate Close', 'Relay ON' , 'Relay OFF')
                        

                    Example:
                        controller_event = {'Controller ID': 'gtht6577gjd88f',
                                            'Pin List': [0,1,200],
                                            'Pin ID': ['dasfgdeg', 'f324f4f', 'hgh6h6h'],
                                            'Pin Type': [],
                                            'Timer List': [2001,2100,0],
                                            'Delay List':[3,1.2,0.04],
                                            'Scenario': 'Auto Alarm'}

                        'Pin List': [0,1,200] -> 0 is Y0 or M0 Register (depends on PLC program) for Delta PLCs , 1 is Y1 or M1 Register (depends on PLC program) for Delta PLCs, 200 is M200 Register (must programmed on PLC) for Delta PLCs
                        'Timer List': [2000,2001,2999] -> 2000 is D2000 corresponding to the timer (Tx) that is programmed on PLC (for example: ATMR T2 D2000). Note: Data registers from 0 to 1999 are not 'latch' so not be used. Also, Timers from T0 to T127 must be used in PLC program (because of the Base Time)
                        'Delay List':[3,1.2,0.04] -> delay (second) corresponding to the value of Data Registers (for example: delay between ON and OFF state of 0 pin:
                                                                                                                                |M0|-----------------------------|SET Y2|
                                                                                                                                |YD|-----|ATMR T2 D2000|---------|RST Y2|) 
        """
    def __init__(self, controller_info):

        # Initialize logger
        self.controller_logger = ControllerLogger()
        
        scenarios_info = create_scenario_pin_dict()
        self.controller_info = controller_info

        self.lock = threading.Lock()        
        self.thread_controller_clients_definition = threading.Thread(target=self.controller_clients_definition, args=(controller_info,), daemon=True)
        self.thread_controller_clients_definition.start()

        self.thread_controller_state_monitor = threading.Thread(target=self.controller_state_monitor, args=(scenarios_info,), daemon=True)
        self.thread_controller_state_monitor.start()

        # Log the initialization
        self.controller_logger.logger.debug("................Controller class initialized................")
        try:
            log_message = f"Controllers information: {json.dumps(self.controller_info, indent=4, ensure_ascii=False)}"
            self.controller_logger.logger.info(log_message)
            log_message = f"Scenarios information: {json.dumps(scenarios_info, indent=0, ensure_ascii=False)}"
            self.controller_logger.logger.info(log_message)
        except Exception as e:
            log_message = f"Exception in Controllers and Scenarios Logging: {e}"
            self.controller_logger.logger.error(log_message)
            print(log_message)

    def controller_clients_heartbeat(self):
        "rabbitmq_publisher()" #! rabbitmq_publisher()
        pass

    def controller_clients_definition(self, controller_info):
        with self.lock:
            self.clients_list, self.clients_protocol = self.controller_clients_creator(controller_info)
            self.controller_clients_initial_connector(self.clients_list, self.clients_protocol, controller_info)
        log_message = "Clients definition thread run"
        self.controller_logger.logger.debug(log_message)

    def controller_clients_creator(self, controller_info: dict):
        clients_list = {}
        clients_protocol = {}
        for controller_name, controller in controller_info.items():
            if controller['Controller Type'] == 'PLC Delta':
                if controller['Controller Protocol'] == 'Ethernet':
                    client = ModbusClient(host=controller['Controller IP'],
                                          port=controller['Controller Port'],
                                          timeout=3, 
                                          unit_id=controller['Controller Unit'])
                    clients_list[controller['Controller ID']] = client
                    clients_protocol[controller['Controller ID']] = 'Ethernet'
                elif controller['Controller Protocol'] == 'Serial':
                    client = ModbusSerialClient(method="rtu",
                                                port=controller['Controller Driver'], 
                                                stopbits=1,
                                                bytesize=8,
                                                parity="E",
                                                baudrate=9600,
                                                timeout=0.1)
                    clients_list[controller['Controller ID']] = client
                    clients_protocol[controller['Controller ID']] = 'Serial'

                log_message = f"✅ Client for [{controller_name}] controller created"
                self.controller_logger.logger.info(log_message)
                log_message = f"Client information of [{controller_name}]: [{client}]"
                self.controller_logger.logger.debug(log_message)
            else:
                clients_list[controller['Controller ID']] = None
                clients_protocol[controller['Controller ID']] = None
                log_message = f"❌ Client for [{controller_name}] controller is not defined!"
                self.controller_logger.logger.error(log_message)
                print(log_message)


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
                        log_message = f"✅ Client for [{controller_name}] controller connected"
                        self.controller_logger.logger.info(log_message)
                        print(log_message)
                        connected = True
                        break
                    else:
                        log_message = f"🔄 Retrying to connect to [{controller_name}] controller... ({retries + 1}/{max_retries})"
                        self.controller_logger.logger.warning(log_message)
                        print(log_message)
                        retries += 1
                        time.sleep(retry_delay)
                except Exception as e:
                    log_message = f"🔄 Retrying to connect to [{controller_name}] controller... ({retries + 1}/{max_retries})"
                    self.controller_logger.logger.warning(log_message)
                    print(log_message)
                    log_message = f"Exception in controller_clients_initial_connector(): {e}"
                    self.controller_logger.logger.error(log_message)
                    print(log_message)                    
                    retries += 1
                    time.sleep(retry_delay)
            if connected is False:
                log_message = f"❌ Client for [{controller_name}] controller NOT connected after [{max_retries}] retries."
                self.controller_logger.logger.error(log_message)
                print(log_message)    
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
                    log_message = f"✅ Client for [{self.controller_info_name}] controller connected AGAIN"
                    self.controller_logger.logger.info(log_message)
                    print(log_message)
                    connected = True
                    break
                else:
                    log_message = f"🔄 Retrying to connect AGAIN to [{self.controller_info_name}] controller... ({retries + 1}/{max_retries})"
                    self.controller_logger.logger.warning(log_message)
                    print(log_message)
                    retries += 1
                    time.sleep(retry_delay)
            except Exception as e:
                log_message = f"🔄 Retrying to connect AGAIN to [{self.controller_info_name}] controller... ({retries + 1}/{max_retries})"
                self.controller_logger.logger.warning(log_message)
                print(log_message)
                log_message = f"Exception in controller_client_connector(): {e}"
                self.controller_logger.logger.error(log_message)
                print(log_message)   
                retries += 1
                time.sleep(retry_delay)
        if connected is False:
            log_message = f"❌ Client for [{self.controller_info_name}] controller NOT connected AGAIN after [{max_retries}] retries."
            self.controller_logger.logger.error(log_message)
            print(log_message)  

    def controller_register_creator(self, controller_event={}, pin=0, create_from_controller_event=True):
        if create_from_controller_event:
            registers_list = []
            if self.controller_info_id == controller_event['Controller ID']:
                if self.controller_info_type == 'PLC Delta':
                    for pin in controller_event['Pin List']:
                        if self.controller_info_protocol == 'Ethernet':
                            registers_list.append(pin + 2048) ##! Must be tested using an Ethernet PLC
                        elif self.controller_info_protocol == 'Serial':
                            registers_list.append(pin + 2048)
                else:
                    print(
                        f"Register Address for Controller \033[1m[{controller['Controller Type']}]\033[0m is Not Defined!")
                    registers_list = None
            print(f'{registers_list=}')
            return registers_list
        else:
            return pin + 2048

    def controller_timer_handler(self, timer, delay, client, client_unit, option='w'):
        if option == 'w':
            # Modbus protocol, you typically subtract 400001 when using function codes 0x03 (read holding registers) and 0x06 (write single register):
            address = timer + 404097 - 400001 
            result = client.write_register(address, delay*10, client_unit) # delay coefficient (10) is only for T0 to T127 timers
            print(f"{result=}")
            return result
        elif option == 'r':
            result = client.read_holding_registers(address, 1, client_unit)
            print(result.registers[0])
            return result.registers[0]

    def controller_state_monitor(self, scenarios_info: dict):
            log_message = "state monitor thread run"
            self.controller_logger.logger.debug(log_message)
            scenarios_info_temp = scenarios_info
            for pin_info_list in scenarios_info_temp.values():
                for pin_info in pin_info_list:
                    register = self.controller_register_creator(pin=pin_info['number'], create_from_controller_event=False)
                    state = self.controller_register_read_value(client=self.clients_list[pin_info['controller_id']], register=register, client_unit=pin_info['controller_unit'])
                    pin_info['previous_state'] = state
                    pin_info['register'] = register
                    pin_info['client'] = self.clients_list[pin_info['controller_id']]
            while True:
                # log_message = 'threaaaaaaaaaaaaaad' #! temp
                # self.controller_logger.logger.debug(log_message) #! temp
                # print(log_message) #! temp
                try:
                    with self.lock:
                        for scenario, pin_info_list in scenarios_info_temp.items():
                            for pin_info in pin_info_list:
                                current_state = self.controller_register_read_value(client=pin_info['client'], register=pin_info['register'], client_unit=pin_info['controller_unit'])
                                if current_state != pin_info['previous_state']:
                                    # if scenario in ['Auto Alarm', 'Auto Caller']: ##! Temporary Commented
                                    if True: #! Temporary
                                        log_message = f"Button State of pin [{pin_info['number']}] changed"
                                        self.controller_logger.logger.info(log_message) 
                                        pin_info['button_single'] = current_state
                                        pin_info['previous_state'] = current_state
                                        # time.sleep(1) #! temp
                                    else:
                                        pass ##! Other Scenarios Must Be Implemented
                                    current_pin_buttons_state = {'button_single':pin_info['button_single'],
                                                                'button_dual_set':pin_info['button_dual_set'],
                                                                'button_dual_reset':pin_info['button_dual_reset']}
                                    self.controller_button_to_db(button_states=current_pin_buttons_state, pin_id=pin_info['_id'], pin=pin_info['number'])
                                    print(f"Scenario is {scenario} , the pins are {pin_info}, and the button states are {current_pin_buttons_state}")
                except Exception as e:
                    log_message = f"Exception in controller_state_monitor(): {e}"
                    self.controller_logger.logger.error(log_message)
                    print(log_message)
        
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
        button_dual_set = None
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

    def controller_button_to_db(self, button_states, pin_id, pin):
        result = pin_collection.update_badge(button_states, pin_id)
        log_message = f"Button States of pin [{pin}] is: [{button_states}]"
        self.controller_logger.logger.debug(log_message)
        print(log_message)   
        print(f"update_badge result is: [{result}]")

    def controller_register_read_value(self, client, register: int, client_unit: int):
        try:
            value = client.read_coils(address=register, count=1, slave=client_unit).bits[0]  # see mixin.py in the site-packages: /home/hoopad/.HBOX/plc_service/venv/lib/python3.8/site-packages/pymodbus/client/mixin.py
        except:
            value = None
        return value
    
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
                    read_value = self.controller_register_read_value(client=client, register=register, client_unit=client_unit)
                    if read_value == write_status:  # Must be checked for Ethernet: client.read_coils(address=register, count=1, slave=client_unit).bits[0]
                        operation_completed = True
                        log_message = f"✅  [{self.controller_info_name}] Controller -> Output Pin [{pin}] -> Register [{register}] -> Set [{write_status}]"
                        self.controller_logger.logger.info(log_message)
                        print(log_message)
                        return True  # Must be modified
                    elif read_value == write_status:
                        log_message = f"🔄  [{self.controller_info_name}] Controller -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{write_status}] -> Retrying to Set...([read_coil] Attempt {attempt + 1}/{retries})"
                        self.controller_logger.logger.warning(log_message)
                        print(log_message)
                        self.controller_client_connector(client)
                else:
                    log_message = f"🔄  [{self.controller_info_name}] Controller -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{write_status}] -> Retrying to Set...([read_coil] Attempt {attempt + 1}/{retries})"
                    self.controller_logger.logger.warning(log_message)
                    print(log_message)
                    self.controller_client_connector(client)
            if operation_completed is False:
                log_message = f"❌ [{self.controller_info_name}] Controller -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{write_status}]"
                self.controller_logger.logger.error(log_message)
                print(log_message)
                return False  # Must be modified
        except Exception as e:
            log_message = f"❌ [{self.controller_info_name}] Controller -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{write_status}]"
            self.controller_logger.logger.error(log_message)
            print(log_message)
            log_message = f"Exception in controller_output_control(): {e}"
            self.controller_logger.logger.error(log_message)
            print(log_message)
            return False  # Must be modified

    def controller_scenario(self, controller_event: dict, client_registers, client):
        for idx, register in enumerate(client_registers):
            if controller_event['Scenario'] in ['Auto Alarm', 'Auto Caller']:
                self.controller_timer_handler(timer=controller_event['Timer List'][idx],
                                              delay=controller_event['Delay List'][idx],
                                              client=client,
                                              client_unit=self.controller_info_unit)
                control_result_on = self.controller_output_control(client_unit=self.controller_info_unit,
                                                                   client=client,
                                                                   pin=controller_event['Pin List'][idx],
                                                                   register=register,
                                                                   write_status=True)
                button_states = self.controller_button_state(scenario=controller_event['Scenario'], write_status=True, read_status=control_result_on)
                log_message = f"Output Control Result is [{control_result_on}] for [{controller_event['Scenario']}] Scenario"
                self.controller_logger.logger.info(log_message)
                print(log_message)
                self.controller_button_to_db(button_states=button_states, pin_id=controller_event['Pin ID'][idx], pin=controller_event['Pin List'][idx])

            elif controller_event['Scenario'] in ['Auto Gate', 'Manual Alarm ON', 'Manual Gate Open', 'Relay ON']: #! log
                control_result = self.controller_output_control(client_unit=self.controller_info_unit, client=client,
                                                                pin=controller_event['Pin List'][idx],
                                                                register=register, write_status=True)
                button_states = self.controller_button_state(scenario=controller_event['Scenario'], write_status=True, read_status=control_result)
                self.controller_button_to_db(button_states=button_states, pin_id=controller_event['Pin ID'][idx], pin=controller_event['Pin List'][idx])
                print(f"Output Control Result is [{control_result}] for [{controller_event['Scenario']}] Scenario")

            elif controller_event['Scenario'] in ['Manual Alarm OFF', 'Manual Gate Close', 'Relay OFF']: #! log
                control_result = self.controller_output_control(client_unit=self.controller_info_unit, client=client,
                                                                pin=controller_event['Pin List'][idx],
                                                                register=register, write_status=False)
                button_states = self.controller_button_state(scenario=controller_event['Scenario'], write_status=False, read_status=control_result)
                self.controller_button_to_db(button_states=button_states, pin_id=controller_event['Pin ID'][idx], pin=controller_event['Pin List'][idx])
                print(f"Output Control Result is [{control_result}] for [{controller_event['Scenario']}] Scenario")

            else:
                print(f"Scenario is not defined. Write its code 🙂") #! log

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
    test_type = 3
    # def stop_process():
    #     import signal
    #     print("Stopping process...")
    #     os.kill(os.getpid(), signal.SIGTERM)

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

    elif test_type == 3:
        controller_info = {
            'PLC دلتا': {'Controller ID': "5d86a0b8-d789-4637-9c61-86617afe6808",
                         'Controller Type': 'PLC Delta',
                         'Controller Protocol': 'Serial',
                         'Controller IP': None,
                         'Controller Port': None,
                         'Controller Driver': "/dev/ttyUSB0",
                         'Controller Unit': 1,
                         'Controller Count Pin IN': 8,
                         'Controller Count Pin OUT': 4}
        }
        controller = Controller(controller_info)
        scenarios_info = {'Auto Alarm': [{
                                            "_id": "5e572805-a061-4ac9-8e32-2d6f43bcac8c",
                                            "type": "in",
                                            "controller_id": "5d86a0b8-d789-4637-9c61-86617afe6808",
                                            "controller_unit": 1,
                                            "number": 0,
                                            "delay": 1,
                                            "button_dual_reset": None,
                                            "button_dual_set": None,
                                            "button_single": False
                                            },
                                            {
                                            "_id": "aef3c624-37ba-456f-98b3-3d3e9e2a0ac4",
                                            "type": "in",
                                            "controller_id": "5d86a0b8-d789-4637-9c61-86617afe6808",
                                            "controller_unit": 1,
                                            "number": 10,
                                            "delay": 1,
                                            "button_dual_reset": None,
                                            "button_dual_set": None,
                                            "button_single": False
                                            }],
                          'Auto Gate': [{
                                            "_id": "d0616f63-b321-48d7-bb5a-6744d865f44c",
                                            "type": "in",
                                            "controller_id": "5d86a0b8-d789-4637-9c61-86617afe6808",
                                            "controller_unit": 1,
                                            "number": 100,
                                            "delay": 1,
                                            "button_dual_reset": True,
                                            "button_dual_set": False,
                                            "button_single": None
                                            }]}     
        controller.controller_state_monitor(scenarios_info)
        # stop_process()