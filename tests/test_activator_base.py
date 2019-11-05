# -*- coding: utf-8 -*-
import sys
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

import pytest

from aiida_project.activate_env import ActivateEnvBase


def test_load_project_spec(project_spec_file):
    """Test loading of project specs in activators."""
    base = ActivateEnvBase()
    # check loading succeeds
    project_spec = base.load_project_spec('conda_project')
    project_spec = base.load_project_spec('virtualenv_project')
    # check loading failes for unkown environment
    with pytest.raises(Exception) as exception:
        project_spec = base.load_project_spec('fantasy_project')
    assert "Unable to complete activation" in str(exception.value)
