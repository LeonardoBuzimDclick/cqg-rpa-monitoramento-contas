import base64
import logging
import re
from datetime import datetime

from config.request_config import request_post_soap_base
from utils.create_file_csv import monta_arquivo_consolidado, criar_arquivo_csv
from utils.listas_utils import agrupa_listas_rm


def request_usuario_fluig(url: str, body: dict) -> list[dict[str, any]]:
    """
    Esta função obtém os dados dos usuários ativos no FLUIG.
    :param url: (str): recebe um endpoint dos usuários ativos.
    :param body: (dict): recebe um xml em string.
    :return: retorna uma lista de usuários ativos no FLUIG.
    """
    return request_post_soap_base(url=url, body=body)


def request_grupo_associado_fluig(url: str, body: dict) -> list[dict[str, any]]:
    """
    Esta função obtém os grupos associados para cada usuário ativo no FLUIG.
    :param url: (str): recebe o endpoint de grupos associados para cada usuário ativo.
    :param body: (dict): recebe um xml em string.
    :return: retorna uma lista de usuários ativo no FLUIG e seus grupos associados.
    """
    return request_post_soap_base(url=url, body=body)


def busca_usuarios_ativos_e_grupos_associados_fluig(url_fluig: str, body_fluig: dict,
                                                    url_grupo_fluig: str, body_grupo_fluig: dict, tenant: str) -> None:
    """
    Esta função obtém os dados dos usuários ativos e seus grupos associados no FLUIG.
    :param url_fluig: (str): recebe o endpoint de usuários ativos.
    :param body_fluig: (dict): recebe um xml em string.
    :param url_grupo_fluig: (str):  recebe o endpoint de grupos associados para cada usuário ativo no SCA.
    :param body_grupo_fluig: (dict): recebe um xml em string.
    :param tenant: (str): recebe um Tenant.
    """
    logging.info(
        f"-----Buscando usuarios ativos no fluig da busca dos usuarios ativos no fluig no ambiente {tenant}-----")

    usuarios_list = request_usuario_fluig(url_fluig, body_fluig)
    grupos_list = request_grupo_associado_fluig(url_grupo_fluig, body_grupo_fluig)

    usuarios_consolidados = []
    headers_consolidados = []
    for usuario in usuarios_list:
        usuario_consolidado = {}
        id = usuario['colleaguePK.colleagueId']
        grupos_associados = []
        for grupo in grupos_list:
            if id == grupo['colleagueGroupPK.colleagueId']:
                grupos_associados.append(grupo['colleagueGroupPK.groupId'])

        usuario_consolidado['sig_usuario'] = re.search(r'([\w\\.]*)^([\w\\.]*)', usuario['mail'].upper()).group() \
            if usuario['mail'] else ''
        usuario_consolidado['email'] = usuario['mail'].upper() if usuario['mail'] else ''
        usuario_consolidado['sistema'] = 'FLUIG'
        usuario_consolidado['ambiente'] = tenant
        usuario_consolidado['perfil'] = ','.join(grupos_associados)
        usuario['grupos_associados'] = grupos_associados
        usuarios_consolidados.append(usuario_consolidado)

        if not headers_consolidados:
            for chave, value in usuario_consolidado.items():
                headers_consolidados.append(chave)

    logging.info(
        f"-----Termino da busca dos usuarios ativos no fluig no ambiente {tenant} com {len(usuarios_list)} dados-----")
    logging.debug(f"-----Inicio da escrita dos usuarios ativos do fluig do ambiente {tenant} no CSV -----")
    monta_arquivo_consolidado(headers_consolidados, usuarios_consolidados)
    criar_arquivo_csv(usuarios_list, f'csv/usuarios_fluig_{tenant}_{datetime.now().strftime("%Y%m%dT%H%M%SZ")}.csv')
    logging.debug(f"-----Termino da escrita dos usuarios ativos do fluig do ambiente {tenant} no CSV -----")


def busca_usuarios_ativos_rm(url_rm: str, body_rm: dict, soap_action: str, token_authorization: str, tenant: str):
    """
    Esta função busca usuários ativos no RM.
    :param url_rm: (str): recebe um endpoint de usuários ativos.
    :param body_rm: (dict): recebe um xml em string.
    :param soap_action: (str): recebe um valor string.
    :param token_authorization: (str): recebe token de autorização.
    :param tenant: (str): recebe um Tenant.
    """

    base64_bytes = base64.b64encode(token_authorization.encode('ascii'))
    base64_message = base64_bytes.decode('ascii')

    headers = {
        "Content-Type": "text/xml;charset=UTF-8",
        "SOAPAction": soap_action,
        "Authorization": "Basic " + base64_message
    }

    logging.info(f"-----Inicio da busca dos usuarios ativos no rm no ambiente {tenant}-----")
    response = request_post_soap_base(url=url_rm, body=body_rm, headers=headers, is_rm=True)

    usuarios_consolidados_disperso = []
    headers_consolidados = []
    for usuario in response:
        if 'EMAIL' not in usuario or 'SISTEMA' not in usuario:
            logging.warning(
                f'Não foram encontradas os cabeçalhos EMAIL ou SISTEMA no retorno - RM - {tenant} - {usuario["CODUSUARIO"]}')
            continue
        usuario_consolidado = {'sig_usuario': usuario['CODUSUARIO'].upper() if usuario['CODUSUARIO'] else '',
                               'email': usuario['EMAIL'].upper() if usuario['EMAIL'] else '',
                               'sistema': 'RM',
                               'ambiente': tenant,
                               'perfil': usuario['SISTEMA'] if usuario['SISTEMA'] else ''}
        usuarios_consolidados_disperso.append(usuario_consolidado)
        if not headers_consolidados:
            for chave, value in usuario_consolidado.items():
                headers_consolidados.append(chave)

    usuarios_consolidados_agrupados = agrupa_listas_rm(usuarios_consolidados_disperso)
    usuarios_consolidados = []
    for usuario_list in usuarios_consolidados_agrupados:
        perfil = []
        for usuario in usuario_list:
            perfil.append(usuario['perfil'])

        usuario_consolidado = {'sig_usuario': usuario_list[0]['sig_usuario'].upper(),
                               'email': usuario_list[0]['email'].upper(),
                               'sistema': 'RM',
                               'ambiente': tenant,
                               'perfil': perfil}

        usuarios_consolidados.append(usuario_consolidado)

    logging.info(
        f"-----Termino da busca dos usuarios ativos no rm no ambiente {tenant} com {len(usuarios_consolidados)} dados-----")
    logging.debug(f"-----Inicio da escrita dos usuarios ativos do rm do ambiente {tenant} no CSV -----")
    date_files = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    monta_arquivo_consolidado(headers_consolidados, usuarios_consolidados)
    criar_arquivo_csv(response, f'csv/usuario_rm_{tenant}_{date_files}.csv')
    logging.debug(f"-----Termino da escrita dos usuarios ativos do rm do ambiente {tenant} no CSV-----")
