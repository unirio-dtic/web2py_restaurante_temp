# -*- coding: utf-8 -*-
from datetime import datetime

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

    form2 = FORM(
        INPUT(_name='ret_matricula', _type='text', _value=''),
        INPUT(_name='ret_refeicao_id', _type='text', _value=str(refeicao.id)),
        INPUT(_name='ret_descricao_vinculo', _type='text', _value=''),
        BR(),
        INPUT(_name='but_pag_total', _type='button',
              _value=T("Pagamento total: R$ ") + str(refeicao.preco_total).replace('.', ',')),
        INPUT(_name='but_pag_subs', _type='button',
              _value=T("Pagamento subsidiado: R$ ") + str(refeicao.preco_subsidiado).replace('.', ',')))
    """
            _onclick="ajax('registra_compra_total', [" + str(refeicao.id) + ", "
                           + str(form.vars['matricula']) + ", "
                           + str(dados['descricao_vinculo']) + "], 'target')"
            """
    dados = None
    texto_debug = []

    # aqui virao coisas do form
    if form.accepts(request, session):

        dados = busca_dados_por_matricula(form.vars['matricula'])
        foto = busca_foto(dados)
        if foto is not None:
            src_foto = foto

        caixas = form2.elements('input', _type='text')
        for c in caixas:
            if c['_name'] == 'ret_matricula':
                c['_value'] = str(dados['matricula'])
            if c['_name'] == 'ret_descricao_vinculo':
                c['_value'] = dados['descricao_vinculo']
            c['_readonly'] = 'readonly'

        registra_leitura(refeicao.id, form.vars['matricula'], dados['descricao_vinculo'])

        # adicionar função do botões (dependente de haver dados)

        click_action_total = "ajax('leitura/registra_compra_total',['ret_refeicao_id', 'ret_matricula', " \
                             "'ret_descricao_vinculo'], '')"
        click_action_sub = "ajax('leitura/registra_compra_subsi',['ret_refeicao_id', 'ret_matricula', " \
                             "'ret_descricao_vinculo'], '')"
        form2.element('input', _type='button', _name='but_pag_total')['_onclick'] = click_action_total
        form2.element('input', _type='button', _name='but_pag_total')['_onclick'] = click_action_sub

        texto_debug.append(str(foto))

    # caso não seja aluno ocultar opção de pagamento subsidiado

        if not eh_aluno(dados) or refeicao.id == 1:
            form2.element('input', _type='button', _name='but_pag_subs')['_style'] = 'visibility:hidden'
        elif dados['matricula'] in busca_refeicoes_realizadas(dados['matricula']):
            form2.element('input', _type='button', _name='but_pag_subs')['_style'] = 'visibility:hidden'
            form2.element('input', _type='button', _name='but_pag_total')['_style'] = 'visibility:hidden'
        else:
            form2.element('input', _type='button', _name='but_pag_subs')['_style'] = 'visibility:visible'

        response.flash = 'Lido'

    # aqui caso ocorreu xabu
    elif form.errors:
        response.flash = 'Erro na leitura'

    # mensagem ao entrar. podemos tirar isso tambem
    else:
        response.flash = 'Insira a matrícula'


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
        texto_debug.append(' %s, ' % row.descricao)  # debug


    contadores = {}
    # TODO: contador sempre retorna 1 a mais - descobrir motivo
    for row in db(db.refeicoes).select():
        if row is not None:
            contadores[str(row.descricao)] = db(db.log_refeicoes.fk_refeicao == row.id).count(db.log_refeicoes.fk_tipo_leitura != 1)

    return dict(form=form, refeicao=refeicao, desc=dados, src_foto=src_foto,
                form2=form2, horarios=horarios, dbug=texto_debug, contadores=contadores)


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
        # TODO registrar essas ocorrencias de erro ao ler a foto
        pass

    return foto


def eh_aluno(dados):

    """
    Retorna Verdadeiro ou Falso para uma lista de 'dados', a saber:

    dados:
        código da refeição (chave);
        Matrícula do aluno/servidor;
        descrição do Vinculo do aluno/servidor

    """

    is_aluno = False
    if dados['vinculo_item'] == 1:  # ou seja, aluno
        is_aluno = True
    else:
        is_aluno = False

    return is_aluno


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


def registra_compra_subsi(refeicao, matricula, categoria):

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
              db.log_refeicoes.timestamp.date == datetime.today() and
              db.log_refeicoes.fk_tipo_leitura != 1).select()
