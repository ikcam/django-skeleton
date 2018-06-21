#!/bin/bash

APP_ENV="production"
NAME="matrix"
DOMAIN=matrix.cubo.pe
PROJECTDIR=/var/www/$DOMAIN
DJANGODIR=$PROJECTDIR/htdocs

# Create Project dir
if [ ! -d $PROJECTDIR ]; then
  ee site create $DOMAIN --mysql
fi

# Go to project folder
cd $DJANGODIR

# Creating virtualenv
if [ ! -d ~/.pyenv/version/$NAME ]; then
  pyenv virtualenv 3.6.1 $NAME
  pyenv local $NAME
fi

if [ ! -f env ]; then
  ln -s ~/.pyenv/versions/$NAME $DJANGODIR/env
fi

# Update NGINX
rm -rf /etc/nginx/sites-available/$DOMAIN.conf
cp $DJANGODIR/nginx.conf /etc/nginx/sites-available/$DOMAIN

# Update supervisor files
if [ -f /etc/supervisor/conf.d/$NAME.conf ]; then
  rm -rf /etc/supervisor/conf.d/$NAME.conf
fi
ln -s $DJANGODIR/supervisor.conf /etc/supervisor/conf.d/$NAME.conf

if [ ! -d $PROJECTDIR/run ]; then
  mkdir $PROJECTDIR/run
fi

export APP_ENV

git pull
chown -hR www-data:www-data *

source env/bin/activate

pip install -U -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput
python manage.py compilemessages --locale=es

bower install --allow-root

supervisorctl reread
supervisorctl update
supervisorctl restart matrix_gunicorn
supervisorctl restart matrix_celery
supervisorctl restart matrix_beat

# To enable access to Celery Flower
chmod 777 $PROJECTDIR/run/flower.sock
