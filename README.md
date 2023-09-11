# AWS Micro Services Python

## Directory structure

```
aws-micro-services-python
├──  .github - GitHub related folder, contains workflow for the CI as well as general settings for GitHub
│ ├── workflows - <https://docs.github.com/en/actions/using-workflows>
│ ├── CODEOWNERS - <https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners>
│ ├── dependabot.yml - <https://docs.github.com/en/code-security/dependabot/dependabot-version-updates/configuration-options-for-the-dependabot.yml-file>
│ └── pull_request_template.md - <https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/creating-a-pull-request-template-for-your-repository>
├── infra - Folder contanining all the YAML file to deploy the microservices to AWS using AWS SAM
├── src - Folder containing the source code that will be use by the AWS Lambda runtime
│ ├── libraries - shared libraries used by all the microservices, deployed as lambda layers
│ └── services - microservices folder
├── tests - shared folder for all the tests
│ ├── requirements.txt - separated requirement.txt file to contains only the dependecies needed when running the tests
│ └── conftest.py - <https://docs.pytest.org/en/6.2.x/fixture.html#conftest-py-sharing-fixtures-across-multiple-files>
├── .markdownlint.json - Configuration file for the MarkDown, used by pre-commit
├── .pre-commit-config.yaml - pre-commit hooks config file
├── .prettierrc.json - Configuration file for the JSON and YAML, used by pre-commit
├── Makefile -Make file to ease the local setup, tests, deploy and run CI/CD commands
├── pyproject.toml - File to store the python configuration for black
├── README-DEVELOPMENT.md - Readme file to setup local env
├── README.md - This file
├── requirements-dev.txt - Python requirements to setup the local development environment
├── setup.cfg - The ini file, containing option defaults for setup.py commands
└── setup.py - The setup command
```

### Architecture Diagram of Users Microservice

![Alt Diagram](./docs/diagram.png?raw=true "Architecture Diagram")

Please you can find the SWAGGER documentation of Users Microservice at <https://piuxg04uu7.execute-api.eu-central-1.amazonaws.com/users/docs>.

### Deployment on AWS

Be sure that SAM is installed on your machine, eventually check:

- <https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/prerequisites.html>
- <https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html>

**ATTENTION:** Be sure that a default profile is configured in `~/.aws` or change the `infra\samconfig.toml` configuration to meet you environment.

Navigate to the infra folder and run `sam build` and `sam deploy` command

```bash
cd infra
sam build
sam deploy
```

or use the make command

```bash
make build-deploy
```

### Python Folder Structure and Setup

Each subfolder in `src\libraries` or in `src\services` can be interpreted as a separate python module.
In this way if we decide to move folders around we do not need to change any python code (we still need to change the IaC and the setup for the local virtual environment).

This is due to the fact that every folder contains his own `setup.py` and `requirements.txt` files:

- `setup.py` is needed to make the local virtual environment aware of all these modules, check `requirements-dev.txt`.
- each `requirements.txt` is used by `setup.py` for the `install_requires` argument but also as generic file that any IaC tool to recognize the needed dependencies in the AWS Lambda Runtime.
- all the python code reside into an additional subfolder (e.g. `../micro_aws/micro_aws`), in this way the AWS Lambda runtime and the local virtual environment created using the different `setup.py` will make the imports seamless between the 2 environments.

This works with AWS SAM as shown in this repository but can be used in the same way using AWS CDK or the AWS Lambda TF Module (<https://registry.terraform.io/modules/terraform-aws-modules/lambda/aws/latest>)

#### My consideration on why setuptools and not poetry

- With every `pyproject.toml` comes also a `poetry.lock` in every folder (AWS Lambda or AWS Lambda Layer)
- [Provide ability to read another .toml file instead of pyproject.toml · Issue #4460 · python-poetry/poetry is not considered to work in a multi "module" (our lambdas/layers) env](https://github.com/python-poetry/poetry/issues/4460#issuecomment-909881665)
- AWS SAM do not support it. (but AWS CDK and AWS Lamda TF module do)
