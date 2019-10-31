# -*- coding: utf-8 -*-
import shutil
import tempfile
import sys
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

import pytest
from click.testing import CliRunner

from aiida_project.create_env import CreateEnvBase


# skip certain tests for current platform
def pytest_runtest_setup(item):
    all_platforms = set("darwin linux win32".split())
    item_markers = [mark.name for mark in item.iter_markers()]
    supported_platforms = all_platforms.intersection(item_markers)
    current_platform = sys.platform
    if supported_platforms and current_platform not in supported_platforms:
        pytest.skip("skipping")


# register custom markers
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "linux: Mark test for execution only on linux platforms"
    )
    config.addinivalue_line(
        "markers", "win32: Mark test for execution only on windows platforms"
    )
    config.addinivalue_line(
        "markers", "darwin: Mark test for execution only on macos platforms"
    )


@pytest.fixture
def temporary_folder():
    tmp = tempfile.mkdtemp()
    yield pathlib.Path(tmp).absolute()
    shutil.rmtree(str(tmp))


@pytest.fixture
def env_creator(temporary_folder):
    class CreateEnvTest(CreateEnvBase):
        def __init__(self):
            # project attributes
            self.proj_name = "aiida_project"
            self.proj_path = pathlib.Path(temporary_folder).absolute()
            # environment creation
            self.env_executable = "env_executable"
            self.env_commands = ["env_command1", "env_command2"]
            self.env_flags = ["--flag1 arg1", "-flag2", "-flag3 arg3",
                              "--flag4=arg4"]
            self.env_arguments = ["arg1", "arg2", "arg3"]
            # package installation
            self.pkg_executable = "pkg_executable"
            self.pkg_commands = ["pkg_command1", "pkg_command2"]
            self.pkg_flags = ["--flag1 arg1", "-flag2", "-flag3 arg3",
                              "--flag4=arg4"]
            self.pkg_flags_source = ["--flag5 arg5", "-flag6", "-flag7 arg7",
                                     "--flag7=arg7"]
            self.pkg_arguments = ["arg1", "arg2=1.0.0", "arg3[extra1]",
                                  "user1/repo1:branch1", "user2/repo2[extra2]",
                                  "user3/repo3:branch2[extra3]",
                                  "arg4==0.12.1[extra4]"]
    return CreateEnvTest()


@pytest.fixture
def valid_env_input():
    valid_inputs = {
        'proj_name': 'test_project',
        'proj_path': pathlib.Path('/some/system/path'),
        'python_version': '3.6',
        'aiida_version': '1.0.0',
        'packages': ['postgresql', 'aiida-core.services'],
    }
    return valid_inputs


@pytest.fixture
def fake_popen(monkeypatch):
    class FakePopen(object):
        returncode = 0
        stdout = b''
        stderr = b''
        args = []
        kwargs = []

        def __init__(self, *args, **kwargs):
            # store arguments for later analysis
            self.args.append(args)
            self.kwargs.append(kwargs)

        def communicate(self, input=None):
            # do nothing but return the fake stdout / stderr
            return (self.stdout, self.stderr)
    monkeypatch.setattr('subprocess.Popen', FakePopen)
    yield FakePopen


@pytest.fixture
def click_cli_runner():
    yield CliRunner()