#!/bin/sh

# Seems to be the only way to change the timezone used by cron
unlink /etc/localtime
ln -s /usr/share/zoneinfo/Europe/Paris /etc/localtime
# Copy root environment variables to root's crontab
printenv > /var/spool/cron/crontabs/root
service cron start

python manage.py collectstatic --noinput

# For the very first deploy of the app, load initial data
if [ "$INITIAL_DEPLOY" = true ]
then
  python manage.py flush --no-input
  python manage.py makemigrations oboo_api
  python manage.py migrate
  python manage.py createsuperuser --noinput
  python manage.py loaddata initial
else
  echo "Skipping loading of initial data because INITIAL_DEPLOY was set to false."
  python manage.py makemigrations oboo_api
  python manage.py migrate
fi

# Adds the cronjob to the crontab and stores the result in the variable below
crontab_add_output=$(python manage.py crontab add)
echo "$crontab_add_output"
# The crontab hash is extracted using this (not so great) hack
cronjob_hash=$(echo "$crontab_add_output" | cut -d '(' -f2 | cut -d ')' -f1)
# We then manually start the cronjob once
echo "Starting cronjob $cronjob_hash..."
python manage.py crontab run "$cronjob_hash"

exec "$@"
