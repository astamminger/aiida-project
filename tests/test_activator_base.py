# -*- coding: utf-8 -*-
import sys
import os
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

import pytest

from aiida_project.constants import AIIDA_SUBFOLDER
from aiida_project.activate import ActivateEnvBase


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


def test_correct_aiida_path(project_spec_file):
    """Check that aiida path is returned correctly."""
    base = ActivateEnvBase()
    project_spec_venv = base.load_project_spec('virtualenv_project')
    # this should raise because the folder does not exists
    aiida_path = pathlib.Path.home() / 'virtualenv_project'
    aiida_venv = pathlib.Path.home() / 'virtualenv_project' / AIIDA_SUBFOLDER
    with pytest.raises(Exception) as exception:
        aiida_folder = base.get_aiida_path_from_spec(project_spec_venv)
    assert "Aiida subfolder not found at location" in str(exception.value)
    # and this should succeed
    aiida_venv.mkdir(parents=True)
    loaded_aiida_path = base.get_aiida_path_from_spec(project_spec_venv)
    assert loaded_aiida_path == aiida_path.absolute()


def test_validate_activatable():
    """Check that we only activate if no another project is active"""
    base = ActivateEnvBase()
    # this should succeed
    base.validate_activatable()
    # and these two should raise
    os.environ['AIIDA_PROJECT_ACTIVE'] = 'a_loaded_project'
    with pytest.raises(Exception) as exception:
        base.validate_activatable()
    assert "needs to be deactivated prior to" in str(exception.value)
    os.environ['AIIDA_PROJECT_ACTIVE'] = ''
    os.environ['AIIDA_PATH'] = '/a/test/aiida/path'
    with pytest.raises(Exception) as exception:
        base.validate_activatable()
    assert "AIIDA_PATH is already set" in str(exception.value)
    # reset environment
    os.environ['AIIDA_PROJECT_ACTIVE'] = ''
    os.environ['AIIDA_PATH'] = ''
