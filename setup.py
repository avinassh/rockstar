#!/usr/bin/env python

from setuptools import setup, find_packages

try:
    import pypandoc
    long_description = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError):
    long_description = open('README.md').read()

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

version = '0.5'

setup(
    name='rockstar',
    version=version,
    install_requires=requirements,
    author='Avinash Sajjanshetty',
    author_email='hi@avi.im',
    packages=find_packages(),
    include_package_data=True,
    url='https://github.com/avinassh/rockstar/',
    license='MIT',
    description='Makes you a Rockstar programmer in 2 minutes',
    long_description=long_description,
    entry_points={
        'console_scripts': [
            'rockstar = rockstar:cli',
        ]
    },
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
