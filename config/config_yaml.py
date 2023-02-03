import sys

import yaml
from yaml import SafeLoader


def busca_valor_yaml() -> dict:
    """
    Esta função busca valores em yaml.
    :return: retorna os valor desejado.
    """
    with open(f'application-{sys.argv[1]}.yaml') as f:
        return yaml.load(f, Loader=SafeLoader)

