
import time
from datetime import datetime
from pyModbusTCP.client import ModbusClient
from pymodbus.client import ModbusSerialClient
from utils.logger.logger_controller import ControllerLogger


class Controller:
    def __init__(self):
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
                                'Controller Name': [Controller ID, Controller Type, Controller Protocol, Controller IP, Controller Port, 
                                                    Controller Driver, Controller Unit , Controller Count Pin IN, Controller Count Pin OUT]                                              
                                }

                    Validation:
                        Controller Name -> str : Arbitrary Name
                        Controller ID -> int : Arbitrary Number (1, 2, ...)
                        Controller Type -> str : Fixed Names (PLC Delta, PLC Siemens, ARM Micro-controller, Relay Module)
                        Controller Protocol -> str : Fixed Names (Ethernet, Serial)
                        Controller IP -> str/NoneType : IP Address
                        Controller Port -> int/NoneType : Port Address
                        Controller Driver -> str/NoneType : Based on Serial Port Name ("/dev/ttyUSBx" on Ubuntu , 'COMx' on Windows)
                        Controller Unit -> int/NoneType : Based on Clients Number (Clients IDs)
                        Controller Count Pin IN -> int/NoneType : Number of Input Pins
                        Controller Count Pin Out -> int/NoneType : Number of Output Pins

                Example:
                    controller_info = {
                                'Delta PLC': [3, 'PLC Delta', 'Ethernet', '192.168.10.5', 502, None, 1, 8, 4],
                                'bluepill': [20, 'ARM Micro-controller', 'Serial', None, None, "/dev/ttyUSB0", 2, 10, 10],
                                'ماژول رله': [100, 'Relay Module', 'Ethernet', '192.168.10.16', 502, None, None, 0, 4]
                                }
            
        """
        # Initialize logger
        self.logger = ControllerLogger()

        # Log the initialization
        self.logger.info("................Controller initialized................")