import base64
import json
import logging
import re
from datetime import datetime

import requests

from config.request_config import request_post_soap_base
from requests_service.soap.body_xml import envelope_fluig_gestores
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
                perfil_consolidado = {'nom': f'{grupo["colleagueGroupPK.groupId"]}',
                                      'cod': f'{grupo["colleagueGroupPK.groupId"]}', 'tipo': 'COMUM'}

                grupos_associados.append(perfil_consolidado)

        usuario_consolidado['sig_usuario'] = re.search(r'([\w\\.]*)^([\w\\.]*)', usuario['mail'].upper()).group() \
            if usuario['mail'] else ''
        usuario_consolidado['email'] = usuario['mail'].upper() if usuario['mail'] else ''
        usuario_consolidado['sistema'] = 'FLUIG'
        usuario_consolidado['ambiente'] = tenant
        usuario_consolidado['perfil'] = json.dumps(grupos_associados)
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

        perfil_consolidado = {'nom': f'{usuario["NOME_PERFIL"]}',
                              'cod': f'{usuario["CODPERFIL"]}',
                              'tipo': f'{usuario["CODSISTEMA"]}'}

        usuario_consolidado = {'sig_usuario': usuario['CODUSUARIO'].upper() if usuario['CODUSUARIO'] else '',
                               'email': usuario['EMAIL'].upper() if usuario['EMAIL'] else '',
                               'sistema': 'RM',
                               'ambiente': tenant,
                               'perfil': perfil_consolidado
                               }
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
                               'perfil': json.dumps(perfil)
                               }

        usuarios_consolidados.append(usuario_consolidado)

    logging.info(
        f"-----Termino da busca dos usuarios ativos no rm no ambiente {tenant} com {len(usuarios_consolidados)} "
        f"dados-----")
    logging.debug(f"-----Inicio da escrita dos usuarios ativos do rm do ambiente {tenant} no CSV -----")
    date_files = datetime.now().strftime("%Y%m%dT%H%M%SZ")
    monta_arquivo_consolidado(headers_consolidados, usuarios_consolidados)
    criar_arquivo_csv(response, f'csv/usuario_rm_{tenant}_{date_files}.csv')
    logging.debug(f"-----Termino da escrita dos usuarios ativos do rm do ambiente {tenant} no CSV-----")


def enviar_gestores_colaboradores_fluig(gestores_colab_list: list[dict]):
    indice = 0
    for gestor_colab in gestores_colab_list:

        indice += 1

        envelope = envelope_fluig_gestores(nom_gestor=gestor_colab['nom_gestor'],
                                           login_gestor=gestor_colab['login_gestor'],
                                           email_gestor=gestor_colab['email_gestor'],
                                           colab_list=gestor_colab['colaboradores'],
                                           company_id=gestor_colab['company_id'],
                                           password='portal.vendas@21317100',
                                           username='portal.vendas@qgsa.com.br',
                                           process_id='procMonitorConta')\
            .encode('utf-8')

        response = requests.post(
            url='https://dc01-hom127.queirozgalvao.com/webdesk/ECMWorkflowEngineService?wsdl', data=envelope)
        print(response.status_code)

        # response = request_post_soap_base(
        # url='https://dc01-hom127.queirozgalvao.com/webdesk/ECMWorkflowEngineService?wsdl', body=envelope)


