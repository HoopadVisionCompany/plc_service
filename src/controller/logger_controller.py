import logging
import os

class ControllerLogger():
    def __init__(self):            
        # Configure the first logger
        self.logger = logging.getLogger('controller_log')
        self.logger.setLevel(logging.INFO)

        # Create a file handler for the first logger
        file_handler = logging.FileHandler(os.getenv("CONTROLLER_LOG_ADDRESS"))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        try:
            print("______________Controller Log Started_____________")
            log_message = f"______________Controller Log Started_____________"
            self.logger.info(log_message)
        except Exception as e:
            log_message = f"Controller Logging Exception -> {e}"
            self.logger.error(log_message)
            print(f"Controller Logging Exception -> {e}")
