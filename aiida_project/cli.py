# -*- coding: utf-8 -*-
import click


@click.group('aiida-project')
def main():
    """Create and manage AiiDA projects."""
    pass


@main.command()
@click.argument('name', type=str)
@click.option('--manager', type=click.Choice(["conda"]),
              help="Manager to be used for creating the environment")
@click.option('--aiida-version', 'version', type=str,
              help=("AiiDA version to install. This may be either a version "
                    "string if conda is used but also a github url for "
                    "virtualenv or virtualenvwrapper"))
@click.option('--python', type=str, help="The environment's python version")
@click.option('--plugin', 'plugins', multiple=True, type=str,
              help=("One or multiple plugins which will be installed to the "
                    "environment"))
def create(name, manager, version, python, plugins):
    """Create a new AiiDA project environment with name NAME."""
    pass
