# -*- coding: utf-8 -*-
__author__ = 'carlosfaruolo'


def index():

    form = FORM(T('Matricula'), INPUT(_name='matricula', requires=IS_NOT_EMPTY()), INPUT(_type='submit'))
    desc = None
    foto = URL("static", "images/silhueta.png")

    if form.accepts(request, session):
        response.flash = 'Lido'

        matricula = form.vars['matricula']

        try:
            params = {
                'LMIN': 0,
                'LMAX': 1,
                'MATRICULA': matricula,
            }
            result = api.get('V_PESSOAS_DADOS', params)  # type: unirio.api.result.APIRestultObject
            desc = result.content[0]

            # Por enquanto deixa quieto isso até ver como lidar com a foto vinda do banco.
            # eh_aluno = (desc.descricao_vinculo == 1 or desc.descricao_vinculo == 2)
            # nome_da_tabela_de_foto = 'V_ALU_FOTO' if eh_aluno else 'V_FUNC_FOTO'
            # result = api.get(nome_da_tabela_de_foto, params)
            # if result.content[0]['foto'] is not None:
            #     foto = result.content[0]['foto']

        except:
            response.flash = 'Erro na consulta ao banco de dados'
            pass

    elif form.errors:
        response.flash = 'Erro na leitura'
    else:
        response.flash = 'Insira a matricula'


    return dict(form=form, desc=desc, foto=foto)
