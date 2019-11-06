# -*- coding: utf-8 -*-
import os
import sys
import string
import random
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

import pytest

from aiida_project import utils
from aiida_project import constants


def test_unpack_package_def():
    """Test extraction of username, repository and branch name."""
    charset = ''.join([string.ascii_letters, string.digits, r"_.\-~"])
    #
    # test disassembling of full repo definition
    #
    user = ''.join([random.choice(charset) for _ in range(50)])
    repo = ''.join([random.choice(charset) for _ in range(50)])
    branch = ''.join([random.choice(charset) for _ in range(50)])
    repo_def = "{}/{}:{}".format(user, repo, branch)
    u, r, b = utils.unpack_package_def(repo_def)
    assert u == user
    assert r == repo
    assert b == branch
    #
    # test disassembling of partial repo definition
    #
    user = ''.join([random.choice(charset) for _ in range(50)])
    repo = ''.join([random.choice(charset) for _ in range(50)])
    repo_def = "{}/{}".format(user, repo)
    u, r, b = utils.unpack_package_def(repo_def)
    assert u == user
    assert r == repo
    assert b is None


def test_unpack_raw_package_input():
    """Test dissasembly of the user's raw package input."""
    # test for sources with branch
    source = "someuser/repository:devel_branch"
    extras = "[pre-commit, testing, docs]"
    full_input = source + extras
    out_source, out_extras = utils.unpack_raw_package_input(full_input)
    assert out_source == source
    assert out_extras == extras
    # test also for source without branch definition
    source = "someuser/repository"
    extras = "[pre-commit, testing, docs]"
    full_input = source + extras
    out_source, out_extras = utils.unpack_raw_package_input(full_input)
    assert out_source == source
    assert out_extras == extras
    # check if no extras are given
    source = "someuser/repository:devel_branch"
    out_source, out_extras = utils.unpack_raw_package_input(source)
    assert out_source == source
    assert out_extras == ''


def test_assert_package_is_source():
    """Test the assert_package_is_source() utility function."""
    package_source = "aiidateam/aiida-core:develop"
    assert utils.assert_package_is_source(package_source) is True
    package_source = "aiidateam/aiida-core"
    assert utils.assert_package_is_source(package_source) is True
    package_source = "aiidateam/aiida-core:develop[has,some,extras]"
    assert utils.assert_package_is_source(package_source) is True
    package_source = "aiidateam/aiida-core[has,some,extras]"
    assert utils.assert_package_is_source(package_source) is True
    package_index = "aiida-core==1.0.0b6"
    assert utils.assert_package_is_source(package_index) is False


def test_assert_valid_package_def():
    """Test assertion function for package definition strings."""
    charset = ''.join([string.ascii_letters, string.digits, r"_.\-~"])
    chars = ''.join([random.choice(charset) for _ in range(50)])
    testcases = [
        # allowed patterns
        ("{}/{}:{}".format(*(chars,) * 3), True),
        ("{}/{}".format(*(chars,) * 2), True),
        # build some malformed testcases
        ("{}/{}:".format(*(chars,) * 2), False),
        ("{}/{}:{}{}/{}:{}".format(*(chars,) * 6), False),
        ("/{}:{}".format(*(chars,) * 2), False),
        ("{}:{}".format(*(chars,) * 2), False),
        ("{}/:{}".format(*(chars,) * 2), False),
        ("{}//{}:".format(*(chars,) * 2), False),
        ("{}/{}::{}".format(*(chars,) * 3), False),
        ("", False),
        ("{}".format(chars), False),
    ]
    for (testcase, result) in testcases:
        assert utils.assert_valid_package_def(testcase) == result


def test_assert_valid_aiida_version():
    """Test assertion function for aiida version numbers."""
    # Test against all AiiDA versions available on pypi.org
    testcases = [
        "0.6.0.1",
        "0.7.0.1",
        "0.7.1.1",
        "0.8.0rc1",
        "0.8.0rc2",
        "0.8.0",
        "0.8.1",
        "0.9.0",
        "0.9.1",
        "0.10.0rc1",
        "0.10.0rc2",
        "0.10.0rc2",
        "0.10.0",
        "0.10.1",
        "0.11.0",
        "0.11.1",
        "0.11.2",
        "0.11.3",
        "0.11.4",
        "0.12.0",
        "0.12.1",
        "0.12.2",
        "0.12.3",
        "0.12.4",
        "1.0.0a1",
        "1.0.0a2",
        "1.0.0a3",
        "1.0.0a4",
        "1.0.0b1",
        "1.0.0b2",
        "1.0.0b3",
        "1.0.0b4",
        "1.0.0b5",
        "1.0.0b6",
    ]
    for testcase in testcases:
        assert utils.assert_valid_aiida_version(testcase) is True


