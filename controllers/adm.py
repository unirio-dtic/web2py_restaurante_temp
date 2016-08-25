# -*- coding: utf-8 -*-


@auth.requires_membership(role='admin')
def horario():

    """registro dos horários das refeições"""

    response.subtitle = 'Nova refeição'

    # record = db.refeicoes(request.args(0)) or redirect(URL('ler_horario'))
    form = SQLFORM(db.refeicoes, submit_button='Salvar',
                   labels={'descricao': 'Descrição', 'hr_inicio':'Hora de Início',
                           'hr_fim': 'Hora do Término', 'preco_total': 'Preço Total',
                           'preco_subsidiado': 'Preço Subsidiado'},
                   separator=': ', upload=URL('download'))

    registros = SQLFORM.grid(db.refeicoes, deletable=True)  # db(db.refeicoes).select()

    if form.process().accepted:
        response.flash = 'Cadastrado com sucesso!'
    elif form.errors:
        response.flash = 'Há valores inválidos!'

    return dict(form=form, registros=registros)


@auth.requires_membership(role='admin')
def log_refeicoes():

    """Mostrar quantas refeições foram servidas no dia"""
    response.title = 'RESTAURANTE UNIVERSITÁRIO'
    response.subtitle = 'Relatório de registros'

    form = SQLFORM.grid(db.log_refeicoes)
    """for row in db(db.refeicoes.descricao != '').select():
        form.append(db.refeicoes.descricao)"""

    return dict(form=form)


@auth.requires_membership(role='admin')
def tipo_leitura():
    """

    Exibe: tipos de leitura

    """
    response.title = 'RESTAURANTE UNIVERSITÁRIO'
    response.subtitle = 'Tipos de Leitura'

    form = SQLFORM.grid(db.tipo_leitura)

    return dict(form=form)


@auth.requires_membership(role='admin')
def refeicoes():
    """

    Exibe: refeições Cadastradas

    """
    response.title = 'RESTAURANTE UNIVERSITÁRIO'
    response.subtitle = 'Refeições cadastradas'

    form = SQLFORM.smartgrid(db.refeicoes)

    return dict(form=form)
