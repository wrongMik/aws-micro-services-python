from setuptools import setup, find_packages

SETUP_OPTIONS = dict(
    name="sqs-users-processor",
    version="0.1.0",
    author="Michele Ugolini",
    description="SQS Processor for Users Service - Running in AWS Lambda",
    packages=find_packages(exclude=["tests"]),
    classifiers=[
        "Programming Language :: Python :: 3.11",
        "Operation System :: OS Independent",
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
    ],
    package_dir={":": "."},
)

setup(**SETUP_OPTIONS)
