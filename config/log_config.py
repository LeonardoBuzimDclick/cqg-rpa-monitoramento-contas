import logging
import sys
from datetime import datetime


def ajusta_config_logging(config: dict):
    """
    Esta função ajusta a configuração dos logging.
    :param config: (dict): recebe um configuração.
    """
    filename = f'logs/{config["config"]["logging"]["filename"]}-{datetime.now().strftime("%Y%m%dT%H%M%SZ")}.log'

    logging.basicConfig(filename=filename,
                        level=config["config"]["logging"]["level"],
                        datefmt='%Y-%m-%dT%H:%M:%S',
                        format='%(asctime)s.%(msecs)03dZ;'
                               '%(module)s.%(funcName)s;'
                               '[%(levelname)s];'
                               '[PID-%(process)d];'
                               '%(message)s')
    bot_text_art()
    logging.info(f'A monitoração de contas foi iniciada no perfil: {sys.argv[1]}')


def bot_text_art():
    logging.info("    ____     ")
    logging.info("   [____]    ")
    logging.info(" |=]()()[=|  ")
    logging.info(" __\_\/_/__   _____     _____   _        _____    _____   _  __")
    logging.info("|__|    |__| |  __ \   / ____| | |      |_   _|  / ____| | |/ /")
    logging.info(" |_|_/\_|_|  | |  | | | |      | |        | |   | |      | ' / ")
    logging.info(" | | __ | |  | |  | | | |      | |        | |   | |      |  <  ")
    logging.info(" |_|[  ]|_|  | |__| | | |____  | |____   _| |_  | |____  | . \ ")
    logging.info(" \_|_||_|_/  |_____/   \_____| |______| |_____| \ _____| |_|\_\\")
    logging.info("   |_||_|                                                       ")
    logging.info("  _|_||_|_   ")
    logging.info(" |___||___|  ")
    logging.info("             ")


