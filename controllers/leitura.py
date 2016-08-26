# -*- coding: utf-8 -*-
from datetime import datetime

__author__ = 'carlosfaruolo'


@auth.requires_membership(role='admin')
def index():
    """
    Definindo valores de exibição

    """
    pagamento_realizado = request.vars['pagamento_realizado']  # flag indicando se estamos voltando de um pagamento

    # definindo qual refeição está sendo servida
    response.meta.time = request.now
    refeicao_atual = _busca_refeicao_atual()

    refeicoes_do_dia = db(db.refeicoes).select(orderby='id') or []

    if not refeicao_atual:
        redirect(URL('leitura', 'preparando_refeicao'))

    response.title = 'RESTAURANTE UNIVERSITÁRIO - UNIRIO'
    response.subtitle = 'Controle de refeições - ' + refeicao_atual.descricao

    form = FORM(T('Matrícula: '),
                INPUT(_name='matricula', requires=IS_NOT_EMPTY(), _error=T('Insira uma matrícula')),
                INPUT(_type='submit'),
                BR())
    src_foto = URL("static", "images/nova_silhueta.png")

    precos_info = None
    dados = None
    refeicoes_realizadas = None

    # aqui virao coisas do form da matricula
    if form.accepts(request, session):
        pagamento_realizado = None

        dados = api.get_single_result('V_PESSOAS_DADOS', {'MATRICULA': form.vars['matricula']}, bypass_no_content_exception=True)

        if dados:
            refeicoes_realizadas = _busca_refeicoes_realizadas(dados['matricula'])

            session.dados = dados
            session.id_refeicao = refeicao_atual.id

            _registra_log_refeicoes(ID_TIPO_LEITURA_LEITURA_DE_MATRICULA)
            fez_refeicao_subsidiada = ID_TIPO_PRECO_DESCONTO in [i['fk_tipo_preco'] for i in refeicoes_realizadas]

            precos_info = []

            for preco in refeicao_atual.precos:
                if preco['tipo_vinculo'] == dados['vinculo_item']:
                    precos_info.append({
                        'label': preco['descricao'],
                        'quantia': preco['quantia'],
                        'id_preco': preco['id']
                    })

            foto = _busca_foto(dados)
            if foto:
                src_foto = foto
                response.flash = 'Lido'
            else:
                # todo não deviamos tratar isso, mas...
                response.flash = 'Foto não encontrada'
        else:
            response.flash = 'Matricula inexistente ou ausente do banco de dados.'

    # aqui caso ocorreu xabu
    elif form.errors:
        response.flash = 'Erro na leitura'

    # mensagem ao entrar. podemos tirar isso tambem
    else:
        response.flash = 'Insira a matrícula'

    # Exibir as refeições cadastradas
    info_refeicoes_do_dia = []

    for row in refeicoes_do_dia:
        info_refeicao = {
            'descricao': row.descricao,
            'classes': 'caixa_refeicao'
        }

        if row.id == refeicao_atual.id:
            info_refeicao['classes'] += ' caixa_refeicao_atual'

        if _refeicao_ja_realizada(refeicoes_realizadas, row):
            info_refeicao['classes'] += ' caixa_refeicao_realizada'
        else:
            info_refeicao['classes'] += ' caixa_refeicao_nao_realizada'

        info_refeicoes_do_dia.append(info_refeicao)

    # Exibir contador geral de refeições
    contadores = {}
    for row in refeicoes_do_dia:
        contadores[row.descricao] = \
            db((db.log_refeicoes.fk_refeicao == row.id) &
               (db.log_refeicoes.fk_tipo_leitura != ID_TIPO_LEITURA_LEITURA_DE_MATRICULA)).count()

    return dict(form=form, refeicao=refeicao_atual, desc=dados, src_foto=src_foto,
                precos_info=precos_info, info_refeicoes_do_dia=info_refeicoes_do_dia, contadores=contadores,
                pagamento_realizado=pagamento_realizado)


@auth.requires_membership(role='admin')
def preparando_refeicao():
    response.title = 'RESTAURANTE UNIVERSITÁRIO'
    response.subtitle = 'Preparando próxima refeição'
    return {}


@auth.requires_membership(role='admin')
def registra_compra():
    _registra_log_refeicoes(ID_TIPO_LEITURA_PAGAMENTO, request.vars['id_preco'])
    redirect(URL('index', vars=dict(pagamento_realizado=True)), client_side=True)


def _busca_foto(dados):
    if dados['vinculo_item'] in [ID_TIPO_VINCULO_CATEGORIA_ALUNO_GRAD, ID_TIPO_VINCULO_CATEGORIA_ALUNO_POS]:
        tabela = 'V_ALU_FOTO'
    else:
        tabela = 'V_FUNC_FOTO'

    foto = None
    try:
        result = api.get_single_result(tabela, {'matricula': dados['matricula']}, bypass_no_content_exception=True)
        if result['foto']:
            foto = 'data:image/jpeg;base64,' + result['foto']
    except (TypeError, KeyError):
        # Caso de matricula invalida, result == None ou não tem a coluna foto
        # todo: Remover keyerror quando corrigir a view
        pass
    return foto


def _busca_refeicao_atual():

    """
    Baseado no horario atual, retorna, se existir, a refeição válida no momento.
    Retorna None caso não existam refeições ativas no horário atual.

    """

    refeicao = db((db.refeicoes.hr_fim >= response.meta.time) &
                  (db.refeicoes.hr_inicio <= response.meta.time)).select().first()

    # refeicao = db(db.refeicoes).select().first()  # DEBUG

    precos = db(db.v_precos.fk_refeicao == refeicao['id']).select()
    refeicao.precos = precos
    return refeicao


def _busca_refeicoes_realizadas(matricula):
    """

    Retorna refeicoes realizadas por um determinada matrícula NO DIA:

    """
    refeicoes_realizadas = db((db.v_log_refeicoes.matricula == matricula) &
                              (db.v_log_refeicoes.fk_tipo_leitura != ID_TIPO_LEITURA_LEITURA_DE_MATRICULA) &
                              (db.v_log_refeicoes.timestamp.day() == datetime.now().date().day) &
                              (db.v_log_refeicoes.timestamp.month() == datetime.now().date().month) &
                              (db.v_log_refeicoes.timestamp.year() == datetime.now().date().year)).select()

    return refeicoes_realizadas


def _refeicao_ja_realizada(refeicoes_realizadas, row):
    if not refeicoes_realizadas:
        return False

    return row.id in [i['fk_refeicao'] for i in refeicoes_realizadas]


def _registra_log_refeicoes(acao_id, preco=None):
    params = {
        'fk_refeicao': session.id_refeicao,
        'fk_preco': preco,
        'fk_tipo_leitura': acao_id,
        'categoria': session.dados['descricao_vinculo'],
        'matricula': session.dados['matricula']
    }

    db.log_refeicoes.bulk_insert([params])
