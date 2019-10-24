# -*- coding: utf-8 -*-
import click


@click.group('aiida-project')
def main():
    """Create and manage AiiDA projects."""
    pass


@main.command()
@click.argument('name', type=str)
@click.option('--manager', type=click.Choice(["conda", "venv"]),
              default="venv",
              help="Manager to be used for creating the environment")
@click.option('--aiida', 'aiida_core', type=str, default=None,
              help=("AiiDA version to install. This may be either a version "
                    "string if conda is used but also a github url for "
                    "virtualenv or virtualenvwrapper"))
@click.option('--python', 'python_version', type=str, default="3.6",
              help="The environment's python version")
@click.option('--plugin', 'plugins', multiple=True, type=str,
              help=("One or multiple plugins which will be installed to the "
                    "environment"))
@click.option('--pkg', 'pkgs', multiple=True, type=str,
              help=("One or multiple additional packages (i.e. plugins etc.) "
                    "that will be installed to the environment."))
def create(name, manager, aiida_core, python_version, plugins, pkgs):
    """Create a new AiiDA project environment with name NAME."""
    # other packages to be installed, i.e. plugins or auxiliary
    # packages like postgresql etc.
    packages = list(plugins + pkgs)
    # b = EnvBuilder(current_folder, aiida_core, python, packages)
    # b.create_environment()
    print(manager)
    print(aiida_core)
    print(python_version)
    print(packages)
    pass
