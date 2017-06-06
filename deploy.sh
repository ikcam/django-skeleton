#!/bin/bash

cd /var/www/myappdir/htdocs/
git pull
chown -hR www-data:www-data *
source env/bin/activate

pip install -U -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput

supervisorctl restart myapp_gunicorn
supervisorctl restart myapp_celery
