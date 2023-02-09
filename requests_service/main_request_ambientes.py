import logging
from datetime import datetime

from utils.create_file_csv import retorna_nomes_arquivos_em_lista_ambiente
from requests_service.rest.rest_request import get_usuarios_ativos_grupos_associados_sca, request_protheus, \
    buscar_usuarios_grupos_associados_top
from requests_service.soap.body_xml import consulta_usuarios_ativos_fluig, consulta_usuarios_grupos_fluig, \
    obter_dados_usuarios_ativos_rm_seus_grupos
from requests_service.soap.soap_request import busca_usuarios_ativos_e_grupos_associados_fluig, busca_usuarios_ativos_rm


def busca_usuarios_ativos_nos_ambientes(config: dict) -> bool:
    """
    Esta função busca os usuários ativos nos ambientes.
    :param config: (dict): recebe as configurações do sistema.
    :return: retorna o numero onde parou a tarefa.
    """
    logging.info(f'-----Inicio da fase 1 [coleta]-----')
    arquivos_criados = retorna_nomes_arquivos_em_lista_ambiente()
    sca_ok = False
    try:
        data_ini = datetime.now()
        if not arquivos_criados['sca']:
            get_usuarios_ativos_grupos_associados_sca(
                url_sca=config['request']['rest']['sca']['usuarios']['url'],
                token_usuario=config['request']['rest']['sca']['usuarios']['token_authorizaton'],
                url_grupo_sca=config['request']['rest']['sca']['grupos_associados'],
                divisao_listas=config['config']['qtd_lista_multithread'])
            sca_ok = True
        else:
            logging.info('Como há arquivos SCA no diretório, o robô não enviou requisição para o SCA')
        data_fim = datetime.now()
        time_diff = data_fim - data_ini
        logging.debug(f'O tempo total de execução de busca no SCA foi: {time_diff}')
        sca_ok = True

    except Exception as e:
        sca_ok = False
        logging.warning(e)

    protheus_ok = False
    try:
        data_ini = datetime.now()
        ambientes = config['request']['rest']['protheus']
        for ambiente in ambientes:
            for key, config_request in ambiente.items():
                executar = True
                for arquivo_protheus in arquivos_criados['protheus']:
                    if key == arquivo_protheus:
                        executar = False
                        break

                if executar:
                    request_protheus(url=config_request['url'],
                                     header_tenant_id=config_request['header'],
                                     tenant=key)
                else:
                    logging.info(
                        f'Como há arquivos protheus-{key} no diretório, o robô não enviou requisição para o protheus-{key}')
        data_fim = datetime.now()
        time_diff = data_fim - data_ini
        logging.debug(f'O tempo total de execução de busca no protheus foi: {time_diff}')
        protheus_ok = True

    except Exception as e:
        protheus_ok = False
        logging.warning(e)

    fluig_ok = False
    try:
        data_ini = datetime.now()
        ambientes = config['request']['soap']['fluig']['urls']
        for ambiente in ambientes:
            for key, config_request in ambiente.items():
                executar = True
                for arquivo_protheus in arquivos_criados['fluig']:
                    if key == arquivo_protheus:
                        executar = False
                        break

                if executar:
                    busca_usuarios_ativos_e_grupos_associados_fluig(url_fluig=config_request['usuarios'],
                                                                    body_fluig=consulta_usuarios_ativos_fluig(),
                                                                    url_grupo_fluig=config_request['grupos_associados'],
                                                                    body_grupo_fluig=consulta_usuarios_grupos_fluig(),
                                                                    tenant=key)
                else:
                    logging.info(
                        f'Como há arquivos fluig-{key} no diretório, o robô não enviou requisição para o fluig-{key}')
        data_fim = datetime.now()
        time_diff = data_fim - data_ini
        logging.debug(f'O tempo total de execução de busca no fluig foi: {time_diff}')
        fluig_ok = True
    except Exception as e:
        fluig_ok = False
        logging.warning(e)

    rm_ok = False
    try:
        data_ini = datetime.now()
        ambientes = config['request']['soap']['rm']['urls']
        headers = config['request']['soap']['rm']['header']
        for ambiente in ambientes:
            for key, config_request in ambiente.items():
                executar = True
                for arquivo_protheus in arquivos_criados['rm']:
                    if key == arquivo_protheus:
                        executar = False
                        break

                if executar:
                    busca_usuarios_ativos_rm(url_rm=config_request['usuarios'],
                                             body_rm=obter_dados_usuarios_ativos_rm_seus_grupos(),
                                             soap_action=headers['soap_action'],
                                             token_authorization="{}:{}".format(
                                                 headers['token_authorization']['username'],
                                                 headers['token_authorization']['password']),
                                             tenant=key)
                else:
                    logging.info(
                        f'Como há arquivos rm-{key} no diretório, o robô não enviou requisição para o rm-{key}')
        data_fim = datetime.now()
        time_diff = data_fim - data_ini
        logging.debug(f'O tempo total de execução de busca no rm foi: {time_diff}')
        rm_ok = True
    except Exception as e:
        rm_ok = False
        logging.warning(e)

    top_ok = False
    try:
        data_ini = datetime.now()
        if not arquivos_criados['top']:
            buscar_usuarios_grupos_associados_top(url=config['request']['rest']['top']['url'])
            top_ok = True
        else:
            logging.info('Como há arquivos TOP no diretório, o robô não enviou requisição para o TOP')
        data_fim = datetime.now()
        time_diff = data_fim - data_ini
        logging.debug(f'O tempo total de execução de busca no TOP foi: {time_diff}')
        top_ok = True

    except Exception as e:
        top_ok = False
        logging.warning(e)

    logging.info('-----Termino da fase 1 [coleta]-----')
    return sca_ok and protheus_ok and fluig_ok and rm_ok and top_ok

