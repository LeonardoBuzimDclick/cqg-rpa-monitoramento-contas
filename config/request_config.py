import ast
import json
import logging
import time
from typing import Any

import jxmlease
import requests

from config.config_yaml import busca_valor_yaml


def request_post_soap_base(url: str, body: dict, headers=None, is_rm=False) -> list[dict[str, str]] | dict[Any, Any]:
    """
    Esta função obtém um xml em string e retorna uma lista de dicionário e um dicionário.
    :param url: (str): recebe um endpoint.
    :param body: (dict): recebe uma configuração em xml.
    :param headers: (None): recebe um xml em string.
    :param is_rm: (False): Recebe um valor False.
    :return: retorna uma lista de dicionário ou um dicionário.
    """

    logging.debug("-----Inicio do metodo soap post base-----")

    i = 0
    config = busca_valor_yaml()
    time_retry = config['config']['request']['retry_times']

    while i < time_retry:

        if i != 0:
            time.sleep(config['config']['request']['sleep'])

        try:
            i += 1
            response = requests.post(url=url, data=body, headers=headers,
                                     timeout=config['config']['request']['timeout'])

            if response.status_code != 200:
                logging.warning(f"-----Mensagem com erro {i}/{time_retry} tentativas-----")
                continue

            text = jxmlease.parse(response.text)

            logging.debug("-----Fim do metodo soap post base-----")

            if is_rm:

                xml_response = text['s:Envelope']['s:Body']['RealizarConsultaSQLResponse'][
                    'RealizarConsultaSQLResult']
                xml_response_list = jxmlease.parse(xml_response)['NewDataSet']['Resultado']
                return transforma_lista_xml_em_list_dict(xml_response_list)

            else:
                return transforma_xml_em_dict(
                    text['soap:Envelope']['soap:Body']['ns1:getDatasetResponse']['dataset']['columns'],
                    text['soap:Envelope']['soap:Body']['ns1:getDatasetResponse']['dataset']['values'])

        except requests.exceptions.RequestException as e:
            logging.exception(e.errno)
            logging.debug(f"-----Houve um erro na hora de requisitar {i}/{time_retry} tentativas-----")
            if i == time_retry:
                raise e


def transforma_lista_xml_em_list_str(lst: list) -> list:
    """
    Esta função obtém uma lista xml e retorna uma lista.
    :param lst: (list): recebe uma xml.
    :return: retorna uma lista de string.
    """
    return list(map(lambda a: str(a), lst))


def transforma_lista_xml_em_list_dict(lst: list) -> list:
    """
    Esta função obtém uma lista em xml e retorna uma lista de dicionários.
    :param lst: (list): recebe uma xml.
    :return: retorna uma lista de dicionários.
    """
    return list(map(lambda a: ast.literal_eval(str(a)), lst))


def transforma_xml_em_dict(coluna_soap: list, usuario_soap: list) -> list[dict[str, str]]:
    """
    Esta função obtém uma lista xml e retorna uma lista de usuários em dicionário.
    :param coluna_soap: (list): recebe uma xml.
    :param usuario_soap: (list): recebe uma lista de usuário.
    :return: retorna uma lista de usuários em dicionário.
    """

    colunas_list = transforma_lista_xml_em_list_str(coluna_soap)
    usuarios_dict_list = []
    for usuario_xml in usuario_soap:
        usuario_str = transforma_lista_xml_em_list_str(usuario_xml['value'])
        usuario = dict(zip(colunas_list, usuario_str))
        usuarios_dict_list.append(usuario)

    return usuarios_dict_list


def request_rest_get_base(url: str, header=None) -> dict:
    """
    Esta função transforma um json em dicionário.
    :param url: (str): recebe um endpoint.
    :param header: (dict): recebe um xml em string.
    :return: retorna um dicionário de usuários.
    """
    logging.debug("-----Inicio do metodo get base-----")

    i = 0
    config = busca_valor_yaml()
    time_retry = config['config']['request']['retry_times']

    while i < time_retry:

        if i != 0:
            time.sleep(config['config']['request']['sleep'])

        try:
            i += 1
            response = requests.get(url=url, headers=header, timeout=config['config']['request']['timeout'])

            if response.status_code != 200:
                logging.warning(f"-----Mensagem com erro {i}/{time_retry} tentativas-----")
                continue

            logging.debug("-----Fim do metodo get base-----")
            return json.loads(response.text)

        except requests.exceptions.RequestException as e:
            logging.exception(e.errno)
            logging.info(f"-----Houve um erro na hora de requisitar {i}/{time_retry} tentativas-----")
            if i == time_retry:
                raise e


def request_rest_post_base(url: str, body: dict, header=None) -> list:
    """
    Esta função transformar um json em uma lista.
    :param url: (str): recebe um endpoint.
    :param body: (dict): recebe uma configuração em xml.
    :param header: (None): recebe um xml em string.
    :return: retorna uma lista de usuários.
    """
    logging.debug("-----Inicio do metodo post base-----")

    i = 0
    config = busca_valor_yaml()
    time_retry = config['config']['request']['retry_times']

    while i < time_retry:

        if i != 0:
            time.sleep(config['config']['request']['sleep'])

        try:
            i += 1
            response = requests.post(url=url, data=body, headers=header, timeout=config['config']['request']['timeout'])

            if response.status_code != 200:
                if response.status_code == 404:
                    logging.info(f"-----Nao foi encontrado grupos associados ao usuario {body} -----")
                    break
                logging.warning(f"-----Mensagem com erro {i}/{time_retry} tentativas-----")
                continue

            logging.debug("-----Fim do metodo post base-----")

            return [] if response.text == '' else json.loads(response.text)

        except requests.exceptions.RequestException as e:
            logging.exception(e.errno)
            logging.warning(f"-----Houve um erro na hora de requisitar {i}/{time_retry} tentativas-----")
            if i == time_retry:
                raise e

