import csv
import json
import logging
import os
import sys
from datetime import datetime

from config.config_yaml import busca_valor_yaml


def criar_arquivo_csv(list_rows: list[dict], filename: str) -> None:
    """
    Esta função cria um arquivo CSV.
    :param list_rows: (list): recebe uma lista de linhas do CSV.
    :param filename: (str): recebe o nome do arquivo CSV.
    """
    header = []
    for chave, value in list_rows[0].items():
        header.append(chave)

    with open(filename, mode='w', encoding='utf-8', newline='') as filecsv:
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


def retorna_nome_arquivo_consolidada() -> str:
    """
    Esta função apenas retorna o nome do arquivo consolidade.
    :return: retorna o nome do arquivo consolidade.
    """
    config = busca_valor_yaml()
    return f'{config["config"]["filenames"]["consolidate"]}.csv'


def monta_arquivo_consolidado(header: list, list_rows: list) -> None:
    """
    Esta função monta um arquivo consolidado.
    :param header: (list): colunas do arquivo.
    :param list_rows: (list): linhas do arquivo.
    """

    filename = retorna_nome_arquivo_consolidada()
    arquivo_listas = listar_diretorio_csv()
    if arquivo_listas.count(filename) == 0:
        criar_arquivo_csv(list_rows, f'csv/{filename}')
    else:
        continua_arquivo_csv(header, list_rows, f'csv/{filename}')


def retorna_nomes_arquivos_em_lista_ambiente() -> dict[str, list[str]]:
    """
    Esta função retorna nomes dos arquivos para seus respectivos ambientes.
    :return: retorna o nome dos arquivos para seus respectivos ambientes.
    """
    ambiente = {}
    rm_lista = []
    sca_lista = []
    fluig_lista = []
    protheus_lista = []
    top_lista = []
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
            case 'top':
                top_lista.append(nome_lista[1])
            case _:
                logging.warning(f"Ambiente desconhecido: {nome_lista[1]}.")

    ambiente['rm'] = rm_lista
    ambiente['sca'] = sca_lista
    ambiente['fluig'] = fluig_lista
    ambiente['protheus'] = protheus_lista
    ambiente['top'] = top_lista
    return ambiente


def listar_diretorio_csv():
    """
    Esta função lista a diretoria.
    """
    res = []
    for path in os.listdir('csv/'):
        if os.path.isfile(os.path.join('csv/', path)):
            res.append(path)
    return res


def deletar_todos_arquivos_csv():

    for pasta, subpasta, arquivos in os.walk('csv/'):

        for arquivo in arquivos:

            if arquivo.endswith('.csv'):
                path = os.path.join(pasta, arquivo)
                logging.info('deleted : ', path)
                os.remove(path)


def ler_arquivo_consolidada() -> list[dict]:
    """
    Esta função ler o arquivo consolidade.
    :return: retorna as linhas.
    """

    maxInt = sys.maxsize
    while True:
        try:
            filename = f'csv/{retorna_nome_arquivo_consolidada()}'
            with open(filename, newline='') as filecsv:
                csv.field_size_limit(maxInt)
                reader = csv.DictReader(f=filecsv, delimiter=';')
                linhas = []
                for row in reader:
                    linha = {
                        'sig_usuario': row['sig_usuario'],
                        'email': row['email'],
                        'sistema': row['sistema'],
                        'ambiente': row['ambiente'],
                        'perfil': json.loads(row['perfil'])
                    }
                    linhas.append(linha)
                return linhas
        except OverflowError:
            maxInt = int(maxInt / 10)


def cria_csv_gestores_colab_fora_corpweb(usuarios_fora_corp_web: list[dict]):

    gestores_consolidados = []

    for usuario in usuarios_fora_corp_web:

        for usuario_agrupado in usuario['usuario_agrupado']:

            for perfil in usuario_agrupado['perfil']:

                sistema = usuario_agrupado['sistema']

                gestor_cosolidado = {'ambiente': usuario_agrupado['ambiente'],
                                     'gestor_login': 'N/A',
                                     'gestor_email': 'N/A',
                                     'gestor_nome': 'N/A',
                                     'area_colaborador': 'N/A',
                                     'cccodigo': 'N/A',
                                     'ccdescricao': 'N/A',
                                     'colab_login': usuario['sig_usuario'],
                                     'colab_email': usuario['email'],
                                     'colab_nome': 'N/A',
                                     'sistema': sistema,
                                     'sistema_fluig': 'S' if sistema.upper() == 'FLUIG' else 'N',
                                     'grupo_codigo': perfil['cod'],
                                     'grupo_nome': perfil['nom'],
                                     'grupo_tipo': perfil['tipo']}

                gestores_consolidados.append(gestor_cosolidado)

    date_files = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    criar_arquivo_csv(gestores_consolidados, f'csv/FORA_CORP_WEB_{date_files}.csv')


