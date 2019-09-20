ARG := $(word 2, $(MAKECMDGOALS) )

activate:
	pyenv local

install:
	pip install -r requirements.txt

compose-services:
	docker-compose up -d db elastic redis mosquitto 

compose-full:
	docker-compose up -d

start:
	python pushetta/manage.py runserver


