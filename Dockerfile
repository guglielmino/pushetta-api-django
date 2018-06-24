FROM python:2.7.15

ENV PYTHONUNBUFFERED 1

RUN adduser --disabled-password --gecos '' pushetta

WORKDIR /usr/src/app

COPY install.txt ./
# pip doesn't follow requirements file order then the following hack
RUN cat install.txt | xargs -n 1 pip install --no-cache-dir
COPY . .

RUN chown -R pushetta /usr/src/app

USER pushetta

EXPOSE 8001

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uwsgi", "--ini", "/usr/src/app/pushetta/pushetta/uwsgi.ini"]