def cria_csv_gestores_corp_web_dados_invalidos(usuarios_corp_web_dados_invalidos: list[dict]):

    gestores_invalidos = []

    for gestor in usuarios_corp_web_dados_invalidos:

        if not gestor['colaboradores']:

            gestor_invalido = {'ambiente': 'N/A',
                               'gestor_login': gestor['login_gestor'],
                               'gestor_email': gestor['email_gestor'],
                               'gestor_nome': gestor['nom_gestor'],
                               'area_colaborador': 'N/A',
                               'cccodigo': 'N/A',
                               'ccdescricao': 'N/A',
                               'colab_login': 'N/A',
                               'colab_email': 'N/A',
                               'colab_nome': 'N/A',
                               'sistema': 'N/A',
                               'sistema_fluig': 'N/A',
                               'grupo_codigo': 'N/A',
                               'grupo_nome': 'N/A',
                               'grupo_tipo': 'N/A'}

            gestores_invalidos.append(gestor_invalido)
        else:

            for colaborador in gestor['colaboradores']:

                for usuario_agrupado in colaborador['usuario_agrupado']:

                    for perfil in usuario_agrupado['perfil']:

                        sistema = usuario_agrupado['sistema']

                        gestor_invalido = {'ambiente': usuario_agrupado['ambiente'],
                                           'gestor_login': gestor['login_gestor'],
                                           'gestor_email': gestor['email_gestor'],
                                           'gestor_nome': gestor['nom_gestor'],
                                           'area_colaborador': colaborador['usuario_dado_corp_web']['area_colaborador'],
                                           'cccodigo': colaborador['usuario_dado_corp_web']['cc_colaborador'],
                                           'ccdescricao': colaborador['usuario_dado_corp_web']['dsc_cc_colaborador'],
                                           'colab_login': colaborador['sig_usuario'],
                                           'colab_email': colaborador['email'],
                                           'colab_nome': colaborador['usuario_dado_corp_web']['nom_usuario'],
                                           'sistema': sistema,
                                           'sistema_fluig': 'S' if sistema.upper() == 'FLUIG' else 'N',
                                           'grupo_codigo': perfil['cod'],
                                           'grupo_nome': perfil['nom'],
                                           'grupo_tipo': perfil['tipo']}

                        gestores_invalidos.append(gestor_invalido)

    date_files = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    criar_arquivo_csv(gestores_invalidos, f'csv/GESTORES_CORP_WEB_DADOS_INVALIDOS_{date_files}.csv')


def cria_csv_gestores_invalidos_fluig(usuarios_invalidos_fluig: list[dict]):

    gestores_invalidos = []

    for gestor in usuarios_invalidos_fluig:

        for colaborador in gestor['colaboradores']:

            for usuario_agrupado in colaborador['usuario_agrupado']:

                for perfil in usuario_agrupado['perfil']:

                    sistema = usuario_agrupado['sistema']

                    gestor_invalido = {'ambiente': usuario_agrupado['ambiente'],
                                       'gestor_login': gestor['login_gestor'],
                                       'gestor_email': gestor['email_gestor'],
                                       'gestor_nome': gestor['nom_gestor'],
                                       'area_colaborador': colaborador['usuario_dado_corp_web']['area_colaborador'],
                                       'cccodigo': colaborador['usuario_dado_corp_web']['cc_colaborador'],
                                       'ccdescricao': colaborador['usuario_dado_corp_web']['dsc_cc_colaborador'],
                                       'colab_login': colaborador['sig_usuario'],
                                       'colab_email': colaborador['email'],
                                       'colab_nome': colaborador['usuario_dado_corp_web']['nom_usuario'],
                                       'sistema': sistema,
                                       'sistema_fluig': 'S' if sistema.upper() == 'FLUIG' else 'N',
                                       'grupo_codigo': perfil['cod'],
                                       'grupo_nome': perfil['nom'],
                                       'grupo_tipo': perfil['tipo']}

                    gestores_invalidos.append(gestor_invalido)

    date_files = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    criar_arquivo_csv(gestores_invalidos, f'csv/gestores_invalidos_fluig_{date_files}.csv')

