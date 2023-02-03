from itertools import groupby


def agrupa_listas_rm(list_dict: list) -> list:
    """
    Esta função agrupa as listas rm.
    :param list_dict: (list): recebe uma lista.
    :return: retorna um lista consolidada.
    """
    INFO = sorted(list_dict, key=key_func_rm)
    resutado = []
    for key, value in groupby(INFO, key_func_rm):
        resutado.append(list(value))
    return resutado


def agrupa_listas_consolidada(list_dict: list) -> list:
    """
    Esta função agrupa listas.
    :param list_dict: (list): recebe uma lista.
    :return: retorna um lista consolidada.
    """
    INFO = sorted(list_dict, key=key_func_consolidada)
    resutado = []
    for key, value in groupby(INFO, key_func_consolidada):
        resutado.append(list(value))
    return resutado


def key_func_consolidada(k: dict):
    """
    Esta função retorna o valor perante a uma chave padrão.
    usado para a consolidada
    :param k: (dict): o dictionario.
    :return: retorna o valor.
    """
    return k['sig_usuario']


def key_func_rm(k: dict):
    """
    Esta função retorna o valor perante a uma chave padrão.
    usado para o dado do RM
    :param k: (dict): o dictionario.
    :return: retorna o valor.
    """
    return k['email']


def separa_listas(seq: list[any], num: int) -> list[list]:
    """
    Esta função separa listas em páginas.
    :param seq: (list): recebe uma lista como parâmetro.
    :param num: (int): recebe um valor que define em quantas páginas será separada.
    :return: retorna uma lista separa em páginas.
    """
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out
