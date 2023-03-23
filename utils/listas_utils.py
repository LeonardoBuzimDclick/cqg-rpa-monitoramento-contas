import operator
from itertools import groupby


def agrupa_listas_rm(list_dict: list) -> list:
    """
    Esta função agrupa as listas rm.
    :param list_dict: (list): recebe uma lista.
    :return: retorna um lista consolidada.
    """
    INFO = sorted(list_dict, key=key_func_rm)
    resutado = []
    for key, value in groupby(INFO, key_func_rm):
        resutado.append(list(value))
    return resutado


def agrupa_listas_consolidada(list_dict: list) -> list:
    """
    Esta função agrupa listas por determinada chave.
    :param list_dict: (list): recebe uma lista.
    :return: retorna um lista consolidada.
    """
    chave_sig_usuario = operator.itemgetter("sig_usuario", "email")
    group_sig_usuario = sorted(list_dict, key=chave_sig_usuario)
    usuario_agrupado_sig_usuario_list = []
    for key, values in groupby(group_sig_usuario, chave_sig_usuario):
        if key == '':
            for value in list(values):
                usuario_agrupado_sig_usuario_list.append(value)
            continue

        usuario_agrupado_sig_usuario = {}
        for value in list(values):
            usuario_agrupado_sig_usuario = {
                'sig_usuario': checa_chave_e_retorna_mesma_string('sig_usuario', usuario_agrupado_sig_usuario, value),
                'email': checa_chave_e_retorna_mesma_string('email', usuario_agrupado_sig_usuario, value),
                'sistema': checa_chave_e_add_lista('sistema', usuario_agrupado_sig_usuario, value),
                'ambiente': checa_chave_e_add_lista('ambiente', usuario_agrupado_sig_usuario, value),
                'perfil': checa_chave_e_add_lista('perfil', usuario_agrupado_sig_usuario, value),
            }
            usuario_agrupado_sig_usuario_list.append(usuario_agrupado_sig_usuario)

    chave_email = operator.itemgetter("email")
    group_email = sorted(usuario_agrupado_sig_usuario_list, key=chave_email)
    usuario_agrupado_email_list = []
    for key, values in groupby(group_email, chave_email):
        if key == '':
            for value in list(values):
                usuario_agrupado_email_list.append(value)
            continue

        usuario_agrupado_sig_usuario = {}
        for value in list(values):
            usuario_agrupado_sig_usuario = {
                'sig_usuario': checa_chave_e_retorna_mesma_string('sig_usuario', usuario_agrupado_sig_usuario, value),
                'email': checa_chave_e_retorna_mesma_string('email', usuario_agrupado_sig_usuario, value),
                'sistema': checa_chave_e_add_lista('sistema', usuario_agrupado_sig_usuario, value),
                'ambiente': checa_chave_e_add_lista('ambiente', usuario_agrupado_sig_usuario, value),
                'perfil': checa_chave_e_add_lista('perfil', usuario_agrupado_sig_usuario, value),
            }
            usuario_agrupado_email_list.append(usuario_agrupado_sig_usuario)

    return usuario_agrupado_email_list


def checa_chave_e_retorna_mesma_string(chave: str, dicionario_alvo: dict, dicionario_recurso: dict):
    """
    Esta função checa se a chave pertence ou não pertence ao dicionário alvo.
    :param chave: (str): valor a se testado.
    :param dicionario_alvo: (dict): dicionário alvo.
    :param dicionario_recurso: (dict): dicionário de retorno.
    :return: retorna uma dicinário com os valores.
    """
    if chave in dicionario_alvo:
        return dicionario_alvo[chave]
    else:
        return dicionario_recurso[chave]


def checa_chave_e_add_lista(chave: str, dicionario_alvo: dict, dicionario_recurso: dict):
    """
    Esta função checa se a chave pertence ou não pertence ao dicionário alvo.
    :param chave: (str): valor a se testado.
    :param dicionario_alvo: (dict): dicionário alvo.
    :param dicionario_recurso: (dict): dicionário de retorno.
    :return:
    """
    if chave in dicionario_alvo:
        dicionario_alvo[chave].append(dicionario_recurso[chave])
        return dicionario_alvo[chave]
    else:
        if type(dicionario_recurso[chave]) == list:
            return dicionario_recurso[chave]

        return [dicionario_recurso[chave]]


def key_func_consolidada(k: dict):
    """
    Esta função retorna o valor perante a uma chave padrão.
    usado para a consolidada
    :param k: (dict): o dictionario.
    :return: retorna o valor.
    """
    return k['sig_usuario']


def key_func_rm(k: dict):
    """
    Esta função retorna o valor perante a uma chave padrão.
    usado para o dado do RM
    :param k: (dict): o dictionario.
    :return: retorna o valor.
    """
    return k['email']


def separa_listas(seq: list[any], num: int) -> list[list]:
    """
    Esta função separa listas em páginas.
    :param seq: (list): recebe uma lista como parâmetro.
    :param num: (int): recebe um valor que define em quantas páginas será separada.
    :return: retorna uma lista separa em páginas.
    """
    avg = len(seq) / float(num)
    out = []
    last = 0.0

    while last < len(seq):
        out.append(seq[int(last):int(last + avg)])
        last += avg

    return out


def remove_duplicados(lista_itens_duplicados: list) -> list:
    """
    Esta função remove ítens duplicados dentro de uma lista e mantém a ordem original.
    :param lista_itens_duplicados: (list): recebe uma lista de ítens duplicados.
    :return: retorna uma lista com ítens não duplicados.
    """
    lista_itens_nao_duplicada = []
    for item in lista_itens_duplicados:
        if item not in lista_itens_nao_duplicada:
            lista_itens_nao_duplicada.append(item)
    return lista_itens_nao_duplicada


def agrupa_lista_por_email_sig_usuario(usuarios_list: list[dict]) -> list[dict]:
    usuarios_agrupado_list = []
    for usuario in usuarios_list:
        usuario_consolidado = []
        for usu in usuarios_list:
            if usu['sig_usuario'] != '' and usu['sig_usuario'] == usuario['sig_usuario'] or \
                    usu['email'] != '' and usu['email'] == usuario['email']:
                usuarios_list.remove(usu)
                usuario_consolidado.append(usu)

        usuario_final = {
            'sig_usuario': usuario['sig_usuario'],
            'email': usuario['email'],
            'usuario_agrupado': usuario_consolidado
        }
        usuarios_agrupado_list.append(usuario_final)

    return usuarios_agrupado_list
