# -*- coding: utf-8 -*-
# from unirio.login import UNIRIOLDAP
from datetime import datetime
from gluon.tools import Auth, Service, PluginManager
from gluon import current

db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int))
current.db = db

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')

auth = Auth(db)
service = Service()
plugins = PluginManager()

## create all tables needed by auth if not custom tables
auth.define_tables(username=True, signature=False)
auth.settings.actions_disabled = [
    'register',
    'retrieve_username',
    'profile',
    'lost_password',
    'request_reset_password',
    'change_password'
]

db.auth_user.username.label = 'CPF'

# from gluon.contrib.login_methods.ldap_auth import ldap_auth
# auth.settings.login_methods = [ldap_auth(mode='uid', server=UNIRIOLDAP.LDAP_TESTE, base_dn='ou=people,dc=unirio,dc=br')]
# auth.settings.login_onaccept.append(login_helper.adiciona_info_pessoa_logada)

## configure auth policy
# auth.settings.registration_requires_verification = False
# auth.settings.registration_requires_approval = False
# auth.settings.reset_password_requires_verification = True

db.define_table('refeicoes',
                Field('descricao', 'string', label='Descrição'),
                Field('hr_inicio', 'time', label='Início'),
                Field('hr_fim', 'time', label='Termino'),
                Field('preco_total', 'decimal(10,2)', label='Preço Normal'),
                Field('preco_subsidiado', 'decimal(10,2)', label='Preço Subsidiado')
                )

db.define_table('tipo_leitura',
                Field('descricao', 'string')
                )

db.define_table('log_refeicoes',
                Field('fk_refeicao', 'reference refeicoes', label='Refeição'),  # Chave estrangeira: id/refeicoes
                Field('fk_tipo_leitura', 'reference tipo_leitura', label='Operação'),  # Chave estrangeira: id/tipo_leitura
                Field('timestamp', 'datetime', default=datetime.now(), label='Hora do registro'),  # todo substituir request por datetime
                Field('categoria', 'string'),
                Field('matricula', 'string')
                )

# TODO: definir validadores
db.refeicoes.descricao.requires = IS_NOT_IN_DB(db, 'refeicoes.descricao')
db.refeicoes.hr_inicio.requires = IS_TIME(error_message='Formato de hora: HH:MM')
db.refeicoes.hr_fim.requires = IS_NOT_EMPTY()
db.refeicoes.hr_fim.requires = IS_TIME(error_message='Formato de hora: HH:MM')
db.refeicoes.preco_total.represent = db.refeicoes.preco_subsidiado.represent = \
    lambda value, row: DIV('R$ %.2f' % (0 if value is None else value))

db.log_refeicoes.fk_refeicao.represent = lambda value, row: db(db.refeicoes.id == value).select()[0].descricao
db.log_refeicoes.fk_tipo_leitura.represent = lambda value, row: db(db.tipo_leitura.id == value).select()[0].descricao
# db.tipo_leitura.requires.descricao = IS_NOT_EMPTY()

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
