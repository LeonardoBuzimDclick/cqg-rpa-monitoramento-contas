import datetime
import json
import logging
import threading
from datetime import datetime
from itertools import chain

from config.request_config import request_rest_get_base, request_rest_post_base
from utils.create_file_csv import ler_arquivo_consolidada, monta_arquivo_consolidado, criar_arquivo_csv
from utils.listas_utils import separa_listas, agrupa_lista_por_email_sig_usuario


def get_usuarios_ativos_sca(url: str, token: str) -> list[dict]:
    """
    Esta função obtém os dados dos usuários ativos no SCA.
    :param url: (str): recebe um endpoint de usuários ativos.
    :param token: (str): recebe token de segurança.
    :return: retorna uma lista de usuários ativos.
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
    :param url: (str): recebe um endpoint de grupos.
    :param user_input_list: (list): recebe uma lista de usuários ativos.
    :return: retorna uma lista de usurious ativo no SCA e seus grupos associados.
    """
    logging.debug("-----Inicio do metodo get grupos associados SCA-----")

    for user_input in user_input_list:
        sig_usuario = user_input['sigUsuario']
        acessos = request_rest_post_base(url=url, body={'user': sig_usuario})

        logging.debug(f'usuario: {sig_usuario} - perfil: {acessos}')
        user_input['grupos'] = acessos
        user_input['nomUsuario'] = str(user_input['nomUsuario']).strip()

    logging.debug("-----Fim do metodo get grupos associados SCA-----")

    return user_input_list


