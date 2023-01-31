import logging
import sys
from datetime import datetime
import requests
import json

from config.config_yaml import busca_valor_yaml
from config.log_config import ajusta_config_logging
from requests_service.mail.send_email import send_email
from requests_service.main_request_ambientes import busca_usuarios_ativos_nos_ambientes


def metodo_principal_execucao():
    data_ini = datetime.now()
    config_app = busca_valor_yaml()
    ajusta_config_logging(config_app)
    try:
        busca_usuarios_ativos_nos_ambientes(config=config_app)
        data_fim = datetime.now()
        time_diff = data_fim - data_ini
        logging.info(f'O tempo total de execução do robô foi: {time_diff}')
        sys.exit(0)
    except Exception as e:
        logging.warning("Robô teve problemas ao buscar as informações.")
        logging.warning(e)
        try:
            send_email(config_app['email'], f'Favor restartar o robô, pois o mesmo teve problema.')
            logging.info("Robô enviou o email de restart.")
        except Exception as e:
            logging.warning("Robô não conseguiu enviar o email solicitando o restart")
            logging.warning(e)
        data_fim = datetime.now()
        time_diff = data_fim - data_ini
        logging.info(f'O tempo total de execução do robô com erro foi: {time_diff}')
        sys.exit(-1)


def obter_gestores_seus_colaboradores_associados():

    request = requests.get('https://cqghom.queirozgalvao.com/corp-web/rest/organograma/obter/43701')

    response = json.loads(request.content)
    

    gestores_lista = response['filhos'][0]['filhos']

    colaboradores_lista = response['filhos'][0]['filhos'][0]
    for i in response['filhos'].get:
        print(type(i))


    # gestores = {'SIG_USUARIO': dic['SIG_USUARIO'] for dic in response['filhos'][0][0]}
    #
    # colaboradores = {dic['filhos'] for dic in response['filhos']}
    #
    # print(gestores)


if __name__ == '__main__':
    obter_gestores_seus_colaboradores_associados()
    # metodo_principal_execucao()



