# -*- coding: utf-8 -*-

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
## File is released under public domain and you can use without limitations
#########################################################################

## if SSL/HTTPS is properly configured and you want all HTTP requests to
## be redirected to HTTPS, uncomment the line below:
# request.requires_https()

## app configuration made easy. Look inside private/appconfig.ini
# from unirio.login import UNIRIOLDAP

from gluon import current
## once in production, remove reload=True to gain full speed
# from unirio.mail import EmailBasico

if not request.env.web2py_runtime_gae:
    ## if NOT running on Google App Engine use SQLite or other DB
    db = DAL(myconf.take('db.uri'), pool_size=myconf.take('db.pool_size', cast=int))

else:
    ## connect to Google BigTable (optional 'google:datastore://namespace')
    db = DAL('google:datastore+ndb')
    ## store sessions and tickets there
    session.connect(request, response, db=db)
    ## or store session in Memcache, Redis, etc.
    ## from gluon.contrib.memdb import MEMDB
    ## from google.appengine.api.memcache import Client
    ## session.connect(request, response, db = MEMDB(Client()))

## by default give a view/generic.extension to all actions from localhost
## none otherwise. a pattern can be 'controller/function.extension'
response.generic_patterns = ['*'] if request.is_local else []
## choose a style for forms
response.formstyle = myconf.take('forms.formstyle')  # or 'bootstrap3_stacked' or 'bootstrap2' or other
response.form_label_separator = myconf.take('forms.separator')


## (optional) optimize handling of static files
# response.optimize_css = 'concat,minify,inline'
# response.optimize_js = 'concat,minify,inline'
## (optional) static assets folder versioning
# response.static_version = '0.0.0'


from gluon.tools import Auth, Service, PluginManager

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

## configure email
mail = auth.settings.mailer
mail.settings.server = 'logging' if request.is_local else myconf.take('smtp.server')
mail.settings.sender = myconf.take('smtp.sender')
mail.settings.login = myconf.take('smtp.login')


# current.mailer = EmailBasico(mail, response.render)



## configure auth policy
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.settings.reset_password_requires_verification = True

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################


# todo remover essa definicao de db (existe uma la em cima do codigo que pega essa url de myconf (appconfig.ini)
db = DAL('postgres://postgres:devdtic2@teste.sistemas.unirio.br/restaurante', fake_migrate_all=True)

db.define_table('refeicoes',
                Field('descricao', 'string', length=100, label='Descrição'),
                Field('hr_inicio', 'time', label='Início'),
                Field('hr_fim', 'time', label='Termino'),
                Field('preco_total', 'decimal(10,2)', label='Preço Normal'),
                Field('preco_subsidiado', 'decimal(10,2)', label='Preço Subsidiado')
                )

db.define_table('tipo_leitura',
                Field('descricao', 'string', requires=IS_IN_SET(['Lido', 'Pagamento Total', 'Pagamento Subsidiado'])))

db.define_table('log_refeicoes',
                Field('fk_refeicao', 'reference refeicoes'),  # Chave estrangeira: id/refeicoes
                Field('fk_tipo_leitura', 'reference tipo_leitura'),  # Chave estrangeira: id/tipo_leitura
                Field('timestamp', 'datetime', default=request.now),
                Field('categoria', 'string', length=100),
                Field('matricula', 'string', length=100))

# TODO: definir validadores
db.refeicoes.descricao.requires = IS_NOT_IN_DB(db, 'refeicoes.descricao')
db.refeicoes.hr_inicio.requires = IS_TIME(error_message='Formato de hora: HH:MM')
db.refeicoes.hr_fim.requires = IS_NOT_EMPTY()
db.refeicoes.hr_fim.requires = IS_TIME(error_message='Formato de hora: HH:MM')
db.refeicoes.preco_total.represent = db.refeicoes.preco_subsidiado.represent = lambda value, row: DIV('R$ %.2f' % ('VAZIO' if value == None else value))
#db.refeicoes.preco_total.requiquires = IS_? validador de moeda?
# db.tipo_leitura.requires.descricao = IS_NOT_EMPTY()

## after defining tables, uncomment below to enable auditing
# auth.enable_record_versioning(db)
