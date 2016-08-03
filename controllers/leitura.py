# -*- coding: utf-8 -*-
from datetime import datetime

__author__ = 'carlosfaruolo'


def index():
    """Definindo valores de exibição"""
    # definindo qual refeição está sendo servida
    response.meta.time = request.now
    refeicao = busca_refeicao_atual()

    response.title = 'RESTAURANTE UNIVERSITÁRIO - UNIRIO'
    response.subtitle = 'Controle de refeições - ' + str(refeicao.descricao).upper()

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

        registra_leitura(refeicao.id, form.vars['matricula'], dados['descricao_vinculo'])

        response.flash = 'Lido'

    # aqui caso ocorreu xabu
    elif form.errors:
        response.flash = 'Erro na leitura'

    # mensagem ao entrar. podemos tirar isso tambem
    else:
        response.flash = 'Insira a matrícula'

    horarios = []
    texto_debug = []
    for row in db(db.refeicoes.descricao != '').select():  # todo rever a condicao != ''
        if row.id is refeicao.id:
            horarios.append(SPAN(row.descricao + ' - Atual'))
        else:
            horarios.append(SPAN(row.descricao))
        texto_debug.append(' %s, ' % str(row.descricao))  # debug

    form2 = FORM(
        INPUT(_name='but_pag_total', _type='button', _value=T("Pagamento total: R$") + refeicao.preco_total, _='disable'),
        INPUT(_name='but_pag_subs', _type='button', _value=T("Pagamento subsidiado: R$") + refeicao.preco_subsidiado, _='disable')
    )

    return dict(form=form, refeicao=refeicao, desc=dados, src_foto=src_foto, form2=form2, horarios=horarios, dbug=texto_debug)


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
    return db(db.refeicoes.hr_fim >= response.meta.time).select()[0]


def busca_refeicoes_realizadas():
    pass  # todo
