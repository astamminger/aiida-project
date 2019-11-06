# -*- coding: utf-8 -*-
from setuptools import setup, find_packages

setup(
    name="aiida-project",
    version="0.0.1",
    author="Andreas Stamminger",
    author_email="stammingera@gmail.com",
    description="Utility for setting up and managing AiiDA projects",
    long_description="",
    keywords="",
    url="",
    packages=find_packages(),
    classifiers=[
        ''
    ],
    install_requires=[
        "pathlib2; python_version<'3.0'",
        "pathlib; python_version>='3.0'",
        "click",
        "click-spinner",
        "pyyaml",
    ],
    extras_require={
        'testing': ['pytest', 'pytest-cov'],
        'develop': ['pre-commit'],
    },
    entry_points={
        'console_scripts': ['aiida-project=aiida_project.cli:main'],
    },
)
