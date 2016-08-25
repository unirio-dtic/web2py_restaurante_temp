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
    refeicao = _busca_refeicao_atual()
    if not refeicao:
        redirect(URL('leitura', 'preparando_refeicao'))  # TODO fazer uma pagina dizendo que nao possuem refeicoes no horario atual

    response.title = 'RESTAURANTE UNIVERSITÁRIO - UNIRIO'
    response.subtitle = 'Controle de refeições - ' + refeicao.descricao

    form = FORM(T('Matrícula: '),
                INPUT(_name='matricula', requires=IS_NOT_EMPTY(), _error=T('Insira uma matrícula')),
                INPUT(_type='submit'),
                BR())
    src_foto = URL("static", "images/nova_silhueta.png")

    form2 = None
    dados = None
    refeicoes_realizadas = None

    pagamento_realizado = request.vars['pagamento_realizado']

    # aqui virao coisas do form da matricula
    if form.accepts(request, session):
        pagamento_realizado = None
        dados = None
        try:
            dados = _busca_dados_por_matricula(form.vars['matricula'])
        except NoContentException:
            dados = None

        if dados is not None:
            _registra_leitura(refeicao.id, form.vars['matricula'], dados['descricao_vinculo'])
            refeicoes_realizadas = _busca_refeicoes_realizadas(dados['matricula'])

            ja_fez_refeicao_subsidiada = ID_TIPO_LEITURA_PAGAMENTO_SUBSIDIADO not in [i['fk_tipo_leitura'] for i in refeicoes_realizadas]

            subsidio_permitido = (dados['vinculo_item'] == ID_TIPO_ALUNO_GRADUACAO
                                  and refeicao.id != 1  # TODO tem que se verificar o 'tipo' de refeição, e não o id dela. Cabe uma analise de uma columa ou uma tabela a mais no modelo.
                                  and ja_fez_refeicao_subsidiada)

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
                      _style='visibility:visible' if subsidio_permitido else 'visibility:hidden'),)

            foto = _busca_foto(dados)
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
    # Exibir as refeições cadastradas
    horarios = []

    for row in db(db.refeicoes).select():
        horarios.append(IMG(_src=URL("static", "images/caixa_vermelha.png" if _refeicao_ja_realizada(refeicoes_realizadas, row) else "images/caixa_azul.png"),
                            _name='img_' + str(row.descricao), _style="border: 2px solid black;" if row.id == refeicao.id else None))
        horarios.append(SPAN(str(row.descricao), _name='caption',
                             _style='position: absolute; margin-top: 40px; margin-left: -130px; color: white;'))

    # Exibir contador geral de refeições
    contadores = {}
    rows = db(db.refeicoes).select()
    for row in rows or []:
        contadores[row.descricao] = \
            db((db.log_refeicoes.fk_refeicao == row.id) &
               (db.log_refeicoes.fk_tipo_leitura != ID_TIPO_LEITURA_LEITURA_DE_MATRICULA)).count()

    return dict(form=form, refeicao=refeicao, desc=dados, src_foto=src_foto,
                form2=form2, horarios=horarios, contadores=contadores,
                pagamento_realizado=pagamento_realizado)


def preparando_refeicao():
    response.title = 'RESTAURANTE UNIVERSITÁRIO'
    response.subtitle = 'Preparando próxima refeição'

    form = (DIV(A(IMG(_src=URL('static', 'images/aguardar_refeicao.jpg')), BR(),
                  LABEL(T("Aguarde o horário da próxima refeição")), _href=URL('leitura', 'index'))))

    return dict(form=form)


def registra_compra_total():
    _registra_log_refeicoes(request.vars['ret_refeicao_id'], request.vars['ret_matricula'], request.vars['ret_descricao_vinculo'], ID_TIPO_LEITURA_PAGAMENTO_TOTAL)
    redirect(URL('index', vars=dict(pagamento_realizado=True)), client_side=True)


def registra_compra_subs():
    _registra_log_refeicoes(request.vars['ret_refeicao_id'], request.vars['ret_matricula'], request.vars['ret_descricao_vinculo'], ID_TIPO_LEITURA_PAGAMENTO_SUBSIDIADO)
    redirect(URL('index', vars=dict(pagamento_realizado=True)), client_side=True)


def _registra_leitura(refeicao, matricula, categoria):
    """
    Registra a leitura da matricula

    """
    _registra_log_refeicoes(refeicao, matricula, categoria, ID_TIPO_LEITURA_LEITURA_DE_MATRICULA)


def _busca_dados_por_matricula(matricula):

    params = {'MATRICULA': matricula}
    result = api.get('V_PESSOAS_DADOS', params)
    return result.content[0]


def _busca_foto(dados):
    tabela = None
    foto = None

    if dados['vinculo_item'] in [1, 2]:  # ou seja, aluno
        tabela = 'V_ALU_FOTO'
    else:
        tabela = 'V_FUNC_FOTO'

    try:
        result = api.get_single_result(tabela, {'MATRICULA': dados['matricula']}, bypass_no_content_exception=True)
        if result.content['foto'] is not None:
            foto = 'data:image/jpeg;base64,' + result.content['foto']
    except AttributeError:
        # Caso de matricula invalida, result == None
        pass
    return foto


def _busca_refeicao_atual():

    """
    Baseado no horario atual, retorna, se existir, a refeição válida no momento.
    Retorna None caso não existam refeições ativas no horário atual.

    """

    return db((db.refeicoes.hr_fim >= response.meta.time) &
              (db.refeicoes.hr_inicio <= response.meta.time)).select().first()

# db(db.refeicoes.hr_fim >= response.meta.time).select().first()


def _busca_refeicoes_realizadas(matricula):
    """

    Retorna refeicoes realizadas por um determinada matrícula NO DIA:

    """
    refeicoes_realizadas = db((db.log_refeicoes.matricula == matricula) &
                              (db.log_refeicoes.fk_tipo_leitura != ID_TIPO_LEITURA_LEITURA_DE_MATRICULA) &
                              (db.log_refeicoes.timestamp.day() == datetime.now().date().day) &
                              (db.log_refeicoes.timestamp.month() == datetime.now().date().month) &
                              (db.log_refeicoes.timestamp.year() == datetime.now().date().year)).select()

    return refeicoes_realizadas


def _refeicao_ja_realizada(refeicoes_realizadas, row):
    if not refeicoes_realizadas:
        return False

    return row.id in [i['fk_refeicao'] for i in refeicoes_realizadas]


def _registra_log_refeicoes(refeicao_id, matricula, categoria_desc, acao_id):
    params = {
        'fk_refeicao': refeicao_id,
        'fk_tipo_leitura': acao_id,
        'timestamp': datetime.now(),
        'categoria': categoria_desc,
        'matricula': matricula
    }

    db.log_refeicoes.bulk_insert([params])
