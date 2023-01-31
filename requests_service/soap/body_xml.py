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