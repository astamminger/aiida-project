# -*- coding: utf-8 -*-

from aiida_project.utils import (assert_package_is_source, run_command,
                                 clone_git_repo_to_disk)

import click_spinner

import sys
import re
import shutil

if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib


"""
Create AiiDA project environment and install packages
"""


class CreateEnvBase(object):

    # define environment name and locations
    proj_name = None
    proj_path = None
    source_subfolder = 'src'
    aiida_subfolder = '.aiida'

    # define the command for creating an environment
    env_executable = None
    env_commands = None
    env_flags = None
    env_arguments = None

    # define the command for installing packages
    pkg_executable = None
    pkg_commands = None
    pkg_flags = None
    pkg_flags_source = None  # additional flags used for source install

    # cmd for crearing environment
    cmd_env = "{exe} {cmds} {flags} {args}"
    # cmd for installing packages
    cmd_install = "{exe} {cmds} {flags} {pkgs}"

    def create_folder_structure(self):
        """Setup the environments folder structure."""
        # first we try to create the parent folder to determine if it
        # exists already
        try:
            project_topfolder = self.proj_path / self.proj_name
            project_topfolder.mkdir(exist_ok=False)
        except FileExistsError:
            raise FileExistsError("Cannot create project folder '{}' beacuse "
                                  "the folder already exists"
                                  .format(project_topfolder))
        # once we have setup the parent folder we can create the subfolder
        # structure
        create_subfolder = [self.aiida_subfolder]
        if self.has_source():
            create_subfolder += [self.source_subfolder]
        for subfolder in create_subfolder:
            project_subfolder = project_topfolder / subfolder
            project_subfolder.mkdir(exist_ok=False)

    def install_packages_from_index(self, index_packages, env=None):
        """
        Install a package from the package index.

        :param list packages: A list of strings defining the package names
            that will be installed from a package index
        :param dict env: Optional dictionary containing environment variables
            passed to the subprocess executing the install
        """
        # build command for installing packages from index
        cmd_args = {
            'exe': self.pkg_executable,
            'cmds': self.pkg_commands,
            'flags': self.pkg_flags,
            'pkgs': " ".join(index_packages),
        }
        cmd_install_index = self.cmd_install.format(**cmd_args)
        print(cmd_install_index)
        # this will trigger a simple install
        # build list and install all packages at once
        pass

    def install_packages_from_source(self, source_packages, env=None):
        """Install a package directly from source.

        :param list packages: A list of strings defining the source urls of
            packages that will be installed from source
        :param dict env: Optional dictionary containing environment variables
            passed to the subprocess executing the install
        """
        # build command for installing packages from source
        cmd_args = {
            'exe': self.pkg_executable,
            'cmds': " ".join(self.pkg_commands),
            'flags': " ".join(self.pkg_flags_source),
            'pkgs': " ".join(source_packages),
        }
        cmd_install_source = self.cmd_install.format(**cmd_args)
        print(cmd_install_source)
        # this will trigger editable installation
        # clone all packages to the appropriate destinations
        # transform URLs to paths on disk
        # build list and install all packages at once
        pass

    def create_python_environment(self, python_version):
        """Create the python environment with specified python version."""
        # build command for creating the python environment
        cmd_args = {
            'exe': self.env_executable,
            'cmds': " ".join(self.env_commands),
            'flags': " ".join(self.env_flags),
            'args': " ".join(self.env_arguments),
        }
        cmd_create_env = self.cmd_env.format(**cmd_args)

    def create_aiida_project_environment(self):
        """Create the actual environment."""
        # create_folder_structure()
        # create_python_environment()
        # install_packages_from_index()
        # install_packages_from_source()
        # if failed:
        #    self.exit_on_exception()

    def execute(self):
        """Execute provided command."""
        pass

    def exit_on_exception(self):
        """Cleanup if environment creation fails."""
        project_topfolder = self.proj_path / self.proj_name
        shutil.rmtree(project_topfolder)

    def has_source(self):
        """Check for possible defined installations from source."""
        return any(map(assert_package_is_source, self.pkg_arguments))
