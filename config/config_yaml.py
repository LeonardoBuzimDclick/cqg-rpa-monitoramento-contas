import sys

import yaml
from yaml import SafeLoader


def busca_valor_yaml() -> dict:
    """
    Esta função busca valores dentro de um arquivo yaml denominado como application.
    :return: retorna os valores que pertencem ao arquivo yaml.
    """
    with open(f'application-{sys.argv[1]}.yaml') as f:
        return yaml.load(f, Loader=SafeLoader)

