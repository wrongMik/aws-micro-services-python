from setuptools import setup, find_packages

SETUP_OPTIONS = dict(
    name='simpler-fast-api',
    version='0.1.0',
    author='Nordcloud',
    description='Simpler Fast API - Service',
    packages=find_packages(exclude=['tests']),
    classifiers=[
        'Programming Language :: Python :: 3.11',
        'Operation System :: OS Independent',
        'Development Status :: 1 - Planning',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
    ],
    package_dir={':': '.'},
    install_requires=open('requirements.txt').read().splitlines(),
)

setup(**SETUP_OPTIONS)
