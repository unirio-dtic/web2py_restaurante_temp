# -*- coding: utf-8 -*-
from datetime import datetime

__author__ = 'carlosfaruolo'


def index():

    form = FORM(T('Matricula'), INPUT(_name='matricula', requires=IS_NOT_EMPTY()), INPUT(_type='submit'))
    src_foto = URL("static", "images/silhueta.png")

    refeicao_atual = busca_refeicao_atual()
    dados = None

    # aqui virao coisas do form
    if form.accepts(request, session):

        dados = busca_dados_por_matricula(form.vars['matricula'])
        foto = busca_foto(dados)
        if foto is not None:
            src_foto = foto

        registra_leitura(refeicao_atual['id'], form.vars['matricula'], dados['descricao_vinculo'])

        response.flash = 'Lido'

    # aqui caso ocorreu xabu
    elif form.errors:
        response.flash = 'Erro na leitura'

    # mensagem ao entrar. podemos tirar isso tambem
    else:
        response.flash = 'Insira a matricula'


    return dict(form=form, desc=dados, src_foto=src_foto)


def busca_dados_por_matricula(matricula):

    params = {'MATRICULA': matricula}
    result = api.get('V_PESSOAS_DADOS', params)
    return result.content[0]


def busca_foto(dados):
    tabela = None
    foto = None

    if dados['vinculo_item'] in [1, 2]:  # ou seja, aluno
        tabela = 'V_ALU_FOTO'
    else:
        tabela = 'V_FUNC_FOTO'

    try:
        result = api.get(tabela, {'MATRICULA': dados['matricula']})
        if result.content[0]['foto'] is not None:
            foto = 'data:image/jpeg;base64,' + result.content[0]['foto']
    except:
        # todo registrar essas ocorrencias de erro ao ler a foto
        pass

    return foto


def registra_leitura(refeicao, matricula, categoria):
    params = {
        'fk_refeicao': refeicao,
        'fk_tipo_leitura': 1,  # log de apenas leitura
        'timestamp': datetime.now(),
        'categoria': categoria,
        'matricula': matricula
    }

    db.log_refeicoes.bulk_insert([params])


def busca_refeicao_atual():
    # codigo dummy
    return db(db.refeicoes.id == 1).select()[0]
