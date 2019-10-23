# -*- coding: utf-8 -*-

import re


def clone_git_repo_to_disk(github_url, location):
    """
    Clone the git repository at github_url to location on disk.

    :param str github_url: URL to github repository
    :param str location: path to the location disk
    """
    pass


def disassemble_package_def(package_definition):
    """
    Create a valid github URL from a given package definition.

    :param str package_definition: String of the form
        <username>/<repositor>:<branchname> defining the source of a package
    :returns: tuple containing (username, repository, branch) where branch
        is set to `None` for strings of the form <username>/<repository>
    :rtype: tuple
    """
    return (re.split(r"[\/\:]", package_definition) + [None])[:3]
