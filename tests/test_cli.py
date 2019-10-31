# -*- coding: utf-8 -*-
import sys
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

from aiida_project.cli import create


def test_confirm_directory_delete(click_cli_runner):
    """Check that an existing directory raises a prompt for deletion."""
    result = click_cli_runner.invoke(create, [""])
    assert "Cannot create project folder" in result.output
