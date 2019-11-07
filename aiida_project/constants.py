# -*- coding: utf-8 -*-


import sys


"""
Constants used throughout the project
"""


ON_WIN = bool(sys.platform == "win32")

# default project subdirectories
DEFAULT_SRC_SUBFOLDER = "src"
DEFAULT_ENV_SUBFOLDER = "env"
AIIDA_SUBFOLDER = ".aiida"

# configuration file
CONFIG_FOLDER = ".aiida_project"
PROJECTS_FILE = ".projects.yaml"

# define internal names for package managers
MANAGER_NAME_CONDA = 'conda'
MANAGER_NAME_VENV = 'virtualenv'

# define internal names for shells
SHELL_NAME_BASH = 'bash'

# compatible shells
if ON_WIN:
    SUPPORTED_SHELLS = [
        SHELL_NAME_BASH,
    ]
else:
    SUPPORTED_SHELLS = [
        SHELL_NAME_BASH,
    ]

# compatible environment managers
SUPPORTED_MANAGERS = [
    MANAGER_NAME_CONDA,
    MANAGER_NAME_VENV,
]
