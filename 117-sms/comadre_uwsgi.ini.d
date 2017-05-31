[uwsgi]
#application's base folder
chdir = /data/webserver/www/dml_comadre/117-sms/marketing_notifications_python
application = app
uid = nginx
gid = nginx
master = true
processes = 4

#python module to import
app = app
module = wsgi:manage
plugin = python

virtualenv = /data/webserver/www/dml_comadre/117-sms/venv
pythonpath = %(chdir)

#socket file's location
socket = /data/webserver/www/dml_comadre/117-sms/comadre_uwsgi.sock

#permissions for the socket file
chmod-socket    = 644

#the variable that holds a flask application inside the module imported at line #6
callable = app

die-on-term = true

#location of log files
logto = /var/log/uwsgi/%n.log
