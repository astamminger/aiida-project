# -*- coding: utf-8 -*-


import sys
import shutil
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

import click

from aiida_project.create_env import get_env_creator


@click.group('aiida-project')
def main():
    """Create and manage AiiDA projects."""
    pass


@main.command()
@click.argument('name', type=str)
@click.option('--manager', type=click.Choice(["conda", "virtualenv"]),
              default="virtualenv",
              help="Package manager to be used for creating the environment")
@click.option('--aiida', 'aiida_core', type=str,
              help=("AiiDA version to install. This may be either a version "
                    "string, if conda is used, but can also point to a source "
                    "if virtualenv is used as package manager"))
@click.option('--python', 'python_version', type=str, default="3.6",
              help="The environments python version")
@click.option('--utility-pkg', 'packages', multiple=True, type=str,
              help=("One or multiple additional packages (i.e. plugins etc.) "
                    "that will be installed to the environment. Packages "
                    "need to be defined in a form understood by the used "
                    "package manager (i.e. package=1.0 for conda and "
                    "package==1.0[extras] / source for virtualenv)."))
@click.option('--path', 'path', type=click.Path(exists=True),
              default=pathlib.Path.cwd().absolute(),
              help=("Alternative location for the environment folder "
                    "(Default installation path is the current working "
                    "directory)"))
def create(name, manager, aiida_core, python_version, packages, path):
    """
    Create a new AiiDA project environment named NAME.

    Initializes a new folder named NAME containing an `.aiida` folder at the
    location given by path and creates a new python environment running
    the defined AiiDA version.

    Note:

    The conda package manager is only capable of installing packages available
    on the official anaconda repositories. In case you're planning to
    install source packages or packages not available on the anaconda repos
    please use the virtualenv package manager which also allows the
    installation directly from source and package extras. A source definition
    is expected to be of the form <username>/<repository>:<branch> or
    <username>/<repository>:<branch>[extras] which will also install the
    defined extras.
    """
    # first check if the project folder exists already
    project_folder = path / name
    if project_folder.exists():
        msg = ("Cannot create project folder '{}' because it already exists! "
               "Delete?".format(project_folder))
        delete = click.confirm(msg)
        if delete:
            shutil.rmtree(project_folder)
        else:
            sys.exit(1)
    # fetch and setup the chosen environment manager
    EnvCreator = get_env_creator(manager)
    creator = EnvCreator(proj_name=name, proj_path=pathlib.Path(path),
                         python_version=python_version,
                         aiida_version=aiida_core, packages=list(packages))
    creator.create_aiida_project_environment()
