import logging
import sys
from logging import handlers
import os


path_logs = "./logs"

def get_loger(loger_name, tag = "global") -> logging.LoggerAdapter:
    log = logging.getLogger(loger_name)
    log.setLevel(logging.INFO)
    log = logging.LoggerAdapter(log, {"tag": tag})
    return log


def init_loger(loger_name: str, tag = True):
    handler = logging.StreamHandler(sys.stdout)
    if tag:
        logging_format = logging.Formatter("[%(asctime)s][%(levelname)s][%(tag)s]: %(message)s")
    else:
        logging_format = logging.Formatter("[%(asctime)s][%(levelname)s]: %(message)s")
    handler.setFormatter(logging_format)
    logging.getLogger(loger_name).addHandler(handler)
    if not os.path.exists(path_logs):
        os.makedirs(path_logs)
    log_file_name = "{0}.log".format(loger_name)
    log_file_path = os.path.join(path_logs, log_file_name)
    handler = logging.handlers.TimedRotatingFileHandler(log_file_path, when="midnight", encoding='UTF-8',
                                                        backupCount=30)
    handler.suffix = "%Y-%m-%d"
    handler.setFormatter(logging_format)
    logging.getLogger(loger_name).addHandler(handler)
