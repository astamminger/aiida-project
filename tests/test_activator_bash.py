# -*- coding: utf-8 -*-
import sys
import os
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

import pytest

from aiida_project.activate import ActivateEnvBash
from aiida_project.constants import AIIDA_SUBFOLDER


def test_conda_activation(project_spec_file, fake_popen):
    """Test environment activation for conda environment manager."""
    # setup fake Popen
    fake_popen.set_cmd_attrs('conda', returncode=0)
    # physically setup all folders and initialize activator class
    base_path = project_spec_file['conda_project']['project_path']
    pathlib.Path(base_path).mkdir()
    pathlib.Path(project_spec_file['conda_project']['env_sub']).mkdir()
    pathlib.Path(project_spec_file['conda_project']['src_sub']).mkdir()
    aiida_path = pathlib.Path(base_path) / AIIDA_SUBFOLDER
    aiida_path.mkdir()
    bash = ActivateEnvBash('conda', 'conda_project')
    # check activation
    activate_command = bash.execute('activate')
    activate_wanted = ("export AIIDA_PATH='{}';export AIIDA_PROJECT_ACTIVE="
                       "'{}';conda activate {};eval \"$(verdi "
                       "completioncommand)\""
                       .format(base_path, 'conda_project', 'conda_project'))
    assert activate_command == activate_wanted
    # check deactivation (need to set environment variable otherwise
    # deactivate will expectedly fail
    os.environ['AIIDA_PROJECT_ACTIVE'] = 'conda_project'
    deactivate_command = bash.execute('deactivate')
    deactivate_wanted = ("unset AIIDA_PATH;unset AIIDA_PROJECT_ACTIVE;"
                         "conda deactivate;complete -r verdi")
    assert deactivate_command == deactivate_wanted
    # finally check that a missing conda exectuable results in a
    # meaningful error message
    fake_popen.set_cmd_attrs('conda', returncode=1)
    with pytest.raises(Exception) as exception:
        bash = ActivateEnvBash('conda', 'conda_project')
    assert "conda does not seem to be available" in str(exception.value)
    # reset environment
    os.environ['AIIDA_PROJECT_ACTIVE'] = ''


def test_venv_activation(project_spec_file, fake_popen):
    """Test environment activation for conda environment manager."""
    # setup fake Popen
    fake_popen.set_cmd_attrs('virtualenv', returncode=0)
    # physically setup all folders and initialize activator class
    base_path = project_spec_file['virtualenv_project']['project_path']
    env_path = project_spec_file['virtualenv_project']['env_sub']
    pathlib.Path(base_path).mkdir()
    pathlib.Path(env_path).mkdir()
    pathlib.Path(project_spec_file['virtualenv_project']['src_sub']).mkdir()
    aiida_path = pathlib.Path(base_path) / AIIDA_SUBFOLDER
    aiida_path.mkdir()
    # and we also need the activation file
    env_bin_folder = pathlib.Path(env_path) / 'bin'
    env_bin_folder.mkdir()
    activation_file = env_bin_folder / 'activate'
    activation_file.touch()
    bash = ActivateEnvBash('virtualenv', 'virtualenv_project')
    # check activation
    activate_command = bash.execute('activate')
    activate_wanted = ("export AIIDA_PATH='{}';export AIIDA_PROJECT_ACTIVE="
                       "'{}';. '{}';eval \"$(verdi completioncommand)\""
                       .format(base_path, 'virtualenv_project',
                               activation_file))
    assert activate_command == activate_wanted
    os.environ['AIIDA_PROJECT_ACTIVE'] = 'virtualenv_project'
    deactivate_command = bash.execute('deactivate')
    deactivate_wanted = ("unset AIIDA_PATH;unset AIIDA_PROJECT_ACTIVE;"
                         "deactivate;complete -r verdi")
    assert deactivate_command == deactivate_wanted
    # finally check that a missing activation file results in a
    # meaningful error message
    activation_file.unlink()
    with pytest.raises(Exception) as exception:
        bash = ActivateEnvBash('virtualenv', 'virtualenv_project')
    assert "No activation script found at location" in str(exception.value)
    # reset environment
    os.environ['AIIDA_PROJECT_ACTIVE'] = ''
