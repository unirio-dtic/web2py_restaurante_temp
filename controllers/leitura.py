# -*- coding: utf-8 -*-
__author__ = 'carlosfaruolo'

from datetime import timedelta


def index():

    form = FORM(T('Matricula'), INPUT(_name='matricula', requires=IS_NOT_EMPTY()), INPUT(_type='submit'))
    descricao = None
    src_foto = URL("static", "images/silhueta.png")

    # aqui virao coisas do form
    if form.accepts(request, session):
        response.flash = 'Lido'
        try:
            descricao = busca_por_matricula(form.vars['matricula'])

            try:
                foto = busca_foto_por_matricula(form.vars['matricula'], descricao['descricao_vinculo'])
                if foto is not None:
                    src_foto = foto
                else:
                    response.flash = 'Foto não disponível'

            except:
                response.flash = 'Erro ao consultar a foto'

        except:
            response.flash = 'Erro na consulta ao banco de dados'

    # aqui caso ocorreu xabu
    elif form.errors:
        response.flash = 'Erro na leitura'

    # mensagem ao entrar. podemos tirar isso tambem
    else:
        response.flash = 'Insira a matricula'


    return dict(form=form, desc=descricao, foto=src_foto)


def busca_por_matricula(matricula):

    params = {'MATRICULA': matricula}
    result = api.get('V_PESSOAS_DADOS', params)
    return result.content[0]


def busca_foto_por_matricula(matricula, vinculo_id):
    tabela = None
    foto = None

    if vinculo_id is 1 or 2:  # ou seja, aluno
        tabela = 'V_ALU_FOTO'
    else:
        tabela = 'V_FUNC_FOTO'

    result = api.get(tabela, {'MATRICULA': matricula})
    if result.content[0]['foto'] is not None:
        foto = 'data:image/jpeg;base64,' + result.content[0]['foto']

    return foto


def registra_leitura(refeicao, matricula, categoria):
    params = {
        'fk_refeicao': refeicao,
        'fk_tipo_leitura': 1,
        'timestamp': datetime(),
        'categoria': categoria,
        'matricula': matricula
    }

