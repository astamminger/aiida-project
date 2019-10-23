# -*- coding: utf-8 -*-

import sys
import re

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
    pkg_arguments = None
    pkg_list = None

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
        if self._has_source():
            create_subfolder += [self.source_subfolder]
        for subfolder in create_subfolder:
            project_subfolder = project_topfolder / subfolder
            project_subfolder.mkdir(exist_ok=False)

    def install_packages_to_env(self):
        """Install packages to the generated environment."""
        pass

    def install_package_from_index(self):
        """Install a package from the package index."""
        pass

    def install_package_from_source(self):
        """Install a package directly from source."""
        pass

    def _is_source(self, package):
        """Check if a defined package refers to a source repo."""
        if re.match(r"https://github.com", package):
            return True
        else:
            return False

    def _has_source(self):
        """Check for possible defined installations from source."""
        return any(map(self._is_source, self.pkg_arguments))

    def _execute(self):
        """Execute provided command."""
        pass
