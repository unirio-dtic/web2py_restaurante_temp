# -*- coding: utf-8 -*-
__author__ = 'carlosfaruolo'


def index():

    form = FORM(T('Matricula'), INPUT(_name='matricula', requires=IS_NOT_EMPTY()), INPUT(_type='submit'))
    descricao = None
    url_foto = URL("static", "images/silhueta.png")

    # aqui virao coisas do form
    if form.accepts(request, session):
        response.flash = 'Lido'

        matricula = form.vars['matricula']

        try:
            params = {'MATRICULA': matricula}
            result = api.get('V_PESSOAS_DADOS', params)
            descricao = result.content[0]

            eh_aluno = (descricao['descricao_vinculo'] == 1 or descricao['descricao_vinculo'] == 2)

            try:
                params = {'MATRICULA': matricula}
                result = api.get('V_ALU_FOTO' if eh_aluno else 'V_FUNC_FOTO', params)
                if result.content[0]['foto'] is not None:
                    url_foto = 'data:image/jpeg;base64,' + result.content[0]['foto']
            except:
                response.flash = 'Foto não disponível'

        except:
            response.flash = 'Erro na consulta ao banco de dados'
            pass

    # aqui caso ocorreu xabu
    elif form.errors:
        response.flash = 'Erro na leitura'

    # mensagem ao entrar. podemos tirar isso tambem
    else:
        response.flash = 'Insira a matricula'


    return dict(form=form, desc=descricao, foto=url_foto)
