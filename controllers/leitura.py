# -*- coding: utf-8 -*-
__author__ = 'carlosfaruolo'


def index():

    form = FORM(T('Matricula'), INPUT(_name='matricula', requires=IS_NOT_EMPTY()), INPUT(_type='submit'))
    desc = None

    if form.accepts(request, session):
        response.flash = 'Lido'

        matricula = form.vars['matricula']
        params = {
            'LMIN': 0,
            'LMAX': 1000,
            'MATRICULA': matricula,
        }

        try:
            result = api.get('V_PESSOAS_DADOS', params)  # type: unirio.api.result.APIRestultObject
            desc = result.content[0]
        except:
            pass

    elif form.errors:
        response.flash = 'Erro na leitura'
    else:
        response.flash = 'Insira a matricula'


    return dict(form=form, desc=desc)
