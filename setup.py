# -*- coding: utf-8 -*-
from setuptools import setup

setup(
    name="aiida-project",
    version="0.0.0",
    author="Andreas Stamminger",
    author_email="stammingera@gmail.com",
    description="Utility for setting up and managing AiiDA projects",
    long_description="",
    keywords="",
    url="",
    packages=["aiida_project"],
    classifiers=[
        ''
    ],
    install_requires=[
        "pathlib2; python_version<'3.0'",
        "pathlib; python_version>='3.0'",
        "click",
        "click-spinner",
    ],
    extras_require={
        'testing': ['pytest'],
        'develop': ['pre-commit'],
    },
    entry_points={
        'console_scripts': ['aiida-project=aiida_project.cli:main'],
    },
)
