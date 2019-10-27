# -*- coding: utf-8 -*-

import re
import subprocess

import click_spinner


def clone_git_repo_to_disk(github_url, location, branch=None, debug=False):
    """
    Clone the git repository at github_url to location on disk.

    :param str github_url: URL to github repository
    :param str branch: Specific branch of the github repository
    :param str location: path to the location disk
    """
    git_clone_args = ["git", "clone", "--single-branch"]
    if branch:
        git_clone_args.append("--branch {}".format(branch))
    git_clone_args.append("{}".format(github_url))
    git_clone_args.append("{}".format(location))
    git_clone_command = " ".join(git_clone_args)
    if debug:
        return git_clone_command
    print("Cloning repository {} ...".format(github_url))
    with click_spinner.spinner():
        errcode, stdout, stderr = run_command(git_clone_command, shell=True)
    if errcode:
        raise Exception("Cloning the repository from GitHub failed. Used "
                        "command {}, STDERR={}"
                        .format(git_clone_command, stderr.decode()))


def build_source_url(username, repository):
    """
    Create valid GitHub url for a user's repository.

    :param str username: username of the repository owner
    :param str repository: name of the target repository
    """
    base_url = 'https://github.com/{username}/{repository}'
    return base_url.format(username=username, repository=repository)


def run_command(command, shell=True, env=None):
    """Run a command through python subprocess."""
    proc = subprocess.Popen(command, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, shell=shell, env=env)
    stdout, stderr = proc.communicate()
    return (proc.returncode, stdout, stderr)


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


def assert_package_is_source(package_definition):
    """Check if a defined package refers to a source repo."""
    # basically identical to assert_valid_package_def but this regex will
    # also match <username>/<repository>:<branchname>[extras]
    charset = r"A-Za-z0-9_\.\\\-~"
    regex = (r"^[{}]+\/[{}]+\:[{}]+$|^[{}]+\/[{}]+"
             .format(*(charset,) * 5))
    return re.search(regex, package_definition) is not None


def assert_package_has_extras(package):
    return re.search(r"\[.*\]$", package) is not None


def unpack_package_def(package_definition):
    """
    Create a valid github URL from a given package definition.

    :param str package_definition: String of the form
        <username>/<repositor>:<branchname> defining the source of a package
    :returns: tuple containing (username, repository, branch) where branch
        is set to `None` for strings of the form <username>/<repository>
    :rtype: tuple
    """
    return (re.split(r"[\/\:]", package_definition) + [None])[:3]


def unpack_raw_package_input(package):
    """
    Split the raw user package input

    Raw input for source packages can be of the form
    username/repository:branch but could potentially also incude
    additional extras definitions, i.e.
    aiidateam/aiida-core:deveop[docs] which need to be removed before
    further processing of the string.
    :param str package_definition: String of the form
        <username>/<repositor>:<branchname>[extras] defining the source of a
        package including possible extras of the package
    """
    extras_regex = r"\[.*\]"
    package_extras = re.search(extras_regex, package)
    if package_extras:
        package_extras = package_extras.group(0)
        package_definition = re.sub(extras_regex, '', package)
        return(package_definition, package_extras)
    else:
        return (package, '')


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


def with_spinner(func):
    def wrapper(*args, **kwargs):
        with click_spinner.spinner():
            func(*args, **kwargs)
    return wrapper
