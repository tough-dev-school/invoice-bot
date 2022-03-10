install-dev-deps: dev-deps
	pip-sync requirements.txt dev-requirements.txt

install-deps: deps
	pip-sync requirements.txt

deps:
	pip-compile requirements.in

dev-deps: deps
	pip-compile dev-requirements.in

lint:
	flake8 src
	cd src && mypy

dev:
	watchmedo auto-restart --directory . --patterns '*.py' --recursive -- python -m src.bot
