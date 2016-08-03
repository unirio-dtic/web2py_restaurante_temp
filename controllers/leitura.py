# -*- coding: utf-8 -*-
from datetime import datetime

__author__ = 'carlosfaruolo'


def index():
    """Definindo valores de exibição"""
    # definindo qual refeição está sendo servida
    response.meta.time = request.now
    refeicao = busca_refeicao_atual()

    response.title = 'RESTAURANTE UNIVERSITÁRIO - UNIRIO'
    response.subtitle = 'Controle de refeições - ' + str(refeicao[0].descricao).upper()

    form = FORM(T('Matrícula: '),
                INPUT(_name='matricula', requires=IS_NOT_EMPTY()),
                INPUT(_type='submit'),
                BR())
    src_foto = URL("static", "images/silhueta.png")

    dados = None

    # aqui virao coisas do form
    if form.accepts(request, session):

        dados = busca_dados_por_matricula(form.vars['matricula'])
        foto = busca_foto(dados)
        if foto is not None:
            src_foto = foto

        registra_leitura(refeicao['id'], form.vars['matricula'], dados['descricao_vinculo'])

        response.flash = 'Lido'

    # aqui caso ocorreu xabu
    elif form.errors:
        response.flash = 'Erro na leitura'

    # mensagem ao entrar. podemos tirar isso tambem
    else:
        response.flash = 'Insira a matrícula'

    texto = ''
    listar_botoes = []
    botoes = []
    for row in db(db.refeicoes.descricao != '').select():
        texto += ' %s, ' % str(row['descricao'])
        botoes.append(TAG.button(row['descricao'], _type='button', _='disable'))
    form2 = SQLFORM.factory(db=None, buttons=botoes)

    return dict(form=form, desc=dados, src_foto=src_foto, refeicao=refeicao, dbug=texto, form2=form2)

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
    return db(db.refeicoes.hr_fim >= response.meta.time).select()


def busca_refeicoes_realizadas():
    pass  # todo
