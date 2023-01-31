import csv
import logging
import os

from config.config_yaml import busca_valor_yaml


def criar_arquivo_csv(header: list, list_rows: list, filename: str) -> None:
    """
    Esta função cria um arquivo CSV.
    :param header: (list): recebe uma lista de cabeçalho do CSV.
    :param list_rows: (list): recebe uma lista de linhas do CSV.
    :param filename: (str): recebe o nome do arquivo CSV.
    """

    with open(filename, mode='w', newline='') as filecsv:
        writer = csv.DictWriter(f=filecsv, fieldnames=header, delimiter=';')
        writer.writeheader()
        writer.writerows(list_rows)


def continua_arquivo_csv(header: list, list_rows: list, filename: str) -> None:
    """
    Esta função continua a escrição de um arquivo CSV.
    :param header: (list): recebe uma lista de cabeçalho do CSV.
    :param list_rows: (list): recebe uma lista de linhas do CSV.
    :param filename: (str): recebe o nome do arquivo CSV.
    """

    with open(filename, mode='a', newline='') as filecsv:
        writer = csv.DictWriter(f=filecsv, fieldnames=header, delimiter=';')
        for row in list_rows:
            writer.writerow(row)


def monta_arquivo_consolidado(header: list, list_rows: list):

    config = busca_valor_yaml()
    filename = f'{config["config"]["filenames"]["consolidate"]}.csv'
    arquivo_listas = listar_diretorio_csv()
    if arquivo_listas.count(filename) == 0:
        criar_arquivo_csv(header, list_rows, f'csv/{filename}')
    else:
        continua_arquivo_csv(header, list_rows, f'csv/{filename}')


def retorna_nomes_arquivos_em_lista_ambiente() -> dict[str, list[str]]:
    ambiente = {}
    rm_lista = []
    sca_lista = []
    fluig_lista = []
    protheus_lista = []
    consolidada_arquivo = f'{busca_valor_yaml()["config"]["filenames"]["consolidate"]}.csv'
    diretorio_lista = listar_diretorio_csv()
    for diretorio in diretorio_lista:
        if 'README.MD' == diretorio or consolidada_arquivo == diretorio:
            continue
        nome_lista = diretorio.split('_')
        match nome_lista[1]:
            case 'rm':
                rm_lista.append(nome_lista[2])
            case 'sca':
                sca_lista.append(nome_lista[1])
            case 'fluig':
                fluig_lista.append(nome_lista[2])
            case 'protheus':
                protheus_lista.append(nome_lista[2])
            case _:
                logging.warning(f"Ambiente desconhecido: {nome_lista[1]}.")

    ambiente['rm'] = rm_lista
    ambiente['sca'] = sca_lista
    ambiente['fluig'] = fluig_lista
    ambiente['protheus'] = protheus_lista
    return ambiente


def listar_diretorio_csv():
    res = []
    for path in os.listdir('csv/'):
        if os.path.isfile(os.path.join('csv/', path)):
            res.append(path)
    return res

