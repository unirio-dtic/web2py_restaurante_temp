# -*- coding: utf-8 -*-
__author__ = 'carlosfaruolo'


def index():
    """Definindo valores de exibição"""
    # definindo qual refeição está sendo servida
    response.meta.time = request.now
    refeicao = db(db.refeicoes.hr_fim >= response.meta.time).select()

    response.title = 'RESTAURANTE UNIVERSITÁRIO - UNIRIO'
    response.subtitle = 'Controle de refeições - ' + str(refeicao[0].descricao).upper()

    form = FORM(T('Matrícula: '),
                INPUT(_name='matricula', requires=IS_NOT_EMPTY()),
                INPUT(_type='submit'),
                BR())
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

            params = {'MATRICULA': matricula}
            result = api.get('V_ALU_FOTO' if eh_aluno else 'V_FUNC_FOTO', params)
            if result.content[0]['foto'] is not None:
                url_foto = 'data:image/jpeg;base64,' + result.content[0]['foto']

        except:
            response.flash = 'Erro na consulta ao banco de dados'
            pass

    # aqui caso ocorreu xabu
    elif form.errors:
        response.flash = 'Erro na leitura'

    # mensagem ao entrar. podemos tirar isso tambem
    else:
        response.flash = 'Insira a matrícula'

    texto = ''
    listar_botoes = []
    botoes = []
    for row in db(db.refeicoes.descricao != '').select():
        texto += ' %s, ' % str(row['descricao'])
        botoes.append(TAG.button(row['descricao'], _type='button', _='disable'))
    form2 = SQLFORM.factory(db=None, buttons=botoes)

    return dict(form=form, desc=descricao, foto=url_foto, refeicao=refeicao, dbug=texto, form2=form2)
