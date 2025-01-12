import logging
import os

class ControllerLogger():
    def __init__(self):            
        # Configure the first logger
        logger = logging.getLogger('Controller_Logger')
        logger.setLevel(logging.INFO)

        # Create a file handler for the first logger
        file_handler = logging.FileHandler(os.getenv("CONTROLLER_LOG_ADDRESS"))
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

        try:
            print("........controller log created.............")
            log_message = f"................Controller Log Started................"
            logger.info(log_message)
        except Exception as e:
            log_message = f"Controller Logging Exception -> {e}"
            logger.error(log_message)
            print(f"Controller Logging Exception -> {e}")
