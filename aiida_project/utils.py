# -*- coding: utf-8 -*-

import re


def clone_git_repo_to_disk(github_url, location):
    """
    Clone the git repository at github_url to location on disk.

    :param str github_url: URL to github repository
    :param str location: path to the location disk
    """
    pass


def assert_valid_aiida_version(aiida_version_string):
    """Verify that given aiida version is of type N.N.N(a/bN)."""
    # Regular expression to check for canonical version format according
    # to PEP440, taken from https://www.python.org/dev/peps/pep-0440
    regex = re.compile(r'^([1-9][0-9]*!)?(0|[1-9][0-9]*)'
                       r'(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?'
                       r'(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$')
    return re.match(regex, aiida_version_string) is not None


def assert_valid_package_def(package_definition):
    """
    Verify package definition is formatted as <username>/<repository>:<branch>

    :param str package_definition: String of the form
        <username>/<repositor>:<branchname> defining the source of a package
    """
    charset = r"A-Za-z0-9_\.\\\-~"
    regex = (r"^[{}]+\/[{}]+\:[{}]+$|^[{}]+\/[{}]+$"
             .format(*(charset,) * 5))
    return re.match(regex, package_definition) is not None


def assert_package_is_source(package):
    """Check if a defined package refers to a source repo."""
    return re.match(r"^https://github.com", package) is not None


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
