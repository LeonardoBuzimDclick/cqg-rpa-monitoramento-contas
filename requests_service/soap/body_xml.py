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


def envelope_fluig_gestores(username: str, password: str, company_id: str, process_id: str, indice: int, gestor: dict)\
        -> tuple[str, int]:
    
    tabela_colaboradores, indice = \
        cria_tabela_colaboradores(indice, gestor['sistema'], gestor['colab_list'], gestor['sistema_fluig'])
    
    return f"""
    <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" 
    xmlns:ws="http://ws.workflow.ecm.technology.totvs.com/">
        <soapenv:Header/>
        <soapenv:Body>
            <ws:startProcessClassic>
                <username>{username}</username>
                <password>{password}</password>
                <companyId>{company_id}</companyId> #TODO verificar com equipe que mexe no gecom os valores por sistema
                <processId>{process_id}</processId> #TODO id do fluxo de monitoramento = seria um indice ?! 
                <choosedState>9</choosedState>
                <colleagueIds></colleagueIds>
                <comments>fluxo startado via rpg monitoramento de contas</comments>
                <userId>gma2hsobqyvfzbga1506435909995</userId>
                <completeTask>true</completeTask>
                <attachments></attachments>
                <cardData>
                    <item>
                        <key>ambiente</key>
                        <value>{gestor['ambiente']}</value>
                    </item>
                    <item>
                        <key>gestorLogin</key>
                        <value>{gestor['gestor_login']}</value>
                    </item>
                    <item>
                        <key>gestorEmail</key>
                        <value>{gestor['gestor_email']}</value>
                    </item>
                    <item>
                        <key>gestorNome</key>
                        <value>{gestor['gestor_nome']}</value>
                    </item>         
                    {tabela_colaboradores}
                </cardData>
                <appointment></appointment>
                <managerMode>false</managerMode>
            </ws:startProcessClassic>
        </soapenv:Body>
    </soapenv:Envelope>""", indice


def cria_tabela_colaboradores(indice: int, sistema: str, colab_list: list, sistema_fluig: str) -> tuple[dict, int]:

    indice_local = indice
    envelope = {}
    for colab in colab_list:
        indice_local = + 1
        envelope += f"""                   
                    <item>
                        <key>tabela1Area___{indice}</key>
                        <value>{colab['area_colaborador']}</value>
                    </item>
                    <item>
                        <key>tabela1CCCodigo___{indice}</key> #TODO qual código é esse ?
                        <value>7910150</value>
                    </item>
                    <item>
                        <key>tabela1CCDescricao___{indice}</key>
                        <value>CSC-TI</value>
                    </item>
                    <item>
                        <key>tabela1ColabLogin___{indice}</key>
                        <value>{colab['login_colaborador']}</value>
                    </item>
                    <item>
                        <key>tabela1ColabEmail___{indice}</key>
                        <value>{colab['email_colaborador']}</value>
                    </item>
                    <item>
                        <key>tabela1ColabNome___{indice}</key>
                        <value>{colab['nom_colaborador']}</value>
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
                        <value>admin</value>
                    </item>
                    <item>
                        <key>tabela1GrupoNome___{indice}</key>
                        <value>Administradores</value>
                    </item>
                    <item>
                        <key>tabela1GrupoTipo___{indice}</key>
                        <value>Total</value>
                    </item>"""

    indice = indice_local
    return envelope, indice

