# -*- coding: utf-8 -*-
import pytest
import sys
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

from aiida_project.create_env import CreateEnvVirtualenv
from aiida_project import constants
from aiida_project import utils


def test_python_version(valid_env_input):
    """Test python flag is created correctly."""
    valid_env_input['python_version'] = '123.456'
    env_creator = CreateEnvVirtualenv(**valid_env_input)
    wanted_python_flag = "--python=python123.456"
    assert wanted_python_flag in env_creator.env_flags


def test_aiida_version(valid_env_input):
    """Test aiida package definition is correct."""
    # index package
    valid_env_input['aiida_version'] = "1.2.3b56"
    env_creator = CreateEnvVirtualenv(**valid_env_input)
    wanted_format = "aiida-core==1.2.3b56"
    assert wanted_format in env_creator.pkg_arguments
    # index package with extras
    valid_env_input['aiida_version'] = "1.2.3b56[extras]"
    env_creator = CreateEnvVirtualenv(**valid_env_input)
    wanted_format = "aiida-core==1.2.3b56[extras]"
    assert wanted_format in env_creator.pkg_arguments
    # source package
    valid_env_input['aiida_version'] = 'aiidateam/aiida-core:develop'
    env_creator = CreateEnvVirtualenv(**valid_env_input)
    wanted_format = "aiidateam/aiida-core:develop"
    assert wanted_format in env_creator.pkg_arguments
    # source package with extrs
    valid_env_input['aiida_version'] = 'aiidateam/aiida-core:develop[extra]'
    env_creator = CreateEnvVirtualenv(**valid_env_input)
    print(env_creator.__dict__)
    wanted_format = "aiidateam/aiida-core:develop[extra]"
    assert wanted_format in env_creator.pkg_arguments


def test_create_project_environment_success(temporary_folder, temporary_home,
                                            fake_popen):
    """Test full cycle for creating an environment from conda."""
    # make sure we write to the correct directory
    assert pathlib.Path.home() == temporary_folder
    arguments = {
        'proj_name': 'venv_project',
        'proj_path': pathlib.Path(temporary_folder),
        'python_version': '0.0',
        'aiida_version': '0.0.0',
        'packages': ['aiida-vasp[extras1]', 'pymatgen==2019.3.13',
                     'aiidateam/aiida-ase:devel[extras1]']
    }
    creator = CreateEnvVirtualenv(**arguments)
    fake_popen.returncode = 0
    creator.create_aiida_project_environment()
    base_folder = str((creator.env_folder / creator.proj_name).absolute())
    src_folder = creator.src_folder.absolute()
    expected_cmd_order = [
        "virtualenv --version",
        "git --version",
        # !!! There are 2 empty spaces expected after virtualenv due to the
        # !!! empty env_arguments list
        "virtualenv  --python=python0.0 {}".format(base_folder),
        ("pip install --pre aiida-core==0.0.0 aiida-vasp[extras1] "
         "pymatgen==2019.3.13"),
        ("git clone --single-branch --branch devel https://github.com/"
         "aiidateam/aiida-ase {}"
         .format(str(src_folder / "aiida-ase"))),
        ("pip install --editable {}"
         .format(str(src_folder / "aiida-ase[extras1]")))
    ]
    # compare expected cmd order with actual cmd order send to Popen
    actual_cmd_order = [_ for (_,) in fake_popen.args]
    assert actual_cmd_order == expected_cmd_order
    # test the written project specs
    path_to_config = (pathlib.Path.home() / constants.CONFIG_FOLDER
                      / constants.PROJECTS_FILE)
    assert path_to_config.exists() is True
    loaded_specs = utils.load_project_spec()
    assert 'venv_project' in loaded_specs.keys()
    contents = loaded_specs['venv_project']
    assert contents['project_path'] == str(pathlib.Path(temporary_folder))
    assert contents['aiida'] == '0.0.0'
    assert contents['python'] == '0.0'
    assert contents['env_sub'] == constants.DEFAULT_ENV_SUBFOLDER
    assert contents['src_sub'] == constants.DEFAULT_SRC_SUBFOLDER
    assert contents['manager'] == CreateEnvVirtualenv.__name__


def test_create_project_environment_failure(temporary_folder, temporary_home,
                                            fake_popen):
    """Test full cycle for creating an environment from conda."""
    # make sure we write to the correct directory
    assert pathlib.Path.home() == temporary_folder
    arguments = {
        'proj_name': 'venv_project',
        'proj_path': pathlib.Path(temporary_folder),
        'python_version': '0.0',
        'aiida_version': '0.0.0',
        'packages': ['aiida-vasp[extras1]', 'pymatgen==2019.3.13',
                     'aiidateam/aiida-ase:devel[extras1]']
    }
    fake_popen.returncode = 0
    creator = CreateEnvVirtualenv(**arguments)
    fake_popen.returncode = 1
    fake_popen.stderr = b'Venv'
    with pytest.raises(Exception) as exception:
        creator.create_aiida_project_environment()
    expected_exception_msg = "Environment setup failed (STDERR: Venv)"
    assert expected_exception_msg == str(exception.value)
    assert creator.proj_folder.exists() is False
    # check that nothing is written to the projects file
    path_to_config = (pathlib.Path.home() / constants.CONFIG_FOLDER
                      / constants.PROJECTS_FILE)
    assert path_to_config.exists() is False
