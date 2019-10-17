FROM python:2.7.15-alpine3.6

ENV PYTHONUNBUFFERED 1

RUN set -e; \
    apk add --no-cache --virtual .build-deps  \
    gcc \
    libc-dev \
    linux-headers \
    mariadb-dev \
    libffi-dev \
    libxml2-dev

RUN adduser -D -g '' pushetta

WORKDIR /usr/src/app

COPY requirements.txt ./
# pip doesn't follow requirements file order then the following hack
RUN cat requirements.txt | xargs -n 1 pip install --no-cache-dir
COPY . .
COPY dev_static/ static/

RUN chown -R pushetta /usr/src/app

#USER pushetta

EXPOSE 8001

ENTRYPOINT ["/usr/src/app/docker-entrypoint.sh"]
CMD ["uwsgi", "--ini", "/usr/src/app/pushetta/pushetta/uwsgi.ini"]

