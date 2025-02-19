import sys
import os
import logging
import time
from datetime import datetime
from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusSerialClient
from src.controller.logger_controller import ControllerLogger
from src.utils.patterns.singletons import SingletonMeta
from dotenv import load_dotenv

load_dotenv()

# Set up basic logging configuration
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.DEBUG,  # You can set this to DEBUG, INFO, WARNING, ERROR, CRITICAL as needed
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("controller.log", mode="w")
    ]
)
logger = logging.getLogger(__name__)

class Controller(metaclass=SingletonMeta):
    def __init__(self, controller_info):
        """
        Controller initialization and setup
        """
        # Initialize logger
        self.controller = ControllerLogger()

        # Log the initialization
        logger.info("................Controller initialized................")

        self.controller_info = controller_info
        self.clients_list, self.clients_protocol = self.controller_clients_creator(controller_info)
        self.controller_clients_initial_connector(self.clients_list, self.clients_protocol, controller_info)

    def controller_clients_creator(self, controller_info: dict):
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
                logger.warning(f"Controller [{controller_name}] Client is Not Defined!")
                clients_list[controller['Controller ID']] = None
                clients_protocol[controller['Controller ID']] = None
        return clients_list, clients_protocol

    def controller_client_type_selector(self, client_protocol: str, client):
        if client_protocol == 'Ethernet':
            return client.open()
        elif client_protocol == 'Serial':
            return client.connect()
        else:
            logger.critical(f"Invalid protocol type: {client_protocol}")
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
            while retries < max_retries:
                try:
                    if self.controller_client_type_selector(clients_protocol[controller_id], client):
                        logger.info(f"Controller [{controller_name}] Client Connected")
                        connected = True
                        break
                    else:
                        logger.warning(f"Retrying to connect to controller [{controller_name}]... ({retries + 1}/{max_retries})")
                        retries += 1
                        time.sleep(retry_delay)
                except Exception as e:
                    logger.error(f"Error while connecting to controller [{controller_name}] on retry {retries + 1}/{max_retries}. Exception: {e}")
                    retries += 1
                    time.sleep(retry_delay)
            if not connected:
                logger.critical(f"Controller [{controller_name}] Client NOT connected after {max_retries} retries.")

    def controller_info_extractor(self, controller_event: dict):
        for controller_name, controller in self.controller_info.items():
            if controller['Controller ID'] == controller_event['Controller ID']:
                self.controller_info_name =  controller_name
                self.controller_info_id =  controller['Controller ID']
                self.controller_info_type =  controller['Controller Type']
                self.controller_info_protocol =  controller['Controller Protocol']
                self.controller_info_ip =  controller['Controller IP']
                self.controller_info_port =  controller['Controller Port']
                self.controller_info_driver =  controller['Controller Driver']
                self.controller_info_unit =  controller['Controller Unit']
                self.controller_info_cpi =  controller['Controller Count Pin IN']
                self.controller_info_cpo =  controller['Controller Count Pin OUT']

    def controller_client_connector(self, client):
        max_retries = int(os.getenv('CONTROLLER_RETRIES_NUM'))
        retry_delay = float(os.getenv('CONTROLLER_RETRIES_DELAY'))
        connected = False 
        retries = 0
        while retries < max_retries:
            try:
                if self.controller_client_type_selector(self.controller_info_protocol, client):
                    logger.info(f"Controller [{self.controller_info_name}] Client Connected")
                    connected = True
                    break
                else:
                    logger.warning(f"Retrying to connect to controller [{self.controller_info_name}]... ({retries + 1}/{max_retries})")
                    retries += 1
                    time.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Error while connecting to controller [{self.controller_info_name}] on retry {retries + 1}/{max_retries}. Exception: {e}")
                retries += 1
                time.sleep(retry_delay)
        if not connected:
            logger.critical(f"Controller [{self.controller_info_name}] Client NOT connected after {max_retries} retries.")

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
                logger.warning(f"Register Address for Controller \033[1m[{self.controller_info_type}]\033[0m is Not Defined!")
                registers_list = None
        logger.debug(f'{registers_list=}')
        return registers_list
    
    def controller_output_control(self, client_unit: int, client, pin: int, register: int, status: bool):
        retries = int(os.getenv('CONTROLLER_RETRIES_NUM'))
        delay = float(os.getenv('CONTROLLER_RETRIES_DELAY'))
        try:
            operation_completed = False
            for attempt in range(retries):
                if self.controller_info_protocol == 'Ethernet':
                    write_coil = client.write_single_coil(register, status)
                elif self.controller_info_protocol == 'Serial':
                    write_coil = client.write_coil(register, status)
                else:
                    logger.critical(f"Unknown protocol for controller {self.controller_info_name}")
                    return None
                if write_coil:
                    time.sleep(delay)  # Give some time for the PLC to process the command
                    read_value = client.read_coils(address=register, count=1, slave=client_unit).bits[0]
                    if read_value == status:
                        operation_completed = True
                        logger.info(f"[✔] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> Set [{status}]")
                        return True
                    else:
                        logger.warning(f"[...] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{status}] -> Retrying... ([read_coil] Attempt {attempt + 1}/{retries})")
                        self.controller_client_connector(client)
                else:
                    logger.warning(f"[...] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{status}] -> Retrying... ([write_coil] Attempt {attempt + 1}/{retries})")
                    self.controller_client_connector(client)
            if not operation_completed:
                logger.critical(f"[✘] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{status}]")
                return False
        except Exception as e:
            logger.critical(f"[✘] Controller [{self.controller_info_name}] -> Output Pin [{pin}] -> Register [{register}] -> NOT Set [{status}]. Exception: {e}")
            return False

    def controller_scenario(self, controller_event: dict, client_registers, client):
        for idx, register in enumerate(client_registers):
            if controller_event['Scenario'] in ['Auto Alarm', 'Auto Caller']:
                pin_on_duration = controller_event['Delay List'][idx]
                control_result_on = self.controller_output_control(client_unit=self.controller_info_unit, client=client, pin=controller_event['Pin List'][idx], register=register, status=True)
                time.sleep(pin_on_duration)
                control_result_off = self.controller_output_control(client_unit=self.controller_info_unit, client=client, pin=controller_event['Pin List'][idx], register=register, status=False)
                logger.info(f"Output Control Result [ON] is [{control_result_on}]")
                logger.info(f"Output Control Result [OFF] is [{control_result_off}]")
            elif controller_event['Scenario'] == 'Monitoring':
                # Insert Monitoring logic if necessary
                pass
