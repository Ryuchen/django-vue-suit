#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ==================================================
# @Author : Copyright@Ryuchen
# ==================================================
from io import open
from setuptools import find_packages, setup

REQUIRED_PYTHON = (3, 7)

version_tuple = __import__("vueSuit").VERSION
version = ".".join([str(v) for v in version_tuple])

setup(
    name='vueSuit',
    version=version,
    python_requires='>={}.{}'.format(*REQUIRED_PYTHON),
    description='Create django application comes with lots of goodies easily, '
                'fully extensible with plugin support, '
                'pretty UI based on Ant Design Vue.',
    url='https://ryuchen.github.io',
    author='Ryuchen',
    author_email='chenhaom1993@hotmail.com',
    license=open('LICENSE', encoding='utf-8').read(),
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'django>=2.0'
    ],
    zip_safe=False,
    keywords=['Full Stack', 'Django', 'vueAdmin', 'vuePacks', 'vueForms', 'ant design'],
    classifiers=[
        'Development Status :: 1 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        "Programming Language :: JavaScript",
        'Programming Language :: Python',
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.4",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ]
)
