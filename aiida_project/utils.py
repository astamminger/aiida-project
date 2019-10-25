# -*- coding: utf-8 -*-

import re
import subprocess

import click_spinner


def clone_git_repo_to_disk(github_url, branch, location):
    """
    Clone the git repository at github_url to location on disk.

    :param str github_url: URL to github repository
    :param str branch: Specific branch of the github repository
    :param str location: path to the location disk
    """
    git_clone_command = ("git clone --single-branch --branch {branch} "
                         " {url} {path}".format(branch=branch, url=github_url,
                                                path=location))
    proc = subprocess.Popen(git_clone_command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    print("Cloning repository {} ...".format(github_url))
    with click_spinner.spinner():
        stdout, stderr = proc.communicate()
    if proc.returncode:
        raise Exception("Cloning the repository from GitHub failed. Used "
                        "command {}, STDERR={}"
                        .format(git_clone_command, stderr.decode()))


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


def check_command_avail(command, test_version=True):
    """
    Test if a command is available in the current shell environment.

    :param str command: Command to test
    :param bool test_version: If `True` command --version will be checked
        instead of the plain command
    """
    # run command --version because some commands do not exit with
    # exitcode 0 when called without any arguments (i.e. git)
    if test_version:
        command_to_check = "{} --version".format(command)
    else:
        command_to_check = command
    proc = subprocess.Popen(command_to_check, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=True)
    stdout, stderr = proc.communicate()
    if proc.returncode:
        return False
    else:
        return True
