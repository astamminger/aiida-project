# -*- coding: utf-8 -*-
import pytest
import sys
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

from aiida_project.create_env import CreateEnvBase


def test_has_source():
    """Test the _hase_source() function of CreateEnvBase."""
    base = CreateEnvBase()
    #
    # test mixed list
    #
    package_list = [
        "aiida-core.services",
        "aiidateam/aiida-core:develop",
        "aiida-core==1.0.0b6",
    ]
    base.pkg_arguments = package_list
    assert base.has_source() is True
    #
    # test pure source list
    #
    package_list = [
        "aiidateam/aiida-core:develop",
        "aiidateam/aiida-ase:master",
        "aiidateam/aiida-vasp",
    ]
    base.pkg_arguments = package_list
    assert base.has_source() is True
    #
    # test pure index list
    #
    package_list = [
        "aiida-core==1.0.0b6",
        "aiida-core.services",
        "aiida-core==1.0.0b6[with,extras]",
    ]
    base.pkg_arguments = package_list
    assert base.has_source() is False


def test_create_folder_structure(temporary_folder):
    """Test project folder structure generation."""
    base = CreateEnvBase()
    base.proj_path = pathlib.Path(temporary_folder)
    #
    # test creation for index and source packages
    #
    base.proj_name = 'proj1'
    base.pkg_arguments = ["someuser/somerepo", "aiida-core"]
    base.create_folder_structure()
    # check for expected project and source folder
    assert base.proj_folder.exists() is True
    assert base.src_folder.exists() is True
    # check for the .aiida folder
    aiida_folder = base.proj_folder / base.aiida_subfolder
    assert aiida_folder.exists() is True
    #
    # test if subfolder name redefinitions are respected
    #
    base.proj_name = 'proj2'
    base.aiida_subfolder = 'renamed_aiida_folder'
    base.source_subfolder = 'renamed_source_folder'
    base.pkg_arguments = ["someuser/somerepo", "aiida-core"]
    base.create_folder_structure()
    # check for expected project and source folder
    assert base.proj_folder.exists() is True
    assert base.src_folder.exists() is True
    # check for the .aiida folder
    aiida_folder = base.proj_folder / base.aiida_subfolder
    assert aiida_folder.exists() is True
    #
    # test that source is only created when needed
    #
    base.proj_name = 'proj3'
    base.pkg_arguments = ['package1', 'package2']
    assert base.src_folder.exists() is False


def test_env_creation_routine(env_creator, fake_popen):
    """Test routine for environment installation."""
    cmd_args = {
        'exe': env_creator.env_executable,
        'cmds': " ".join(env_creator.env_commands),
        'flags': " ".join(env_creator.env_flags),
        'args': " ".join(env_creator.env_arguments),
    }
    wanted_cmd = '{exe} {cmds} {flags} {args}'.format(**cmd_args)
    fake_popen.returncode = 0
    env_creator.build_python_environment()
    generated_cmd, = fake_popen.args[0]
    assert generated_cmd == wanted_cmd


def test_install_index_routine(env_creator, fake_popen):
    """Test routine for package installation from index."""
    # index install must not contain any source packages
    index_packages = ["arg1", "arg2=1.0.0", "arg3[extra1]",
                      "arg4==0.12.1[extra4]"]
    cmd_args = {
        'exe': env_creator.pkg_executable,
        'cmds': " ".join(env_creator.pkg_commands),
        'flags': " ".join(env_creator.pkg_flags),
        'args': " ".join(index_packages),
    }
    fake_popen.returncode = 0
    wanted_cmd = '{exe} {cmds} {flags} {args}'.format(**cmd_args)
    env_creator.install_packages_from_index()
    generated_cmd, = fake_popen.args[0]
    assert generated_cmd == wanted_cmd


def test_install_source_routine(env_creator, fake_popen):
    """Test routine for package installation from source."""
    # source install must not contain any index packages and every source
    # definition should have been replaced by its appropriate path on disk
    # defined source packages:
    #   - "user1/repo1:branch1"  --> proj_path/proj_name/src/repo1
    #   - "user2/repo2[extra2]"  --> proj_path/proj_name/src/repo2
    #   - "user3/repo3:branch2[extra3]"  --> proj_path/proj_name/src/repo3
    # source packages installation arguments are expected to be of the
    # form: path_to_source_subfolder/repository_name[extras]
    source_packages = [
        "{}{}".format(str(env_creator.src_folder / 'repo1'), ''),
        "{}{}".format(str(env_creator.src_folder / 'repo2'), '[extra2]'),
        "{}{}".format(str(env_creator.src_folder / 'repo3'), '[extra3]'),
    ]
    wanted_cmds = []
    for source_package in source_packages:
        print(source_package)
        cmd_args = {
            'exe': env_creator.pkg_executable,
            'cmds': " ".join(env_creator.pkg_commands),
            'flags': " ".join(env_creator.pkg_flags_source),
            'args': source_package,
        }
        wanted_cmds.append(('{exe} {cmds} {flags} {args}'.format(**cmd_args),))
    env_creator.install_packages_from_source()
    # call to source install calls popen twice to clone the source from
    # github and install from the cloned source afterwards
    generated_cmds = fake_popen.args[1::2]
    assert wanted_cmds == generated_cmds
