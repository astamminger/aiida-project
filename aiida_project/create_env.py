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
    """Base class for setting up python environments programatically."""

    # define environment name and locations
    proj_name = None
    proj_path = None
    src_subfolder = 'src'
    env_subfolder = 'env'
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

    @property
    def proj_folder(self):
        return self.proj_path / self.proj_name

    @property
    def env_folder(self):
        return self.proj_folder / self.env_subfolder

    @property
    def src_folder(self):
        return self.proj_folder / self.src_subfolder

    def create_folder_structure(self):
        """Setup the environments folder structure."""
        # create the parent folder holding the project
        self.proj_folder.mkdir(exist_ok=False)
        # once we have setup the parent folder we can create the subfolder
        # structure
        create_subfolder = [self.aiida_subfolder, self.env_subfolder]
        if self.has_source():
            create_subfolder += [self.src_subfolder]
        for subfolder in create_subfolder:
            project_subfolder = self.proj_folder / subfolder
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
            clone_path = self.src_folder / repo
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

    def exit_on_exception(self):
        """Cleanup if environment creation fails."""
        shutil.rmtree(str(self.proj_folder.absolute()))

    def has_source(self):
        """Check for possible defined installations from source."""
        return any(map(utils.assert_package_is_source, self.pkg_arguments))

    def has_extras(self):
        """Check for possible package definitions with extras."""
        return any(map(utils.assert_package_has_extras, self.pkg_arguments))


class CreateEnvConda(CreateEnvBase):
    """
    Create new python environment using the conda package manager

    Running the create_aiida_project_environment() function will create
    a new project folder with name `proj_name` in the directory defined by
    `proj_path`. It will then create the `.aiida` folder in the created
    folder and install a new python environment to the `env` subfolder.

    :param str proj_name: Name of the new AiiDA project (This is also going
        to be the name of the created conda environment)
    :param str proj_path: Path to the topfolder containing the new project
    :param str python_version: Python version to be used for the
        environment (expected format: 'N.M', i.e. '2.7', '3.6' ...)
    :param str aiida_version: AiiDA version which will be installed in the
        environment. (accepts any version format that is understood by the
        conda installer, i.e. 1.0.0, 1.0.0b5, ...)
    :param list package: A list of additional packages which will be installed
        in addition to aiida-core (accepts any package format that is
        understood by conda, i.e. 'postgresql', 'postgresql=11.4', ...)

    :raises Exception: if any package is defined as source package (i.e. the
        package definition is of the form aiidateam/aiida-ase,
        aiidateam/aiida-ase:master, ...)
    :raises Exception: if any package defines extras to be installed (i.e.
        package definition is of the form package[extra])
    :raises Exception: if conda is not found on the system
    """
    def __init__(self, proj_name, proj_path, python_version, aiida_version,
                 packages):
        # fail early if any commands are missing
        self.check_required_commands()

        # setup internal variables
        self.proj_name = proj_name
        self.proj_path = proj_path
        self.src_subfolder = "src"
        self.env_subfolder = "env"
        self.aiida_subfolder = ".aiida"

        # environment
        prefix = self.env_folder / self.proj_name
        self.env_executable = "conda"
        self.env_commands = ["create"]
        self.env_flags = [
            "--yes",
            "--prefix {}".format(str(prefix.absolute())),
        ]
        self.env_arguments = [
            "python={}".format(python_version),
        ]
        # additional packages
        self.pkg_executable = "conda"
        self.pkg_commands = ["install"]
        self.pkg_flags = [
            "--yes",
            "--channel conda-forge",
            "--channel bioconda",
            "--channel matsci",
            "--prefix {}".format(str(prefix.absolute())),
        ]
        aiida_core_package = "aiida-core={}".format(aiida_version)
        packages_all = list([aiida_core_package] + packages)
        self.pkg_arguments = packages_all

        # run check hook to verify inputs
        self.verify_inputs()

    def check_required_commands(self):
        """Check required commands are available on the system."""
        # no need to check for git in the conda installer since we do not
        # allow source installes, we only check for conda
        conda_avail = utils.check_command_avail('conda')
        if not conda_avail:
            raise Exception("Unable to find the `conda` executable on the "
                            "system. Is anaconda on the PATH?")

    def verify_inputs(self):
        """Check if inputs are of correct form."""
        if self.has_source():
            raise Exception("Installation from source is only available for "
                            "`virtualenv` manager")
        if self.has_extras():
            raise Exception("Installation of extras only possible for "
                            "`virtualenv` manager")

    def create_aiida_project_environment(self):
        """Create the folder structure and initialize the environment."""
        try:
            self.create_folder_structure()
            self.create_python_environment()
            self.install_packages_from_index()
        except Exception:
            self.exit_on_exception()
