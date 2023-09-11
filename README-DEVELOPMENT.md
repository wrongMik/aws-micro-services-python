# Developer Readme

## Setup for development

### Python Development Setup

Be sure that you are running on Python Version 3.11, eventually check:

- <https://pypi.org/project/pyenv-win/#installation> for Windows
- <https://github.com/pyenv/pyenv> for Linux/Mac

make sure that you had install pip

```bash
pip install --upgrade pip setuptools wheel
```

Create a new python environment and activate it:

1. On Mac/Linux use pyenv-virtualenv (<https://github.com/pyenv/pyenv-virtualenv>)

```bash
pyenv virtualenv 3.11.5 aws-micro-python
pyenv activate aws-micro-python
```

2. On Windows using virtualenv and virtualenvwrapper (<https://github.com/davidmarble/virtualenvwrapper-win/>)

```bash
pip install virtualenv
pip install virtualenvwrapper-win
cd <project>
mkvirtualenv -p3.11.5 aws-micro-python
%USERPROFILE%/Envs/aws-micro-python/Scripts/activate.bat
```

3. Using Python venv

```bash
python -m venv .venv
source .venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### Install Pre-commit Hooks

Install pre-commit and register the hooks

```bash
$ pre-commit install
pre-commit installed at .git\hooks\pre-commit
$ pre-commit install --hook-type pre-commit
pre-commit installed at .git\hooks\pre-commit
```

This hook will run the configuration stored in `.pre-commit-config.yaml` file on the pre-commit event,if you want you can also run manually the pre-commit hooks with:

```bash
pre-commit run --all-files
```

### Formatting

The configuration for formatting are set in the `setup.cfg` and in the `pyproject.toml` file

```bash
make python-format
```

### Linting and Static Type Checking

The configuration for linting are set in the `setup.cfg` file

```bash
make python-lint
```

### Testing

The configuration for testing are set in the `setup.cfg` file, you can run

```bash
pytest
```

or if you want to run it concurrently, generate the report in XML and show the coverage

```bash
make python-tests
```
