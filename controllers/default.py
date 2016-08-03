# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.subtitle = 'Restaurante Universitário'
    response.flash = T("Hello World")
    return dict(message=T('Welcome to web2py!'))


def ler_horario():
    """registro dos horários das refeições"""
    # TODO: incluir política de nível de acesso
    response.subtitle = 'Nova refeição'
    # record = db.refeicoes(request.args(0)) or redirect(URL('ler_horario'))
    form = SQLFORM(db.refeicoes, submit_button='Salvar',
                   labels={'descricao': 'Descrição', 'hr_inicio':'Hora de Início',
                           'hr_fim': 'Hora do Término', 'preco_total': 'Preço Total',
                           'preco_subsidiado': 'Preço Subsidiado'},
                   separator=': ', upload=URL('download'))

    registros = SQLFORM.grid(db.refeicoes, deletable=True)  #db(db.refeicoes).select()

    if form.process().accepted:
        response.flash ='Cadastrado com sucesso!'
    elif form.errors:
        response.flash ='Há valores inválidos!'

    return dict(form=form, registros=registros)


def download():
    return response.download(request, db)

# TODO: definir leitura das codigos (conforme descrição)

def ler_codigo():
    """leitura dos codigos"""

    form = ''

    return dict(form=form)


# TODO: definir registro do log de refeicoes



def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()

def test():

    return dict()


