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

# compatible shells
if ON_WIN:
    COMPATIBLE_SHELLS = [
        'bash',
    ]
else:
    COMPATIBLE_SHELLS = [
        'bash',
    ]
