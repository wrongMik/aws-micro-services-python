.PHONY: help

.DEFAULT_GOAL := help

export PATH := ${HOME}/.local/bin:$(PATH)

# Microservice Specific variables
project-name = aws-micro-python
pre-commit-version = 3.4.0
python-version = 3.11.5

help:
	@echo ###############################################################################
	@echo #   Commands for Development and CI                                           #
	@echo ###############################################################################
	@echo "pre-commit-standalone" - install pre-commit hooks only
	@echo "python" - install python version with pyenv, activate pyenv virtualenv, install dependencies (including dev), install pre-commit hooks
	@echo "python-win" - install python version with pyenv, activate virtualenv with virtualenvwrapper-win, install dependencies (including dev), install pre-commit hooks
	@echo "python-clean" - Remove or delete all the python files used for build or cache
	@echo "python-format" - run configured formatter
	@echo "python-lint" - run flake8 and mypy
	@echo "python-tests" - run the tests with pytest
	@echo "python-ci" - run python-format, python-lint and python-tests

pre-commit-install:
	pre-commit install
	pre-commit install --hook-type pre-commit

pip-install-pre-commit:
	pip install -U pre-commit==$(pre-commit-version)

pre-commit-standalone: pip-install-pre-commit pre-commit-install

run-pre-commit-all:
	pre-commit run --all-files

pyenv-install-python:
	pyenv install $(python-version)

pip-install-base:
	pip install -U pip setuptools wheel

pyenv-virtual-env-activate:
	pyenv virtualenv $(python-version) $(project-name)
	pyenv activate $(project-name)
	pyenv local $(project-name)

virtualenvwrapper-win-activate:
	pip install virtualenv virtualenvwrapper-win
	mkvirtualenv -p$(python-version) $(project-name)
	%USERPROFILE%/Envs/$(project-name)/Scripts/activate.bat

install-requirements-dev:
	pip install -r requirements-dev.txt

python: pyenv-install-python pip-install-base pyenv-virtual-env-activate install-requirements-dev pre-commit-install

python-win: pyenv-install-python pip-install-base virtualenvwrapper-win-activate install-requirements-dev pre-commit-install

clean-build:
	rm -fr **/build/
	rm -fr **/dist/
	rm -fr **/*.egg-info
	rm -fr **/*.spec
	rm -fr .pytest_cache
	rm -fr .mypy_cache

clean-pyc:
	find . -name '**.log*' -delete
	find . -name '**_cache' -exec rm -rf {} +
	find . -name '**.egg-info' -exec rm -rf {} +
	find . -name '**.pyc' -exec rm -f {} +
	find . -name '**.pyo' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -rf {} +

python-clean: clean-build clean-pyc

python-format:
	autoflake --remove-all-unused-imports --remove-unused-variables -ir .
	isort --settings-path setup.cfg .
	black --config pyproject.toml .

python-lint:
	flake8 --config setup.cfg .
	mypy .

python-tests:
	pytest --color=yes -n 8 -rAfv --log-level=WARNING --cov=. --cov-report=xml --show-capture=no

python-ci: python-format python-lint python-tests
