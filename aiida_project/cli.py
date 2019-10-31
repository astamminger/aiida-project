# -*- coding: utf-8 -*-


import sys
import shutil
import re
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
    Create a new AiiDA project environment.

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


@main.command()
@click.argument('name', type=str)
def delete(name):
    """
    Delete an existing AiiDA project environment.

    Removes the AiiDA project environment with given NAME from the
    list of managed environments and deletes the environment folder.

    Note:

    This action will **permanently** delete all data contained in the
    project folder including databases, repositories and configs.
    """
    print("Delete")

#
# using activate / deactivate we communicate with the calling shell by
# printing the commands to stdout, i.e we need to disable all unwanted
# messages to not confuse the shell
#
@main.command(hidden=True, add_help_option=False)
@click.argument('args', nargs=-1)
@click.option('--profile', 'profile', default='default_profile',
              show_default=True,
              help="AiiDA profile to load for the project environment.")
@click.option('--help', '_help', is_flag=True,
              help="Show this message and exit.")
@click.pass_context
def activate(ctx, args, _help, profile):
    """
    Activate an AiiDA project environment.
    """
    # we expect two arguments: shell-type and environment name
    if _help or len(args) != 2:
        help_txt = ctx.command.get_help(ctx).replace("[ARGS]...", "env_name")
        print("echo \"{}\"".format(help_txt))
    else:
        print("echo This will be sourced")
        print("export AIIDA_PATH=/home/andreas/.aiida")


@main.command(hidden=True, add_help_option=False)
@click.argument('args', nargs=-1)
@click.option('--help', '_help', is_flag=True,
              help=("Show this message and exit."))
@click.pass_context
def deactivate(ctx, args, _help):
    """
    Deactivate a loaded AiiDA project environment.
    """
    # we expect one argument: shell-type and environment name
    if _help or len(args) != 1:
        help_txt = ctx.command.get_help(ctx).replace("[ARGS]...", "env_name")
        print("echo \"{}\"".format(help_txt))
    else:
        print("echo This will be sourced")
        print("unset AIIDA_PATH")
