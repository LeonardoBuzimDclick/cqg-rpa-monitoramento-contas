import datetime
import logging
import threading
from itertools import chain

from config.request_config import request_rest_get_base, request_rest_post_base
from create_files import create_file_csv


def get_usuarios_ativos_sca(url: str, token: str) -> list[dict]:
    """
    Esta função obtém os dados dos usuários ativos no SCA.
    :param url: (str): recebe o endpoint de usuários ativos no SCA.
    :param token: (str): recebe token de segurança.
    :return: retorna os usuários ativos no SCA.
    """
    logging.debug("-----Inicio do metodo get usuarios ativos SCA-----")

    header = {'Accept': 'application/json',
              'Authorization': 'Bearer ' + token}
    response = request_rest_get_base(url, header)

    logging.debug("-----Fim do metodo get usuarios ativos SCA-----")
    return response['usuarios']['usuario']


def get_grupos_associados_sca(url: str, user_input_list: list[dict]) -> list[dict]:
    """
    Esta função obtém os grupos associados para cada usuário ativo no SCA.
    :param url: (str): recebe o endpoint de grupos associados para cada usuário ativo no SCA.
    :param user_input_list: (list): recebe lista de usuários ativos.
    :return: retorna uma lista de usuários ativo no SCA e seus grupos associados.
    """
    logging.debug("-----Inicio do metodo get grupos associados SCA-----")

    for user_input in user_input_list:
        acessos = request_rest_post_base(url=url, body={'user': user_input['sigUsuario']})
        user_input["nomUsuario"] = str(user_input["nomUsuario"]).strip()
        user_input["grupos"] = acessos

    logging.debug("-----Inicio do metodo get grupos associados SCA-----")

    return user_input_list


def get_usuarios_ativos_grupos_associados_sca(url_sca: str, token_usuario: str, url_grupo_sca: str,
                                              divisao_listas: int) -> None:
    """
    Esta função obtém os dados dos usuários ativos e seus grupos associados.
    :param divisao_listas: (int): número de listas que será divido para consultar em multithread
    :param url_sca: (str): recebe o endpoint de usuários ativos no SCA.
    :param token_usuario: (str): recebe token de segurança.
    :param url_grupo_sca: (str): recebe o endpoint de grupos associados para cada usuário ativo no SCA.
    """
    logging.info("-----Buscando usuarios ativos no SCA e seus grupos associados-----")

    usuarios = get_usuarios_ativos_sca(url_sca, token_usuario)

    logging.debug(f"----Foram encontrados {len(usuarios)} usuarios ativos no SCA-----")
    usuarios_separados = separa_listas(usuarios, divisao_listas)
    logging.debug(
        f"----Os usuarios foram separados em {divisao_listas} listas e contem {len(list(chain(usuarios_separados)))} listas-----")

    threads = []
    for index, usuario in enumerate(usuarios_separados):
        t = threading.Thread(target=get_grupos_associados_sca, args=[url_grupo_sca, usuario], daemon=True)
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    header = []
    if not header:
        for chave, value in usuarios[0].items():
            header.append(chave)

    usuarios_consolidados = []
    headers_consolidados = []
    for usuario in usuarios:
        usuario_consolidado = {'sig_usuario': usuario['sigUsuario'] if usuario['sigUsuario'] else '',
                               'email': usuario['email'] if usuario['email'] else '',
                               'sistema': 'SCA',
                               'ambiente': 'SCA',
                               'perfil': usuario['grupos'] if usuario['grupos'] else []}
        if not headers_consolidados:
            for chave, value in usuario_consolidado.items():
                headers_consolidados.append(chave)
        usuarios_consolidados.append(usuario_consolidado)

    date_file = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    create_file_csv.monta_arquivo_consolidado(headers_consolidados, usuarios_consolidados)
    create_file_csv.criar_arquivo_csv(header, usuarios,
                                      f'csv/usuarios_sca_{date_file}.csv')
    logging.info("-----Termino da busca dos usuarios ativos no SCA e seus grupos associados-----")


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


def request_protheus(url: str, header_tenant_id: str, tenant: str) -> None:
    """
    Esta função busca os usuarios ativos no Protheus no ambiente.
    :param url: (str): recebe um endpoint do Protheus.
    :param header_tenant_id: (str): recebe o TenantId.
    :param tenant: (str): recebe o ambiente.
    """
    logging.info(f"-----Inicio da busca dos usuarios ativos no Protheus no ambiente {tenant}-----")
    header = {'TenantId': header_tenant_id}
    response = request_rest_get_base(url, header)
    if not response:
        logging.info(
            f"-----Nao foram encontrados dados no ambiente {tenant} com a url {url} e tenand_id {header_tenant_id}-----")
        return

    resultado = response['mensagem']
    logging.info(
        f"-----Termino da busca dos usuarios ativos no Protheus no ambiente {tenant} com {len(resultado)} dados-----")

    header_file = []
    usuario = resultado[0]
    for chave, value in usuario.items():
        header_file.append(chave)

    usuarios_consolidados = []
    headers_consolidados = []
    for usuario in resultado:
        usuario_consolidado = {'sig_usuario': usuario['LOGIN_USUARIO'] if usuario['LOGIN_USUARIO'] else '',
                               'email': usuario['EMAIL_USUARIO'] if usuario['EMAIL_USUARIO'] else '',
                               'sistema': 'PROTHEUS',
                               'ambiente': tenant,
                               'perfil': usuario['GRUPOS'] if usuario['GRUPOS'] else []}
        if not headers_consolidados:
            for chave, value in usuario_consolidado.items():
                headers_consolidados.append(chave)
        usuarios_consolidados.append(usuario_consolidado)

    date_files = datetime.datetime.now().strftime("%Y%m%dT%H%M%SZ")
    logging.debug(f"-----Inicio da escrita dos usuarios ativos do Protheus do ambiente {tenant} no CSV -----")
    create_file_csv.monta_arquivo_consolidado(headers_consolidados, usuarios_consolidados)
    create_file_csv.criar_arquivo_csv(header_file, response['mensagem'],
                                      f'csv/usuarios_protheus_{tenant}_{date_files}.csv')

    logging.debug(f"-----Termino da escrita dos usuarios ativos do Protheus do ambiente {tenant} no CSV-----")
