def consulta_usuarios_ativos_fluig():
    """
    Esta função obtém os dados dos usuários ativos no FLUIG.
    :return: retorna um xml em string.
    """
    return """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:ws="http://ws.dataservice.ecm.technology.totvs.com/">
        <soapenv:Header/>
        <soapenv:Body>
            <ws:getDataset>
                <companyId>1</companyId>
                <username>portal.vendas@qgsa.com.br</username>
                <password>portal.vendas@21317100</password>
                <name>colleague</name>
                <fields>
                    <item>colleaguePK.colleagueId</item>
                    <item>colleagueName</item>
                    <item>mail</item>
                </fields>
                <constraints>
                    <item>
                        <contraintType>MUST</contraintType>
                        <fieldName>active</fieldName>
                        <finalValue>true</finalValue>
                        <initialValue>true</initialValue>
                        <likeSearch>false</likeSearch>
                    </item>
                </constraints>
                <order>
                </order>
            </ws:getDataset>
        </soapenv:Body>
    </soapenv:Envelope>"""


def consulta_usuarios_grupos_fluig():
    """
    Esta função obtém os grupos associados para cada usuário ativo no FLUIG.
    :return: retorna um xml em string.
    """
    return """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:ws="http://ws.dataservice.ecm.technology.totvs.com/">
        <soapenv:Header/>
        <soapenv:Body>
           <ws:getDataset>
                <companyId>1</companyId>
                <username>portal.vendas@qgsa.com.br</username>
                <password>portal.vendas@21317100</password>
                <name>colleagueGroup</name>
                <fields>
                </fields>
                <constraints>
                </constraints>
                <order>
                </order>
           </ws:getDataset>
        </soapenv:Body>
    </soapenv:Envelope>"""


def obter_dados_usuarios_ativos_rm_seus_grupos():
    """
    Esta função obtém os dados dos usuários ativos no RM e seus grupos associados.
    :return: retorna um xml em string.
    """
    return """
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
    xmlns:tot="http://www.totvs.com/">
        <soapenv:Header/>
        <soapenv:Body>
            <tot:RealizarConsultaSQL>
                <!--Optional:-->
                <tot:codSentenca>USUSERV01</tot:codSentenca>
                <!--Optional:-->
                <tot:codColigada>0</tot:codColigada>
                <!--Optional:-->
                <tot:codSistema>P</tot:codSistema>
                <!--Optional:-->
                <tot:parameters></tot:parameters>
            </tot:RealizarConsultaSQL>
        </soapenv:Body>
    </soapenv:Envelope>"""


def envelope_fluig_gestores(nom_gestor: str, password: str, company_id: str, process_id: str, login_gestor: str,
                            email_gestor: str, colab_list: list[dict], username: str) -> str:
    tabela_colaboradores = cria_tabela_colaboradores(colab_list)

    return \
        f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.workflow.ecm.technology.totvs.com/">
	<soapenv:Header />
	<soapenv:Body>
        <ws:startProcessClassic>
            <username>{username}</username>
            <password>{password}</password>
            <companyId>{company_id}</companyId>
            <processId>{process_id}</processId>
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
                    <value>{login_gestor}</value>
                </item>
                <item>
                    <key>gestorEmail</key>
                    <value>{email_gestor}</value>
                </item>
                <item>
                    <key>gestorNome</key>
                    <value>{nom_gestor}</value>
                </item>{tabela_colaboradores}
            </cardData>
            <appointment />
            <managerMode>false</managerMode>
        </ws:startProcessClassic>
    </soapenv:Body>
</soapenv:Envelope>"""


def cria_tabela_colaboradores(colab_list: list[dict]) -> str:
    envelope_list = []
    indice = 0

    for colab in colab_list:

        for usuario_agrupado in colab['usuario_agrupado']:

            for perfil in usuario_agrupado['perfil']:
                indice += 1
                sistema = usuario_agrupado['sistema']
                sistema_fluig = 'S' if sistema.upper() == 'FLUIG' else 'N'

                envelope = f"""
                <item>
                    <key>tabela1Area___{indice}</key>
                    <value>{colab['usuario_dado_corp_web']['area_colaborador']}</value>
                </item>
                <item>
                    <key>tabela1CCCodigo___{indice}</key>
                    <value>{colab['usuario_dado_corp_web']['cc_colaborador']}</value>
                </item>
                <item>
                    <key>tabela1CCDescricao___{indice}</key>
                    <value>{colab['usuario_dado_corp_web']['dsc_cc_colaborador']}</value>
                </item>
                <item>
                    <key>tabela1ColabLogin___{indice}</key>
                    <value>{colab['sig_usuario']}</value>
                </item>
                <item>
                    <key>tabela1ColabEmail___{indice}</key>
                    <value>{colab['email']}</value>
                </item>
                <item>
                    <key>tabela1ColabNome___{indice}</key>
                    <value>{colab['usuario_dado_corp_web']['nom_usuario']}</value>
                </item>
                <item>
                    <key>tabela1Sistema___{indice}</key>
                    <value>{sistema}</value>
                </item>
                <item>
                    <key>tabela1SistemaFluig___{indice}</key>
                    <value>{sistema_fluig}</value>
                </item>
                <item>
                    <key>tabela1GrupoCodigo___{indice}</key>
                    <value>{perfil['cod']}</value>
                </item>
                <item>
                    <key>tabela1GrupoNome___{indice}</key>
                    <value>{perfil['nom']}</value>
                </item>
                <item>
                    <key>tabela1GrupoTipo___{indice}</key>
                    <value>{perfil['tipo']}</value>
                </item>"""

                envelope_list.append(envelope)

    envelope_concatenado = ''
    for envelope in envelope_list:
        envelope_concatenado += envelope

    return envelope_concatenado
