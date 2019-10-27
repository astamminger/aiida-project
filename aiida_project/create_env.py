# -*- coding: utf-8 -*-

from __future__ import print_function

import sys
import re
import shutil
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib

import click
import click_spinner

from aiida_project import utils


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
    pkg_arguments = None

    # cmd for crearing environment
    cmd_env = "{exe} {cmds} {flags} {args}"
    # cmd for installing packages
    cmd_install = "{exe} {cmds} {flags} {pkgs}"

    def create_folder_structure(self):
        """Setup the environments folder structure."""
        # first we try to create the parent folder to determine if it
        # exists already
        project_topfolder = self.proj_path / self.proj_name
        project_topfolder.mkdir(exist_ok=False)
        # once we have setup the parent folder we can create the subfolder
        # structure
        create_subfolder = [self.aiida_subfolder]
        if self.has_source():
            create_subfolder += [self.source_subfolder]
        for subfolder in create_subfolder:
            project_subfolder = project_topfolder / subfolder
            project_subfolder.mkdir(exist_ok=False)

    def install_packages_from_index(self, env=None, debug=False):
        """
        Install a package from the package index.

        :param list packages: A list of strings defining the package names
            that will be installed from a package index
        :param dict env: Optional dictionary containing environment variables
            passed to the subprocess executing the install
        """
        # extract non-source packages from package list
        index_packages = [p for p in self.pkg_arguments if not
                          utils.assert_package_is_source(p)]
        # build command for installing packages from index
        cmd_args = {
            'exe': self.pkg_executable,
            'cmds': " ".join(self.pkg_commands),
            'flags': " ".join(self.pkg_flags),
            'pkgs': " ".join(index_packages),
        }
        cmd_install_index = self.cmd_install.format(**cmd_args)
        if debug:
            return cmd_install_index
        errno, stdout, stderr = utils.run_command(cmd_install_index, env=env,
                                                  shell=True)
        if errno:
            raise Exception("Installation of packages failed (STDERR: {}"
                            .format(stderr))

    def install_packages_from_source(self, env=None, debug=False):
        """Install a package directly from source.

        :param list packages: A list of strings defining the source urls of
            packages that will be installed from source
        :param dict env: Optional dictionary containing environment variables
            passed to the subprocess executing the install
        """
        # extract all source packages from package list
        source_packages = [p for p in self.pkg_arguments if
                           utils.assert_package_is_source(p)]
        # process the raw user inputs
        pkg_install_paths = []
        for package in source_packages:
            pkg_def, pkg_extras = utils.unpack_raw_package_input(package)
            username, repo, branch = utils.unpack_package_def(pkg_def)
            github_url = utils.build_source_url(username, repo)
            # put source in source_subfolder / repository_name
            clone_path = (self.proj_path / self.proj_name
                          / self.source_subfolder / repo)
            clone_path_str = str(clone_path.absolute())
            # clone repository to disk
            utils.clone_git_repo_to_disk(github_url, clone_path_str,
                                         branch=branch, debug=debug)
            # build entry of the form path_to_package[extras] which will
            # be passed to the pip installer
            pkg_install_path = "{}{}".format(clone_path_str, pkg_extras)
            pkg_install_paths.append(pkg_install_path)

        # build command for installing packages from source
        cmd_args = {
            'exe': self.pkg_executable,
            'cmds': " ".join(self.pkg_commands),
            'flags': " ".join(self.pkg_flags_source),
            'pkgs': " ".join(pkg_install_paths),
        }
        cmd_install_source = self.cmd_install.format(**cmd_args)
        if debug:
            return cmd_install_source
        errno, stdout, stderr = utils.run_command(cmd_install_source, env=env,
                                                  shell=True)
        if errno:
            raise Exception("Installation of packages failed (STDERR: {}"
                            .format(stderr))

    def build_python_environment(self, debug=False):
        """Create the python environment with specified python version."""
        # build command for creating the python environment
        cmd_args = {
            'exe': self.env_executable,
            'cmds': " ".join(self.env_commands),
            'flags': " ".join(self.env_flags),
            'args': " ".join(self.env_arguments),
        }
        cmd_create_env = self.cmd_env.format(**cmd_args)
        if debug:
            return cmd_create_env
        errno, stdout, stderr = utils.run_command(cmd_create_env, env=None,
                                                  shell=True)
        if errno:
            raise Exception("Environment setup failed (STDERR: {}"
                            .format(stderr))

    def create_aiida_project_environment(self):
        """This command defines the steps to create the actual environment."""
        # i.e.
        # try:
        #   create_folder_structure()
        #   create_python_environment()
        #   install_packages_from_index()
        #   install_packages_from_source()
        # except:
        #    exit_on_exception()
        raise NotImplementedError("Must be implemented in the subclass")

    def exit_on_exception(self):
        """Cleanup if environment creation fails."""
        project_topfolder = self.proj_path / self.proj_name
        shutil.rmtree(str(project_topfolder.absolute()))

    def has_source(self):
        """Check for possible defined installations from source."""
        return any(map(utils.assert_package_is_source, self.pkg_arguments))

    def has_extras(self):
        """Check for possible package definitions with extras."""
        return any(map(utils.assert_package_has_extras, self.pkg_arguments))