def body():
    return """
    <?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.workflow.ecm.technology.totvs.com/">
            <soapenv:Header />
            <soapenv:Body>
                <ws:startProcessClassic>
                    <username>portal.vendas@qgsa.com.br</username>
                    <password>portal.vendas@21317100</password>
                    <companyId>1</companyId>
                    <processId>procMonitorConta</processId>
                    <choosedState>9</choosedState>
                    <colleagueIds />
                    <comments>fluxo startado via rpg monitoramento de contas</comments>
                    <userId>gma2hsobqyvfzbga1506435909995</userId>
                    <completeTask>true</completeTask>
                    <attachments />
                    <cardData>
                        <item>
                           <key>ambiente</key>
                           <value>TESTE</value>
                        </item>
                        <item>
                           <key>gestorLogin</key>
                           <value>rodrigo.mostaert</value>
                        </item>
                        <item>
                           <key>gestorEmail</key>
                           <value>rodrigo.mostaert@qgsa.com.br</value>
                        </item>
                        <item>
                           <key>gestorNome</key>
                           <value>regis da silva guimaraes</value>
                        </item>
                        <item>
                           <key>tabela1Area___2</key>
                           <value>PSICOLOGO</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___2</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___2</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___2</key>
                           <value>DAYSI.RIBEIRO</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___2</key>
                           <value>DAYSI.RIBEIRO@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___2</key>
                           <value>DAYSI MOREIRA RIBEIRO</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___2</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___2</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___2</key>
                           <value>GP-TRE-70559</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___2</key>
                           <value>Treinamento - Tamoios</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___2</key>
                           <value>V</value>
                        </item>
                        <item>
                           <key>tabela1Area___3</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___3</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___3</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___3</key>
                           <value>JAMILE.PRADE</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___3</key>
                           <value>JAMILE.PRADE@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___3</key>
                           <value>JAMILE REGINA DO PRADO</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___3</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___3</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___3</key>
                           <value>FP-ADM-30009</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___3</key>
                           <value>Contornos - Filial 1/5</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___3</key>
                           <value>P</value>
                        </item>
                        <item>
                           <key>tabela1Area___4</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___4</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___4</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___4</key>
                           <value>JAMILE.PRADE</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___4</key>
                           <value>JAMILE.PRADE@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___4</key>
                           <value>JAMILE REGINA DO PRADO</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___4</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___4</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___4</key>
                           <value>AP-ADM-30009</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___4</key>
                           <value>Automação de Ponto - Contornos</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___4</key>
                           <value>A</value>
                        </item>
                        <item>
                           <key>tabela1Area___5</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___5</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___5</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___5</key>
                           <value>JAMILE.PRADE</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___5</key>
                           <value>JAMILE.PRADE@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___5</key>
                           <value>JAMILE REGINA DO PRADO</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___5</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___5</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___5</key>
                           <value>FP-GF-GER</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___5</key>
                           <value>Geral Obras</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___5</key>
                           <value>F</value>
                        </item>
                        <item>
                           <key>tabela1Area___6</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___6</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___6</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___6</key>
                           <value>JAMILE.PRADE</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___6</key>
                           <value>JAMILE.PRADE@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___6</key>
                           <value>JAMILE REGINA DO PRADO</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___6</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___6</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___6</key>
                           <value>SGB-GER-OBRA</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___6</key>
                           <value>Geral Obras</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___6</key>
                           <value>G</value>
                        </item>
                        <item>
                           <key>tabela1Area___7</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___7</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___7</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___7</key>
                           <value>JAMILE.PRADE</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___7</key>
                           <value>JAMILE.PRADE@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___7</key>
                           <value>JAMILE REGINA DO PRADO</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___7</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___7</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___7</key>
                           <value>GP-BEN-30009</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___7</key>
                           <value>Gestão Benefícios - Contornos</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___7</key>
                           <value>V</value>
                        </item>
                        <item>
                           <key>tabela1Area___8</key>
                           <value>ENCARREGADO PESSOAL II</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___8</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___8</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___8</key>
                           <value>MFLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___8</key>
                           <value>MFLEGLER@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___8</key>
                           <value>MAGDA FRANCISCA FLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___8</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___8</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___8</key>
                           <value>FP-CON-30016</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___8</key>
                           <value>Consulta e Emissao de Relatórios</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___8</key>
                           <value>P</value>
                        </item>
                        <item>
                           <key>tabela1Area___9</key>
                           <value>ENCARREGADO PESSOAL II</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___9</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___9</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___9</key>
                           <value>MFLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___9</key>
                           <value>MFLEGLER@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___9</key>
                           <value>MAGDA FRANCISCA FLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___9</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___9</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___9</key>
                           <value>GP-REC-30016</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___9</key>
                           <value>Recrutamento e Selecao - Santo Amaro</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___9</key>
                           <value>V</value>
                        </item>
                        <item>
                           <key>tabela1Area___10</key>
                           <value>ENCARREGADO PESSOAL II</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___10</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___10</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___10</key>
                           <value>MFLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___10</key>
                           <value>MFLEGLER@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___10</key>
                           <value>MAGDA FRANCISCA FLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___10</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___10</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___10</key>
                           <value>AP-ADM-30016</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___10</key>
                           <value>Automação de Ponto - Santo Amaro</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___10</key>
                           <value>A</value>
                        </item>
                        <item>
                           <key>tabela1Area___11</key>
                           <value>ENCARREGADO PESSOAL II</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___11</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___11</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___11</key>
                           <value>MFLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___11</key>
                           <value>MFLEGLER@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___11</key>
                           <value>MAGDA FRANCISCA FLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___11</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___11</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___11</key>
                           <value>FP-GF-GER</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___11</key>
                           <value>Geral Obras</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___11</key>
                           <value>F</value>
                        </item>
                        <item>
                           <key>tabela1Area___12</key>
                           <value>ENCARREGADO PESSOAL II</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___12</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___12</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___12</key>
                           <value>MFLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___12</key>
                           <value>MFLEGLER@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___12</key>
                           <value>MAGDA FRANCISCA FLEGLER</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___12</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___12</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___12</key>
                           <value>SGB-GER-OBRA</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___12</key>
                           <value>Geral Obras</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___12</key>
                           <value>G</value>
                        </item>
                        <item>
                           <key>tabela1Area___13</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___13</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___13</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___13</key>
                           <value>SHERON.SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___13</key>
                           <value>SHERON.SANTOS@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___13</key>
                           <value>SHERON ANA HILARIO DOS SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___13</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___13</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___13</key>
                           <value>FP-GF-GER</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___13</key>
                           <value>Geral Obras</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___13</key>
                           <value>F</value>
                        </item>
                        <item>
                           <key>tabela1Area___14</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___14</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___14</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___14</key>
                           <value>SHERON.SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___14</key>
                           <value>SHERON.SANTOS@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___14</key>
                           <value>SHERON ANA HILARIO DOS SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___14</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___14</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___14</key>
                           <value>SGB-GER-OBRA</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___14</key>
                           <value>Geral Obras</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___14</key>
                           <value>G</value>
                        </item>
                        <item>
                           <key>tabela1Area___15</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___15</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___15</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___15</key>
                           <value>SHERON.SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___15</key>
                           <value>SHERON.SANTOS@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___15</key>
                           <value>SHERON ANA HILARIO DOS SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___15</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___15</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___15</key>
                           <value>FP-ADM-30009</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___15</key>
                           <value>Contornos - Filial 1/5</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___15</key>
                           <value>P</value>
                        </item>
                        <item>
                           <key>tabela1Area___16</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___16</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___16</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___16</key>
                           <value>SHERON.SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___16</key>
                           <value>SHERON.SANTOS@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___16</key>
                           <value>SHERON ANA HILARIO DOS SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___16</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___16</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___16</key>
                           <value>GP-BEN-30009</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___16</key>
                           <value>Gestão Benefícios - Contornos</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___16</key>
                           <value>V</value>
                        </item>
                        <item>
                           <key>tabela1Area___17</key>
                           <value>AUXILIAR ADMINISTRATIVO I</value>
                        </item>
                        <item>
                           <key>tabela1CCCodigo___17</key>
                           <value>70205590001208</value>
                        </item>
                        <item>
                           <key>tabela1CCDescricao___17</key>
                           <value>GAF - ADMINISTRATIVO</value>
                        </item>
                        <item>
                           <key>tabela1ColabLogin___17</key>
                           <value>SHERON.SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1ColabEmail___17</key>
                           <value>SHERON.SANTOS@QUEIROZGALVAO.COM</value>
                        </item>
                        <item>
                           <key>tabela1ColabNome___17</key>
                           <value>SHERON ANA HILARIO DOS SANTOS</value>
                        </item>
                        <item>
                           <key>tabela1Sistema___17</key>
                           <value>RM</value>
                        </item>
                        <item>
                           <key>tabela1SistemaFluig___17</key>
                           <value>N</value>
                        </item>
                        <item>
                           <key>tabela1GrupoCodigo___17</key>
                           <value>AP-ADM-30009</value>
                        </item>
                        <item>
                           <key>tabela1GrupoNome___17</key>
                           <value>Automação de Ponto - Contornos</value>
                        </item>
                        <item>
                           <key>tabela1GrupoTipo___17</key>
                           <value>A</value>
                        </item>
                    </cardData>
                    <appointment />
                    <managerMode>false</managerMode>
                </ws:startProcessClassic>
            </soapenv:Body>
        </soapenv:Envelope>"""