# -*- coding: utf-8 -*-
import click


@click.group('aiida-project')
def main():
    """Create and manage AiiDA projects."""
    pass


@main.command('create')
def create():
    """Create a new AiiDA project environment."""
    pass