def test_check_command():
    """Test the check_command utility function."""
    # if command succeeds with errorcode 0 we assume it is available
    result = utils.check_command_avail('exit 0', test_version=False)
    assert result is True
    # for returncodes other than 0 we assume the command is not available
    result = utils.check_command_avail('exit 1', test_version=False)
    assert result is False


def test_run_command():
    """Test run_command() function running shell commands."""
    # test simple run (don't use quotations to produce the same results
    # in shell and windows cmd)
    testcmd = 'echo running test command'
    errno, stdout, stderr = utils.run_command(testcmd, shell=True)
    assert errno == 0
    assert stdout.rstrip() == "running test command"
    assert stderr.rstrip() == ""

    # test run with changed environment
    envvar = "set by calling python"
    env = os.environ.copy()
    env["CHANGED_ENVVAR"] = envvar
    testcmd = 'echo $CHANGED_ENVVAR'
    errno, stdout, stderr = utils.run_command(testcmd, shell=True, env=env)
    assert errno == 0
    assert stdout.rstrip() == envvar
    assert stderr.rstrip() == ""


def test_build_source_url():
    """Test creation of source urls for packages hosted on github."""
    username = "someuser"
    repository = "someusersrepository"
    wanted_url = "https://github.com/someuser/someusersrepository"
    url = utils.build_source_url(username, repository)
    assert url == wanted_url


def test_clone_git_repo_to_disk(fake_popen):
    """Test cloning of github repositories to disk"""
    fake_popen.set_cmd_attrs('git', returncode=0)
    # check cloning without defined branch
    location_on_disk = "/some/random/path/on/disk"
    github_url = "https://github.com/user1/repo1"
    utils.clone_git_repo_to_disk(github_url, location_on_disk)
    generated_cmd, = fake_popen.args.pop()
    wanted_cmd = ("git clone --single-branch {} {}"
                  .format(github_url, location_on_disk))
    assert wanted_cmd == generated_cmd

    # check cloning with present path
    branch = 'branch1'
    utils.clone_git_repo_to_disk(github_url, location_on_disk, branch=branch)
    generated_cmd, = fake_popen.args.pop()
    wanted_cmd = ("git clone --single-branch --branch {} {} {}"
                  .format(branch, github_url, location_on_disk))
    assert wanted_cmd == generated_cmd


def test_save_and_load_project_spec(temporary_home):
    """Test that the project spec is written and loaded correctly."""
    project_name_a = 'testproject_a'
    project_spec_a = {
        'project_name': project_name_a,
        'project_path': '/this/is/some/random/path',
        'aiida': '12.2323.23982',
        'python': '28932.28392',
        'env_sub': 'the_env_subfolder',
        'src_sub': 'the_src_subfolder',
        'manager': 'manager_name',
    }
    project_name_b = 'testproject_b'
    project_spec_b = {
        'project_name': project_name_b,
        'project_path': '/this/is/some/random/path',
        'aiida': '12.2323.23982',
        'python': '28932.28392',
        'env_sub': 'the_env_subfolder',
        'src_sub': 'the_src_subfolder',
        'manager': 'manager_name',
    }
    path_to_config = (pathlib.Path.home() / constants.CONFIG_FOLDER
                      / constants.PROJECTS_FILE)
    # check that there is no file already
    assert path_to_config.exists() is False
    # write specs to file
    utils.save_project_spec(project_spec_a)
    assert path_to_config.exists() is True
    # load specs from file
    loaded_spec_a = utils.load_project_spec()
    assert project_name_a in loaded_spec_a.keys()
    # save_project_spec has already popped the 'project_name' key so we
    # can compare the contents immediately
    assert loaded_spec_a[project_name_a] == project_spec_a
    # write the second spec to the file
    utils.save_project_spec(project_spec_b)
    # and load it back
    loaded_spec_b = utils.load_project_spec()
    assert project_name_a in loaded_spec_b.keys()
    assert project_name_b in loaded_spec_b.keys()
    # save_project_spec has already popped the 'project_name' key so we
    # can compare the contents immediately
    assert loaded_spec_b[project_name_a] == project_spec_a
    assert loaded_spec_b[project_name_b] == project_spec_b


def test_project_name_exists(temporary_home):
    """Test the function checking for duplicate project names."""
    project_name = 'test_project'
    project_spec = {
        'project_name': project_name,
        'project_path': '',
        'aiida': '',
        'python': '',
        'env_sub': '',
        'src_sub': '',
        'manager': '',
    }
    # save and check that the project is there
    utils.save_project_spec(project_spec)
    loaded_contents = utils.load_project_spec()
    assert project_name in loaded_contents.keys()
    result = utils.project_name_exists('test_project')
    assert result is True
    result = utils.project_name_exists('test_project_new')
    assert result is False
