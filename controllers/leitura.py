# -*- coding: utf-8 -*-
from datetime import datetime
from unirio.api.exceptions import NoContentException

__author__ = 'carlosfaruolo'


def index():
    """
    Definindo valores de exibição

    """
    # definindo qual refeição está sendo servida
    response.meta.time = request.now
    refeicao = busca_refeicao_atual()

    response.title = 'RESTAURANTE UNIVERSITÁRIO - UNIRIO'
    response.subtitle = 'Controle de refeições - ' + str(refeicao.descricao)

    form = FORM(T('Matrícula: '),
                INPUT(_name='matricula', requires=IS_NOT_EMPTY()),
                INPUT(_type='submit'),
                BR())
    src_foto = URL("static", "images/nova_silhueta.png")

    form2 = None

    dados = None

    pagamento_realizado = request.vars['pagamento_realizado']

    # aqui virao coisas do form da matricula
    if form.accepts(request, session):
        pagamento_realizado = None
        dados = None
        try:
            dados = busca_dados_por_matricula(form.vars['matricula'])
        except NoContentException:
            dados = None

        if dados is not None:
            registra_leitura(refeicao.id, form.vars['matricula'], dados['descricao_vinculo'])

            form2 = FORM(
                INPUT(_name='ret_matricula', _type='text', _value=dados['matricula'], _style='visibility:hidden'),
                INPUT(_name='ret_refeicao_id', _type='text', _value=str(refeicao.id), _style='visibility:hidden'),
                INPUT(_name='ret_descricao_vinculo', _type='text', _value=dados['descricao_vinculo'].encode('utf-8'), _style='visibility:hidden'),
                BR(),
                INPUT(_name='but_pag_total', _type='button',
                      _value=T("Pagamento total: R$ ") + str(refeicao.preco_total).replace('.', ','),
                      _onclick="ajax('registra_compra_total',['ret_refeicao_id', 'ret_matricula', 'ret_descricao_vinculo'], '')"),
                INPUT(_name='but_pag_subs', _type='button',
                      _value=T("Pagamento subsidiado: R$ ") + str(refeicao.preco_subsidiado).replace('.', ','),
                      _onclick="ajax('registra_compra_subs',['ret_refeicao_id', 'ret_matricula', 'ret_descricao_vinculo'], '')",
                      # ocultar opção de pagamento subsidiado caso não seja aluno graduação ou a refeição é café da manhã.
                      _style='visibility:hidden' if dados['vinculo_item'] != 1 or refeicao.id == 1 else 'visibility:visible'),)

            foto = busca_foto(dados)
            if foto is not None:
                src_foto = foto

            response.flash = 'Lido'
        else:
            response.flash = 'Matricula inexistente ou ausente do banco de dados.'

    # aqui caso ocorreu xabu
    elif form.errors:
        response.flash = 'Erro na leitura'

    # mensagem ao entrar. podemos tirar isso tambem
    else:
        response.flash = 'Insira a matrícula'

    # if form2 and form2.accepts(request, session):
    #     response.flash = 'foi'
    #     pass

    horarios = []

    for row in db(db.refeicoes.descricao != '').select():  # TODO rever a condicao != ''
        if row.id == refeicao.id:
            horarios.append(IMG(_src=URL("static", "images/caixa1.png"), _name='img_' + str(row.descricao),
                                _style="border: 2px solid black;"))
            horarios.append(SPAN(str(row.descricao), _name='caption', _style='position: absolute; margin-top: 40px; '
                                                                             'margin-left: -130px; color: white;'))
        else:
            horarios.append(IMG(_src=URL("static", "images/caixa1.png"), _name='img_' + str(row.descricao)))
            horarios.append(SPAN(str(row.descricao), _name='caption', _style='position: absolute; margin-top: 40px; '
                                                                             'margin-left: -130px; color: white; '))

    contadores = {}
    # TODO: contador sempre retorna 1 a mais - descobrir motivo
    for row in db(db.refeicoes).select():
        if row is not None:
            contadores[str(row.descricao)] = db(db.log_refeicoes.fk_refeicao == row.id).count(db.log_refeicoes.fk_tipo_leitura != 1)

    return dict(form=form, refeicao=refeicao, desc=dados, src_foto=src_foto,
                form2=form2, horarios=horarios, contadores=contadores,
                pagamento_realizado=pagamento_realizado)


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
    except NoContentException:
        pass  # normal isso ocorrer, nem todos possuem foto
    except:
        # TODO registrar essas ocorrencias de erro ao ler a foto
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


def registra_compra_total():

    """
    Registra as compras com valor total

    """
    params = {
        'fk_refeicao': request.vars['ret_refeicao_id'],
        'fk_tipo_leitura': 2,  # log de compra total
        'timestamp': datetime.now(),
        'categoria': request.vars['ret_descricao_vinculo'],
        'matricula': request.vars['ret_matricula']
    }

    db.log_refeicoes.bulk_insert([params])
    redirect(URL('index', vars=dict(pagamento_realizado=True)), client_side=True)


def registra_compra_subs():

    """
    Registra as compras com valor subsisdiado

    """

    params = {
        'fk_refeicao': request.vars['ret_refeicao_id'],
        'fk_tipo_leitura': 3,  # log de compra subsidiada
        'timestamp': datetime.now(),
        'categoria': request.vars['ret_descricao_vinculo'],
        'matricula': request.vars['ret_matricula']
    }

    db.log_refeicoes.bulk_insert([params])
    redirect(URL('index', vars=dict(pagamento_realizado=True)), client_side=True)


def busca_refeicao_atual():

    """
    Compara como horário e retorna a refeição atual

    """

    return db(db.refeicoes.hr_fim >= response.meta.time).select()[0]


def busca_refeicoes_realizadas(matricula):
    """

    Retorna refeicoes realizadas por um determinada matrícula NO DIA:

    """
    return db(db.log_refeicoes.matricula == matricula and
              db.log_refeicoes.timestamp == datetime.today() and
              db.log_refeicoes.fk_tipo_leitura != 1).select()
