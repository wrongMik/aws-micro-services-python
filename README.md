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

### Deployment on AWS

Be sure that SAM is installed on your machine, eventually check:

- <https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/prerequisites.html>
- <https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html>

Be sure that a default profile is configured in `~/.aws` or change the `SAM` configuration to meet you environment.

Navigate to the infra folder and run `sam build` and `sam deploy` command

```bash
cd infra
sam build
sam deploy
```
