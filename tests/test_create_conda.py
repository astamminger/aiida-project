# -*- coding: utf-8 -*-
import pytest
import sys
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

from aiida_project.create import CreateEnvConda
from aiida_project import utils
from aiida_project import constants


def test_python_version(valid_env_input, fake_popen):
    """Test python package definition is correct."""
    # setup Popen
    fake_popen.set_cmd_attrs('conda --version', returncode=0)
    fake_popen.set_cmd_attrs('git --version', returncode=0)
    valid_env_input['python_version'] = '123.456'
    env_creator = CreateEnvConda(**valid_env_input)
    wanted_format = "python=123.456"
    assert wanted_format in env_creator.env_arguments


def test_aiida_version(valid_env_input, fake_popen):
    """Test aiida package definition is correct."""
    # setup Popen
    fake_popen.set_cmd_attrs('conda --version', returncode=0)
    fake_popen.set_cmd_attrs('git --version', returncode=0)
    valid_env_input['aiida_version'] = '1.2.3b56'
    env_creator = CreateEnvConda(**valid_env_input)
    wanted_format = "aiida-core=1.2.3b56"
    assert wanted_format in env_creator.pkg_arguments


def test_source_package_raises(valid_env_input, fake_popen):
    """Check that source package definition raises exception."""
    # setup Popen
    fake_popen.set_cmd_attrs('conda --version', returncode=0)
    fake_popen.set_cmd_attrs('git --version', returncode=0)
    # this should work
    try:
        env_creator = CreateEnvConda(**valid_env_input)
    except Exception:
        pytest.fail("Creation of CreateEnvConda instance raised an "
                    "unexpected exception")
    # however, defining a source should fail
    valid_env_input['packages'] = ['postgresql', 'aiidateam/aiida-ase']
    with pytest.raises(Exception) as exception:
        env_creator = CreateEnvConda(**valid_env_input)
    assert "Installation from source" in str(exception.value)


def test_defined_extra_raises(valid_env_input, fake_popen):
    """Check that package with defined extra raises exception."""
    # setup Popen
    fake_popen.set_cmd_attrs('conda --version', returncode=0)
    fake_popen.set_cmd_attrs('git --version', returncode=0)
    # this should work
    try:
        env_creator = CreateEnvConda(**valid_env_input)
    except Exception:
        pytest.fail("Creation of CreateEnvConda instance raised an "
                    "unexpected exception")
    # however, defining a source should fail
    valid_env_input['packages'] = ['postgresql', 'aiida-ase[some_extra]']
    with pytest.raises(Exception) as exception:
        env_creator = CreateEnvConda(**valid_env_input)
    assert "Installation of extras" in str(exception.value)


def test_create_project_environment_success(temporary_folder, temporary_home,
                                            fake_popen):
    """Test full cycle for creating an environment from conda."""
    # setup Popen
    fake_popen.set_cmd_attrs('conda --version', returncode=0)
    fake_popen.set_cmd_attrs('git --version', returncode=0)
    # make sure we write to the correct directory
    assert pathlib.Path.home() == temporary_folder
    arguments = {
        'proj_name': 'conda_project',
        'proj_path': pathlib.Path(temporary_folder),
        'python_version': '0.0',
        'aiida_version': '0.0.0',
        'packages': ['aiida-core.services', 'pymatgen=2019.3.13'],
    }
    creator = CreateEnvConda(**arguments)
    fake_popen.set_cmd_attrs('conda', returncode=0)
    creator.create_aiida_project_environment()
    base_folder = str((creator.env_folder / creator.proj_name).absolute())
    expected_cmd_order = [
        "conda --version",
        "conda create --yes --prefix {} python=0.0".format(base_folder),
        ("conda install --yes --channel conda-forge --channel bioconda "
         "--channel matsci --prefix {} aiida-core=0.0.0 aiida-core.services "
         "pymatgen=2019.3.13".format(base_folder)),
    ]
    # compare expected cmd order with actual cmd order send to Popen
    actual_cmd_order = [_ for (_,) in fake_popen.args]
    assert actual_cmd_order == expected_cmd_order
    # test the written project specs
    path_to_config = (pathlib.Path.home() / constants.CONFIG_FOLDER
                      / constants.PROJECTS_FILE)
    assert path_to_config.exists() is True
    loaded_specs = utils.load_project_spec()
    assert 'conda_project' in loaded_specs.keys()
    contents = loaded_specs['conda_project']
    ppath = pathlib.Path(temporary_folder)
    srcpath = ppath / 'conda_project' / constants.DEFAULT_SRC_SUBFOLDER
    envpath = ppath / 'conda_project' / constants.DEFAULT_ENV_SUBFOLDER
    assert contents['project_path'] == str(ppath)
    assert contents['aiida'] == '0.0.0'
    assert contents['python'] == '0.0'
    assert contents['env_sub'] == str(envpath)
    assert contents['src_sub'] == str(srcpath)
    assert contents['manager'] == constants.MANAGER_NAME_CONDA


def test_create_project_environment_failure(temporary_folder, temporary_home,
                                            fake_popen):
    """Test that exit_on_exception() is called on failed creation."""
    # setup Popen
    fake_popen.set_cmd_attrs('conda --version', returncode=0)
    fake_popen.set_cmd_attrs('git --version', returncode=0)
    # make sure we write to the correct directory
    assert pathlib.Path.home() == temporary_folder
    arguments = {
        'proj_name': 'conda_project',
        'proj_path': pathlib.Path(temporary_folder),
        'python_version': '0.0',
        'aiida_version': '0.0.0',
        'packages': ['aiida-core.services', 'pymatgen=2019.3.13'],
    }
    # make sure command checks pass to initialize the class
    creator = CreateEnvConda(**arguments)
    # now let all future calls to Popen fail
    fake_popen.set_cmd_attrs('conda', returncode=1, stderr=b'Conda')
    with pytest.raises(Exception) as exception:
        creator.create_aiida_project_environment()
    expected_exception_msg = "Environment setup failed (STDERR: Conda)"
    assert expected_exception_msg == str(exception.value)
    assert creator.proj_folder.exists() is False
    # check that nothing is written to the projects file
    path_to_config = (pathlib.Path.home() / constants.CONFIG_FOLDER
                      / constants.PROJECTS_FILE)
    assert path_to_config.exists() is False
