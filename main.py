import json
import logging
import sys
from datetime import datetime

from config.config_yaml import busca_valor_yaml
from config.log_config import ajusta_config_logging
from requests_service.mail.send_email import send_email
from requests_service.main_request_ambientes import busca_usuarios_ativos_nos_ambientes
from requests_service.rest.rest_request import busca_gestores_colaboradores_corp_web_checa_arquivo_consolidado
from requests_service.soap.soap_request import enviar_gestores_colaboradores_fluig
from utils.create_file_csv import cria_csv_gestores_colab_fora_corpweb
from utils.listas_utils import filtrar_usuarios_corp_web_dados_completos


def metodo_principal_execucao():
    """
    Esta função executa o monitoramento de contas.
    """
    ajusta_config_logging()
    logging.info('-----Inicio do metodo principal de execucao-----')
    data_ini = datetime.now()
    config_app = busca_valor_yaml()
    urls_rest = config_app['request']['rest']
    url_usuarios_corp_web = urls_rest['corp_web']['usuarios']
    try:
        if busca_usuarios_ativos_nos_ambientes(config=config_app):
            logging.info('-----Inicio da fase 2 [agrupamento]-----')
            usuarios_corpweb, usuarios_fora_corpweb = \
                busca_gestores_colaboradores_corp_web_checa_arquivo_consolidado(
                    parametros=url_usuarios_corp_web['parametros'],
                    url=url_usuarios_corp_web['url']
                )

            usuarios_dados_completos = filtrar_usuarios_corp_web_dados_completos(usuarios_corpweb,
                                                                                 urls_rest['top']['url_findById'])
            enviar_gestores_colaboradores_fluig(usuarios_dados_completos)
            cria_csv_gestores_colab_fora_corpweb(usuarios_fora_corpweb)

            logging.info('-----Termino da fase 2 [agrupamento]-----')

        else:
            raise Exception('O robô não buscou os usuarios em todos ambientes')

        data_fim = datetime.now()
        time_diff = data_fim - data_ini
        logging.info('-----Termino do metodo principal de execucao-----')
        logging.info(f'O tempo total de execução do robô foi: {time_diff}')
        sys.exit(0)
    except Exception as e:
        logging.warning("Robô teve problemas ao buscar as informações.")
        logging.warning(e)
        try:
            send_email(config_app['email'], f'Favor restartar o robô, pois o mesmo teve problema.\n\n motivo: {e}')
            logging.info("Robô enviou o email de restart.")
        except Exception as e:
            logging.warning("Robô não conseguiu enviar o email solicitando o restart")
            logging.warning(e)
        data_fim = datetime.now()
        time_diff = data_fim - data_ini
        logging.info(f'O tempo total de execução do robô com erro foi: {time_diff}')
        sys.exit(-1)


if __name__ == '__main__':
    metodo_principal_execucao()


