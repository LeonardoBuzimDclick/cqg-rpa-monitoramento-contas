import logging
import sys
from datetime import datetime

from config.config_yaml import busca_valor_yaml
from config.log_config import ajusta_config_logging
from config.request_config import request_rest_get_base
from create_files.create_file_csv import ler_arquivo_consolidada
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


def obter_gestores_seus_colaboradores_associados(url: str, tenant: str) -> list:
    response = request_rest_get_base(url)

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
                'sig_usuario': colaborador['sig_usuario'],
                'email': '' if not colaborador['email'] else colaborador['email']
            }
            colaboradores_lista.append(colaborador_final)

        gestor_final = {
            'sig_usuario': gestor['SIG_USUARIO'],
            'email': '' if not gestor['TXT_EMAIL'] else gestor['TXT_EMAIL'],
            'sig_estr_organizacional': gestor['SIG_ESTR_ORGANIZACIONAL'],
            'colaboradores': colaboradores_lista
        }
        gestores_com_colaboradores.append(gestor_final)

    return gestores_com_colaboradores


def checa_colaboradores_em_corpweb(gestores: list[dict]) -> list[dict]:
    ini = datetime.now()
    usuarios = ler_arquivo_consolidada()
    if len(usuarios) < len(gestores):
        for usuario in usuarios:
            for gestor in gestores:
                if gestor['ambiente'] == usuario['ambiente']:
                    for colaborador in gestor['gestor_colaboradores']['colaboradores']:
                        if usuario['sig_usuario'] == colaborador['sig_usuario'] or \
                                usuario['email'] == colaborador['email']:
                            usuarios.remove(usuario)
                            logging.info(f'usuario está corpweb: {usuario}')
                            break
                        else:
                            print(f'usuario: {usuario}')
                            print(f'colaborador: {colaborador}')
                    break
    else:
        for gestor in gestores:
            for usuario in usuarios:
                isBreak = False
                if gestor['ambiente'] == usuario['ambiente']:
                    for colaborador in gestor['gestor_colaboradores']['colaboradores']:
                        if usuario['sig_usuario'] == colaborador['sig_usuario'] or \
                                usuario['email'] == colaborador['email']:
                            usuarios.remove(usuario)
                            isBreak = True
                            logging.info(f'usuario está corpweb: {usuario}')
                            break
                        else:
                            print(f'usuario: {usuario}')
                            print(f'colaborador: {colaborador}')
                    if isBreak:
                        break
    fim = datetime.now()
    print(f'tempo exec loop: {fim - ini}')
    return usuarios


if __name__ == '__main__':

    # metodo_principal_execucao()

    parametros = {'cqg': '43542'}
    url = 'https://cqghom.queirozgalvao.com/corp-web/rest/organograma/obter/'
    gestores_colaborares_por_ambiente_list = []
    for chave, valor in parametros.items():
        url_parametrizada = url+valor

        gestores_colaborares_por_ambiente = {
            'ambiente': chave,
            'gestor_colaboradores': obter_gestores_seus_colaboradores_associados(url, chave)
        }

        gestores_colaborares_por_ambiente_list.append(gestores_colaborares_por_ambiente)
        usuarios = checa_colaboradores_em_corpweb(gestores_colaborares_por_ambiente_list)
        print(len(usuarios))
        for usuario in usuarios:
            print(usuario)

