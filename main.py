import logging
import sys
from datetime import datetime

from config.config_yaml import busca_valor_yaml
from config.log_config import ajusta_config_logging
from requests_service.mail.send_email import send_email
from requests_service.main_request_ambientes import busca_usuarios_ativos_nos_ambientes
from requests_service.rest.rest_request import busca_gestores_colaboradores_corp_web_checa_arquivo_consolidado


def metodo_principal_execucao():
    """
    Esta função executa o monitoramento de contas.
    """
    logging.info('-----Inicio do metodo principal de execucao-----')
    data_ini = datetime.now()
    config_app = busca_valor_yaml()
    try:
        buscou_todos_usuarios = busca_usuarios_ativos_nos_ambientes(config=config_app)
        if buscou_todos_usuarios:
            busca_gestores_colaboradores_corp_web_checa_arquivo_consolidado(parametros=config_app, url=config_app)
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
    ajusta_config_logging()
    metodo_principal_execucao()