def get_usuarios_ativos_grupos_associados_sca(url_sca: str, token_usuario: str, url_grupo_sca: str,
                                              divisao_listas: int) -> None:
    """
    Esta função obtém os dados dos usuários ativos e seus grupos associados.
    :param url_sca: (str): recebe um endpoint de usuários ativos.
    :param token_usuario: (str): recebe token de segurança.
    :param url_grupo_sca: (str): recebe o endpoint de grupos associados para cada usuário ativo no SCA.
    :param divisao_listas: (int): número de listas que será divido para consultar em multithread.
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

    usuarios_consolidados = []
    headers_consolidados = []
    for usuario in usuarios:

        if not usuario['grupos']:
            logging.info(f'usuario: { usuario["sigUsuario"]} nao tem perfil')
            continue

        perfils_consolidados = []
        for perfil in usuario['grupos']:
            perfil_consolidado = {'nom': perfil, 'cod': perfil, 'tipo': 'Comum'}
            perfils_consolidados.append(perfil_consolidado)

        usuario_consolidado = {'sig_usuario': usuario['sigUsuario'].upper() if usuario['sigUsuario'] else '',
                               'email': usuario['email'].upper() if usuario['email'] else '',
                               'sistema': 'SCA',
                               'ambiente': 'SCA',
                               'perfil': json.dumps(perfils_consolidados)}
        if not headers_consolidados:
            for chave, value in usuario_consolidado.items():
                headers_consolidados.append(chave)
        usuarios_consolidados.append(usuario_consolidado)

    date_file = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    monta_arquivo_consolidado(headers_consolidados, usuarios_consolidados)
    criar_arquivo_csv(usuarios, f'csv/usuarios_sca_{date_file}.csv')
    logging.info("-----Termino da busca dos usuarios ativos no SCA e seus grupos associados-----")


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

    usuarios_consolidados = []
    headers_consolidados = []
    for usuario in resultado:

        if usuario['STATUS_USUARIO'] != 'ATIVO':
            logging.info(f'o usuario {usuario["LOGIN_USUARIO"]} não é ativo')
            continue

        if len(usuario['GRUPOS']) == 1 and \
                usuario['GRUPOS'][0]["NOME_GRUPO"] == '' and \
                usuario['GRUPOS'][0]["CODIGO_GRUPO"] == '':

            logging.info(f'o usuario {usuario["LOGIN_USUARIO"]} não tem perfil')
            continue

        perfils_consolidados = []
        for perfil in usuario['GRUPOS']:
            perfil_consolidado = {'nom': f'{perfil["NOME_GRUPO"]}', 'cod': f'{perfil["CODIGO_GRUPO"]}',
                                  'tipo': 'ADMINISTRADOR' if perfil["CODIGO_GRUPO"] == '000000' else 'COMUM'}
            perfils_consolidados.append(perfil_consolidado)

        usuario_consolidado = {'sig_usuario': usuario['LOGIN_USUARIO'].upper() if usuario['LOGIN_USUARIO'] else '',
                               'email': usuario['EMAIL_USUARIO'].upper() if usuario['EMAIL_USUARIO'] else '',
                               'sistema': 'PROTHEUS',
                               'ambiente': tenant,
                               'perfil': json.dumps(perfils_consolidados)
                               }
        if not headers_consolidados:
            for chave, value in usuario_consolidado.items():
                headers_consolidados.append(chave)
        usuarios_consolidados.append(usuario_consolidado)

    date_files = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    logging.debug(f"-----Inicio da escrita dos usuarios ativos do Protheus do ambiente {tenant} no CSV -----")
    monta_arquivo_consolidado(headers_consolidados, usuarios_consolidados)
    criar_arquivo_csv(response['mensagem'], f'csv/usuarios_protheus_{tenant}_{date_files}.csv')

    logging.debug(f"-----Termino da escrita dos usuarios ativos do Protheus do ambiente {tenant} no CSV-----")


def buscar_usuarios_grupos_associados_top(url: str):
    """
    Esta função obtém os dados dos usuários e seus grupos associados no top.
    :param url: (str): recebe o endpoint de usuários ativos.
    """
    response = request_rest_get_base(url=url)

    response_list = list(response)

    usuarios_consolidados = []

    for usuario in response:
        perfils_consolidados = [
            {'nom': usuario['codPerfil'],
             'cod': usuario['nomePerfil'] if usuario['nomePerfil'] else usuario['codPerfil'],
             'tipo': usuario['codSistema']
             }
        ]

        usuario_consolidado = {'sig_usuario': usuario['codUsuario'].upper() if usuario['codUsuario'] else '',
                               'email': usuario['email'].upper() if usuario['email'] else '',
                               'sistema': 'TOP',
                               'ambiente': 'TOP',
                               'perfil': json.dumps(perfils_consolidados)
                               }

        usuarios_consolidados.append(usuario_consolidado)

    headers_consolidados = list(usuarios_consolidados[0])

    date_file = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    monta_arquivo_consolidado(headers_consolidados, usuarios_consolidados)
    criar_arquivo_csv(response_list, f'csv/usuarios_top_{date_file}.csv')
    logging.info("-----Termino da busca dos usuarios ativos no TOP e seus grupos associados-----")


def obter_gestores_seus_colaboradores_associados(url: str, tenant: str) -> list:
    """
    Esta função obtém os dados dos gestores e seus colaboradores associados.
    :param url: (str): recebe o endpoint dp corp-web.
    :param tenant: (str): recebe o ambiente.
    :return: retorna os gestores com seus colaboradores associados.
    """
    logging.info(f'-----inicio request corp-web-{tenant}-----')
    response = request_rest_get_base(url)
    logging.info(f'-----término request corp-web-{tenant}-----')

    gestores_lista = []
    gestores_com_colaboradores = []
    usuarios_lista = [response] if type(response) == dict else response if type(response) == list else []
    for usuario in usuarios_lista:
        if 'colaboradores' in usuario:
            gestores_lista.append(usuario)
        elif 'filhos' in usuario:
            for u in usuario['filhos']:
                usuarios_lista.append(u)
        else:
            logging.warning(f'usuario quebrado: {usuario}')

    for gestor in gestores_lista:
        colaboradores_lista = []
        for colaborador in gestor['colaboradores']:
            colaborador_final = {
                'sig_usuario': '' if not colaborador['sig_usuario'] else colaborador['sig_usuario'].upper(),
                'email': '' if not colaborador['email'] else colaborador['email'].upper(),
                'nom_usuario': '' if not colaborador['nome'] else colaborador['nome'].upper(),
                'area_colaborador': '' if not colaborador['dsc_centro_custo'] else colaborador['dsc_centro_custo'],
                'cc_colaborador': '' if not colaborador['cod_centro_custo'] else colaborador['cod_centro_custo'],
                'dsc_cc_colaborador': '' if not colaborador['dsc_centro_custo'] else colaborador['dsc_centro_custo']
            }
            colaboradores_lista.append(colaborador_final)

        gestor_final = {
            'amb_gestor': tenant,
            'nom_usuario': '' if not gestor['NOM_COLABORADOR'] else gestor['NOM_COLABORADOR'].lower(),
            'sig_usuario': '' if not gestor['SIG_USUARIO'] else gestor['SIG_USUARIO'],
            'email': '' if not gestor['TXT_EMAIL'] else gestor['TXT_EMAIL'],
            'sig_estr_organizacional': gestor['SIG_ESTR_ORGANIZACIONAL'],
            'colaboradores': colaboradores_lista
        }
        gestores_com_colaboradores.append(gestor_final)

    return gestores_com_colaboradores


def checa_colaboradores_em_corpweb(ambiente_gestores: list) -> tuple[list[dict], list[dict]]:
    """
    Esta função checa cada colaborador em corpweb.
    :param ambiente_gestores: (list): recebe uma lista de gestores com o seu ambiente como chave.
    :return: retorna os usuários.
    """
    usuarios = ler_arquivo_consolidada()
    usuarios_agrupados = agrupa_lista_por_email_sig_usuario(usuarios)
    usuarios_corpweb_consolidado = []
    for gestores_dict in ambiente_gestores:
        for ambiente, gestores in gestores_dict.items():
            for gestor in gestores:
                colaboradores_final = []
                if len(gestor['colaboradores']) == 0:
                    continue
                for colaborador in gestor['colaboradores']:
                    for usuario in usuarios_agrupados:
                        if colaborador['sig_usuario'] != '' and colaborador['sig_usuario'] == usuario['sig_usuario'] or \
                                colaborador['email'] != '' and colaborador['email'] == usuario['email']:
                            usuarios_agrupados.remove(usuario)
                            usuario['usuario_dado_corp_web'] = colaborador
                            colaboradores_final.append(usuario)

                gestor_final = {
                    'amb_gestor': ambiente,
                    'nom_gestor': gestor['nom_usuario'],
                    'login_gestor': gestor['sig_usuario'],
                    'email_gestor': gestor['email'],
                    'company_id': 20 if ambiente == 'AMBIENTAL' else 1,
                    'colaboradores': colaboradores_final,

                }
                usuarios_corpweb_consolidado.append(gestor_final)

    return usuarios_corpweb_consolidado, usuarios_agrupados


def busca_gestores_colaboradores_corp_web_checa_arquivo_consolidado(parametros: dict, url: str) -> \
        tuple[list[dict], list[dict]]:
    """
    Esta função busca os gestores e seus colaboradores associado no corp web é checa o arquivo consolidado.
    """
    gestores_colaborares_por_ambiente_list = []
    for ambiente, codigo in parametros.items():
        url_parametrizada = f'{url}{codigo}'

        gestores_colaborares_por_ambiente = {
            ambiente: obter_gestores_seus_colaboradores_associados(url_parametrizada, ambiente)
        }

        gestores_colaborares_por_ambiente_list.append(gestores_colaborares_por_ambiente)

    return checa_colaboradores_em_corpweb(gestores_colaborares_por_ambiente_list)


def checa_corpweb_e_envia_fluig_gestores_localizados(gestores_colaborares_por_ambiente_list: list):
    usuarios_dentro_corpweb, usuarios_fora_corpweb = \
        checa_colaboradores_em_corpweb(gestores_colaborares_por_ambiente_list)

    date_files = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    criar_arquivo_csv(usuarios_fora_corpweb, f'csv/CONSOLIDADA_POS_CORP_WEB_{date_files}.csv')