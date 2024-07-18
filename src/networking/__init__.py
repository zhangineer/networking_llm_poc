# logger_config.py

from loguru import logger
import streamlit as st
import sys
from settings import get_settings

SETTINGS = get_settings()

LOG_LEVEL: str = SETTINGS.log_level.upper()
LOG_FORMAT: str = SETTINGS.log_format

# Initialize and configure the logger
logger.remove()  # Remove default logger

logger.add(
    sys.stderr,
    colorize=True,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
)

logger.add(
    "chat.log",
    colorize=True,
    format=LOG_FORMAT,
    level=LOG_LEVEL,
    rotation="10 MB",
    filter=lambda record: record["extra"].get("log") == "chat",
    serialize=True
)

logger.bind(log="chat").info("This is a test chat log message.")


# # Set format for logs
# log_format = "{time} {level} {extra[log]} {message}"
#
# # Configure logger for chat
# logger.add("chat.log", format=log_format, level="INFO", rotation="1 MB", retention="10 days", enqueue=True, filter=lambda record: record["extra"].get("log") == "chat")
#
# # Configure logger for backend calls
# logger.add("backend.log", format=log_format, level="INFO", rotation="1 MB", retention="10 days", enqueue=True, filter=lambda record: record["extra"].get("log") == "backend")
#
# # Also log to stdout
# logger.add(sys.stdout, format=log_format, level="INFO")
#
# # Example usage to demonstrate logger setup
# logger.bind(log="init").info("Logger is initialized and configured.")
#
# logger_a = logger.bind(name="chat.log")
# logger_b = logger.bind(name="backend.log")
#
# logger_a.info("Message A")
# logger_b.info("Message B")

#
# @st.cache_resource
# def chat_function():
#     logger.bind(log="chat").info("This is a log message for the chat module.")
#
#
# @st.cache_resource
# def backend_function():
#     logger.bind(log="backend").info("This is a log message for the backend module.")
#

# import logging
# import logging.handlers
#
#
# def create_logger(filename, name=__name__):
#     # Create a logger object
#     logger = logging.getLogger(name)
#
#     logger.propagate = False
#
#     # Set the desired logging level to DEBUG for dev purposes, this should be changed to WARNING in production
#     # this is only the threshold, actual message types to log will be defined in each scenario individually
#     logger.setLevel(logging.DEBUG)
#
#     log_file = filename
#     max_log_size = 1024 * 1024 # max size = 1 MB
#     file_handler = logging.handlers.RotatingFileHandler(filename=log_file, maxBytes=max_log_size, backupCount=5)
#     file_handler.setLevel(logging.DEBUG)
#
#     # This is for console logging
#     ch = logging.StreamHandler()
#     ch.setLevel(logging.WARNING)
#
#     # Create a formatter
#     formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
#
#     # Add formatter to the console handler
#     file_handler.setFormatter(formatter)
#     ch.setFormatter(formatter)  # Optionally set formatter for console handler as well
#
#     # Add console handler to logger
#     logger.addHandler(file_handler)
#     logger.addHandler(ch)
#     logger.info("________________________________Begin Logging________________________________")
#
#     return logger
