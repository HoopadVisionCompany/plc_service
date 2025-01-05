
import time
from datetime import datetime
from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusSerialClient

from configs.database import client


class PLC:
    # recent_opened_plate = deque(maxlen=5)
    recent_opened_plate = {}

    @staticmethod
    def __init__(gates_info):
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

        - Input Data Format (for HPlate):
            gate_info format:
                gates_info = {
                            'Gate Name 1': [Gate ID, PLC Brand, PLC Connection Type, PLC IP, PLC Port, PLC COM Address, PLC Output],
                            'Gate Name 2': [Gate ID, PLC Brand, PLC Connection Type, PLC IP, PLC Port, PLC COM Address, PLC Output],
                            'Gate Name 3': [Gate ID, PLC Brand, PLC Connection Type, PLC IP, PLC Port, PLC COM Address, PLC Output],
                            'Gate Name 4': [Gate ID, PLC Brand, PLC Connection Type, PLC IP, PLC Port, PLC COM Address, PLC Output],
                            'Gate Name 5': [Gate ID, PLC Brand, PLC Connection Type, PLC IP, PLC Port, PLC COM Address, PLC Output],
                            'Gate Name 6': [Gate ID, PLC Brand, PLC Connection Type, PLC IP, PLC Port, PLC COM Address, PLC Output]
                            }

            for example:
                gates_info = {
                            'gate A': [10, 'Delta', 'Ethernet', '192.168.10.5', 502, No PLC, 1],
                            'راه بند جنوبی': [20, 'Delta', 'Serial', No PLC, No PLC, "/dev/ttyUSB0", 3],
                            'X': [30, 'Delta', 'Ethernet', '192.168.10.16', 502, No PLC, 6]
                            }
        """
        global logger
        # global #logger_other
        print("___________________________INIT PLC_____________________________________________________")
        log_message = "___________________________INIT PLC_____________________________________________________\n"
        logger.info(log_message)

        print(f"{gates_info=}")
        PLC.gates = list(gates_info.values())
        print(f"{PLC.gates=}")

        ## PLC Address Register (Lookup Table)
        PLC.address_list_plc_serial = {
            1: 2049,
            2: 2050,
            3: 2051,
            4: 2052,
            5: 2053,
            6: 2054,
            7: 2055
        }

        PLC.address_list_plc_ethernet = {
            1: 2048,
            2: 2049,
            3: 2050,
            4: 2051,
            5: 2052,
            6: 2053
        }

        ## PLC Initialization
        PLC.client_list = []
        PLC.gate_ids = []
        PLC.output_list = []

        print(list(gates_info.values()), 'list///////////////////////////////////')
        for i in range(len(list(gates_info.values()))):
            if PLC.gates[i][1] == "Delta" and PLC.gates[i][2] == "Serial":
                client = ModbusSerialClient(method="rtu", port=PLC.gates[i][5], stopbits=1, bytesize=8, parity="E",
                                            baudrate=9600, timeout=0.1)
                PLC.client_list.append(client);
                PLC.gate_ids.append(PLC.gates[i][0]);
                PLC.output_list.append(PLC.gates[i][-1])
                logger.info(f"Delta & Serial client created successfully for Gate {i}")
            elif PLC.gates[i][1] == "Delta" and PLC.gates[i][2] == "Ethernet":
                try:
                    client = ModbusClient(host=PLC.gates[i][3], port=PLC.gates[i][4], timeout=3, unit_id=2)
                    PLC.client_list.append(client);
                    PLC.gate_ids.append(PLC.gates[i][0]);
                    PLC.output_list.append(PLC.gates[i][-1])
                    log_message = "Clients created correctly:"
                    logger.info(log_message)
                    log_message = f"Clients list -> {PLC.client_list}"
                    logger.info(log_message)
                except Exception as e:
                    log_message = f"Clients NOT created:"
                    logger.error(log_message)
                    log_message = f"{e}"
                    logger.error(log_message)

            elif PLC.gates[i][1] == "Siemens" and PLC.gates[i][2] == "Serial":
                pass
            elif PLC.gates[i][1] == "Siemens" and PLC.gates[i][2] == "Ethernet":
                pass
            elif PLC.gates[i][1] == None and PLC.gates[i][2] == "No PLC":
                PLC.client_list.append(None)
                PLC.gate_ids.append(PLC.gates[i][0])
                PLC.output_list.append(PLC.gates[i][-1])
        print(f"{PLC.client_list=}")
        print('IDSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS')
        print(f"{PLC.gate_ids=}")

    @staticmethod
    def open_clients():
        print("Start open clients")
        alarm_status("OFF")
        for i in range(len(PLC.gate_ids)):
            max_retries = 5
            retry_delay = 3
            created = False
            client = PLC.client_list[i]

            if PLC.gates[i][1] == "Delta" and PLC.gates[i][2] == "Serial":
                retries = 0
                while retries < max_retries:
                    try:
                        if client.connect():
                            print(f"PLC with ID {PLC.gates[i][0]}: Connection established.")
                            break
                        else:
                            print(
                                f"Retrying to connect to PLC with ID {PLC.gates[i][0]}... ({retries + 1}/{max_retries})")
                            retries += 1
                            time.sleep(retry_delay)
                    except Exception as e:
                        print(f"Error: {e}")
                        retries += 1
                        time.sleep(retry_delay)
            elif PLC.gates[i][1] == "Delta" and PLC.gates[i][2] == "Ethernet":
                retries = 0
                t1 = datetime.now()
                while retries < max_retries:
                    try:
                        if client.open():
                            print(f"PLC with ID {PLC.gates[i][0]}: Connection established.")
                            logger.info(f"PLC with ID {PLC.gates[i][0]}: Connection established.")
                            created = True
                            break
                        else:
                            print(
                                f"Retrying to connect to PLC with ID {PLC.gates[i][0]}... ({retries + 1}/{max_retries})")
                            logger.warning(
                                f"Retrying to connect to PLC with ID {PLC.gates[i][0]}... ({retries + 1}/{max_retries})")
                            retries += 1

                            time.sleep(retry_delay)
                    except Exception as e:
                        log_message = f"[Gate Client {PLC.gates[i][0]}] retrying to connect...({retries + 1}/{max_retries})"
                        logger.error(log_message)
                        log_message = f"Client Connection Error: {e}"
                        logger.error(log_message)
                        print(f"Error: {e}")
                        retries += 1
                        time.sleep(retry_delay)
                if created is False:
                    log_message = f"[Gate Client {PLC.gates[i][0]}] NOT Created after {max_retries} retries."
                    logger.error(log_message)
                t2 = datetime.now()
                print(f"..........................elapsed time: {t2 - t1}")

    ## Gate Openning using recognized license plates
    @staticmethod
    def open_gate(gate_id, plate_string):

        global logger
        print('PLCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC', PLC.recent_opened_plate)
        # print(f"{plate_string=}")
        # print(f"{PLC.recent_opened_plate.keys()=}")
        # if (plate_string not in PLC.recent_opened_plate.keys()) or (
        #         datetime.now() - PLC.recent_opened_plate[plate_string]).seconds > int(os.getenv("SAME_PLATE_TIMEOUT")):
        #     print('----------------------OPEN1--------------------------------')
        #     print(PLC.gate_ids, '---------', gate_id)
        index = PLC.gate_ids.index(gate_id)
        #     print(f"{PLC.client_list[index]=}")
        #     print('----------------------OPEN2--------------------------------')
        if PLC.gates[index][1] == "Delta" and PLC.gates[index][2] == "Serial":
            client = PLC.client_list[index]
            # print('----------------------OPEN3--------------------------------')
            # client.write_coil(PLC.address_list_plc_serial[PLC.gates[index][-1]], True, unit=2)
            # print('----------------------OPEN4--------------------------------')
            # PLC.recent_opened_plate[plate_string] = datetime.now()


            # register_address = self.plc_address_serial[output_number] - 1
            register_address = PLC.address_list_plc_serial[1] - 1
            # register_address = 2049
            try:
                opened = False
                for attempt in range(retries):
                    if client.write_coil(register_address, True, unit=1): # Write the coil
                        log_message = f"Serial PLC Coil {register_address} Written True Succsessfully"
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
                        return "True On"
                    else:
                        log_message = f"Serial PLC Coil {register_address} Failed to Write -> Retrying to write on coil {register_address}...(Attempt {attempt+1}/{retries})"
                        logger.warning(log_message)
                        print(log_message)
                if opened is False:
                    log_message = f"Alarm is Not ON"
                    logger.error(log_message)
                    print(log_message)
                    return "False On"
            except Exception as e:
                log_message = f"PLC Serial Problem:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)
                return "False On"

        elif PLC.gates[index][1] == "Delta" and PLC.gates[index][2] == "Ethernet":
            ## ------------------------ MRAG ----------------------------
            retries = 3
            delay = 0.25
            register_address = 2048
            try:
                client = PLC.client_list[index]
                opened = False
                for attempt in range(retries):
                    # Write the coil
                    if client.write_single_coil(register_address, True):
                        log_message = f"[Gate {gate_id}] [Plate {plate_string}] Succsessfully coil {register_address} with write_single_coil() written True"
                        logger.info(log_message)
                        time.sleep(delay)  # Give some time for the PLC to process the command
                        read_value = client.read_coils(register_address, 1)  # Read back the coil value to verify
                        if read_value is not None and read_value[0] == True:
                            opened = True
                            log_message = f"[Gate {gate_id}] [Plate {plate_string}] is opening..."
                            logger.info(log_message)
                            print(
                                f"Gate {gate_id} with output {PLC.output_list[index]} is opening for plate {plate_string}...")
                            PLC.recent_opened_plate[plate_string] = datetime.now()
                            return "True Open Plate"
                        else:
                            log_message = f"[Gate {gate_id}] [Plate {plate_string}] NOT opened -> Retrying to open...(Attempt {attempt + 1}/{retries})"
                            logger.warning(log_message)
                            print(f"Attempt {attempt + 1}: Coil {register_address} not set correctly. Retrying...")
                    else:
                        log_message = f"[Gate {gate_id}] [Plate {plate_string}] Failed to write with write_single_coil() -> Retrying to write on coil {register_address}...(Attempt {attempt + 1}/{retries})"
                        logger.warning(log_message)
                        print(f"Attempt {attempt + 1}: Failed to write to coil {register_address}. Retrying...")
                if opened is False:
                    log_message = f"[Gate {gate_id}] [Plate {plate_string}] NOT opened!"
                    logger.error(log_message)
                    print("Failed to write and verify coil value after retries.")
                    return "False Open Plate"
            except Exception as e:
                log_message = f"[Gate {gate_id}] [Plate {plate_string}] [Client {client}] NOT opened:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)
                return "False Open Plate"

    # else:
    #     log_message = f"[Gate {gate_id}] [Plate {plate_string}] NOT opened (Same Plate Seen)"
    #     logger.warning(log_message)
        ## ------------------------ MRAG ----------------------------
        return None

    ## Manual Gate Openning using "OPEN" button in UI
    @staticmethod
    def manual_open_gate(gate_id):
        global logger
        index = PLC.gate_ids.index(gate_id)
        if PLC.gates[index][1] == "Delta" and PLC.gates[index][2] == "Serial":
            retries = 2
            delay = 0.1
            phone_delay = 4
            client = PLC.client_list[index]
            # print('----------------------OPEN3--------------------------------')
            # client.write_coil(PLC.address_list_plc_serial[PLC.gates[index][-1]], True, unit=2)
            # print('----------------------OPEN4--------------------------------')
            # PLC.recent_opened_plate[plate_string] = datetime.now()


            # register_address = self.plc_address_serial[output_number] - 1
            register_address_alarm = PLC.address_list_plc_serial[1] - 1  # M0 register
            register_address_phone = PLC.address_list_plc_serial[7] - 1  # M2 register
            # register_address = 2049
            try:
                opened = False
                for attempt in range(retries):
                    if client.write_coil(register_address_alarm, True, unit=1): # Write the coil
                        log_message = f"Serial PLC Coil for Alarm {register_address_alarm} Written True Succsessfully"
                        logger.info(log_message)

                        if client.write_coil(register_address_phone, True, unit=1):
                            log_message = f"Serial PLC Coil for Phone {register_address_phone} Written True Succsessfully"
                            logger.info(log_message)
                            time.sleep(phone_delay)
                            client.write_coil(register_address_phone, False, unit=1)
                            log_message = f"Serial PLC Coil for Phone {register_address_phone} after {phone_delay} Second(s) Written False Succsessfully"
                            logger.info(log_message)
                        else:
                            log_message = f"Serial PLC Coil for Phone {register_address_phone} Failed to Write True"
                            logger.warning(log_message)

                        opened = True
                        alarm_status("ON")

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
                        return True
                    else:
                        log_message = f"Serial PLC Coil for Alarm {register_address_alarm} Failed to Write -> Retrying to write on coil {register_address_alarm}...(Attempt {attempt+1}/{retries})"
                        logger.warning(log_message)
                        print(log_message)
                        client.connect()

                if opened is False:
                    log_message = f"Alarm is Not ON"
                    logger.error(log_message)
                    print(log_message)
                    alarm_status("OFF")
                    return False
            except Exception as e:
                log_message = f"PLC Serial Problem:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)
                alarm_status("OFF")
                return False

        elif PLC.gates[index][1] == "Delta" and PLC.gates[index][2] == "Ethernet":
            ## ------------------------ MRAG ----------------------------
            retries = 3
            delay = 0.25
            register_address = PLC.address_list_plc_ethernet[2]
            try:
                client = PLC.client_list[index]
                opened = False
                for attempt in range(retries):
                    # Write the coil
                    if client.write_single_coil(register_address, True):
                        log_message = f"[Gate {gate_id}] Manually Succsessfully coil {register_address} with write_single_coil() written True"
                        logger.info(log_message)
                        time.sleep(delay)  # Give some time for the PLC to process the command
                        read_value = client.read_coils(register_address, 1)  # Read back the coil value to verify
                        if read_value is not None and read_value[0] == True:
                            opened = True
                            log_message = f"[Gate {gate_id}] Manually is opening..."
                            logger.info(log_message)
                            print(f"Gate {gate_id} with output {PLC.output_list[index]} manually is opening...")
                            return "True Open Manual"
                        else:
                            log_message = f"[Gate {gate_id}] Manually NOT opened -> Retrying to open...(Attempt {attempt + 1}/{retries})"
                            logger.warning(log_message)
                            print(f"Attempt {attempt + 1}: Coil {register_address} not set correctly. Retrying...")
                    else:
                        log_message = f"[Gate {gate_id}] Manually Failed to write with write_single_coil() -> Retrying to write on coil {register_address}...(Attempt {attempt + 1}/{retries})"
                        logger.warning(log_message)
                        print(
                            f"Attempt {attempt + 1}: Manually Failed to write to coil {register_address}. Retrying...")
                if opened is False:
                    log_message = f"[Gate {gate_id}] Manually NOT opened!"
                    logger.error(log_message)
                    print("Failed to write and verify coil value after retries.")
            except Exception as e:
                log_message = f"[Gate {gate_id}] [Client {client}] Manually NOT opened:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)

    ## Manual Gate Closing using "CLOSE" button in UI
    @staticmethod
    def manual_close_gate(gate_id):
        global logger
        index = PLC.gate_ids.index(gate_id)

        if PLC.gates[index][1] == "Delta" and PLC.gates[index][2] == "Serial":
            retries = 2
            delay = 0.1
            client = PLC.client_list[index]
            register_address_alarm = PLC.address_list_plc_serial[1] - 1  # M0 register
            register_address_phone = PLC.address_list_plc_serial[7] - 1  # M2 register
            try:
                opened = False
                for attempt in range(retries):
                    if client.write_coil(register_address_alarm, False, unit=1): # Write the coil
                        log_message = f"Serial PLC Coil for Alarm {register_address_alarm} Manually Written False Succsessfully"
                        logger.info(log_message)

                        if client.write_coil(register_address_phone, False, unit=1):
                            log_message = f"Serial PLC Coil for Phone {register_address_phone} Written False Succsessfully"
                            logger.info(log_message)
                        else:
                            log_message = f"Serial PLC Coil for Phone {register_address_phone} Failed to Write False"
                            logger.warning(log_message)

                        opened = True
                        alarm_status("OFF")
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
                        return True
                    else:
                        log_message = f"Serial PLC Coil {register_address_alarm} Failed to Manually Write False -> Retrying to write on coil {register_address_alarm}...(Attempt {attempt+1}/{retries})"
                        logger.warning(log_message)
                        print(log_message)
                        client.connect()

                if opened is False:
                    log_message = f"Alarm is Not OFF"
                    logger.error(log_message)
                    print(log_message)
                    alarm_status("ON")
                    return False
            except Exception as e:
                log_message = f"PLC Serial Problem:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)
                alarm_status("ON")
                return False


        elif PLC.gates[index][1] == "Delta" and PLC.gates[index][2] == "Ethernet":
            ## ------------------------ MRAG ----------------------------
            retries = 3
            delay = 0.25
            register_address = PLC.address_list_plc_ethernet[5]
            try:
                client = PLC.client_list[index]
                opened = False
                for attempt in range(retries):
                    if client.write_single_coil(register_address, True):
                        log_message = f"[Gate {gate_id}] Manually Succsessfully coil {register_address} with write_single_coil() written True"
                        logger.info(log_message)
                        time.sleep(delay)  # Give some time for the PLC to process the command
                        read_value = client.read_coils(register_address, 1)  # Read back the coil value to verify
                        if read_value is not None and read_value[0] == True:
                            opened = True
                            log_message = f"[Gate {gate_id}] Manually is closing..."
                            logger.info(log_message)
                            print(f"Gate {gate_id} with output {PLC.output_list[index]} manually is closing...")
                            return "True Close Manual"
                        else:
                            log_message = f"[Gate {gate_id}] Manually NOT closed -> Retrying to close...(Attempt {attempt + 1}/{retries})"
                            logger.warning(log_message)
                            print(f"Attempt {attempt + 1}: Coil {register_address} not set correctly. Retrying...")
                    else:
                        log_message = f"[Gate {gate_id}] Manually Failed to write with write_single_coil() -> Retrying to write on coil {register_address}...(Attempt {attempt + 1}/{retries})"
                        logger.warning(log_message)
                        print(
                            f"Attempt {attempt + 1}: Manually Failed to write to coil {register_address}. Retrying...")
                if opened is False:
                    log_message = f"[Gate {gate_id}] Manually NOT closed!"
                    logger.error(log_message)
                    print("Failed to write and verify coil value after retries.")
            except Exception as e:
                log_message = f"[Gate {gate_id}] [Client {client}] Manually NOT closed:"
                logger.error(log_message)
                log_message = f"{e}"
                logger.error(log_message)