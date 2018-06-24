#!/usr/bin/env sh

set -e

if [ "x$DJANGO_MANAGEPY_MIGRATE" = 'xon' ]; then
    python pushetta/manage.py migrate --noinput
fi

if [ "x$DJANGO_MANAGEPY_COLLECTSTATIC" = 'xon' ]; then
    python pushetta/manage.py collectstatic --noinput
fi

exec "$@"