# -*- coding: utf-8 -*-


import os
import sys
if sys.version_info >= (3, 0):
    import pathlib as pathlib
else:
    import pathlib2 as pathlib


from aiida_project import utils
from aiida_project import constants


"""
Activate AiiDA projects and export required variables
"""


class ActivateEnvBase(object):
    """Base class for activating AiiDA projects."""

    # define how to export environment variables, etc.
    set_var = None
    unset_var = None
    cmd_join = None

    # environment variables to be exported (expects a list of tuples
    # [(ENVVAR, value), ...]
    environment_variables = []
    # commands to run for activating / deactivating an environment
    # ["command with args", ....]
    activate_commands = []
    deactivate_commands = []

    def load_project_spec(self, project_name):
        """Load the specifications for the given project."""
        project_specs = utils.load_project_spec()
        try:
            project_spec = project_specs[project_name]
        except KeyError:
            raise Exception("Unable to complete activation. Project '{}' "
                            "does not exists.".format(project_name))
        return project_spec

    def get_aiida_path_from_spec(self, project_spec):
        """Determine the path to the .aiida folder of the project."""
        project_path = pathlib.Path(project_spec['project_path'])
        path_to_aiida_folder = project_path / constants.AIIDA_SUBFOLDER
        if not path_to_aiida_folder.exists():
            raise Exception("Aiida subfolder not found at location {}"
                            .format(path_to_aiida_folder))
        return project_path.absolute()

    def validate_activatable(self):
        """Validate activation is possible in the current shell"""
        # refuse to load a project if another project is active in the
        # current shell
        project_name = os.environ.get('AIIDA_PROJECT_ACTIVE', '')
        if project_name:
            raise Exception("currently activated project '{}' needs to be "
                            "deactivated prior to activating a new project"
                            .format(project_name))
        # also refuse to load a project when AIIDA_PATH is already set
        if os.environ.get('AIIDA_PATH', ''):
            raise Exception("cannot activate project because AIIDA_PATH "
                            "is already set")

    def validate_deactivatable(self):
        """Validate deactivation is possible in the current shell"""
        # raise exception during deactivate if not project is loaded
        project_name = os.environ.get('AIIDA_PROJECT_ACTIVE', '')
        if not project_name:
            raise Exception("no project currently loaded")

    def build_cmd_activate(self):
        """Build command for environment activation"""
        # first export all environment variables ...
        activate_commands = []
        for envvar in self.environment_variables:
            activate_commands.append(self.set_var.format(*envvar))
        # ... then run the activation commands if defined
        activate_commands += self.activate_commands
        return self.cmd_join.join(activate_commands)

    def build_cmd_deactivate(self):
        """Build command for environment deactivation"""
        # first unset all environment variables ...
        deactivate_commands = []
        for (envvar_name, _) in self.environment_variables:
            deactivate_commands.append(self.unset_var.format(envvar_name))
        # ... then run the deactivation commands if defined
        deactivate_commands += self.deactivate_commands
        return self.cmd_join.join(deactivate_commands)

    def execute(self, mode):
        """Return string that is source to change shell state"""
        if mode == "activate":
            self.validate_activatable()
            return self.build_cmd_activate()
        elif mode == "deactivate":
            self.validate_deactivatable()
            return self.build_cmd_deactivate()
        else:
            raise Exception("Unknown activation mode: '{}'".format(mode))


class ActivateEnvBash(ActivateEnvBase):

    # bash specifica
    set_var = "export {}='{}'"
    unset_var = "unset {}"
    cmd_join = ";"

    def __init__(self, manager, project_name):
        """Initialize internal variables."""
        project_spec = self.load_project_spec(project_name)
        env_name = project_name
        # set required activation / deactivation commands for manager
        if manager == constants.MANAGER_NAME_CONDA:
            self.check_conda_avail()
            self.activate_commands = ["conda activate {}".format(env_name)]
            self.deactivate_commands = ["conda deactivate"]
        elif manager == constants.MANAGER_NAME_VENV:
            venv_activate_script = self.check_virtualenv_path(project_spec)
            self.activate_commands = [". '{}'".format(venv_activate_script)]
            self.deactivate_commands = ["deactivate"]
        else:
            raise Exception("manager '{}' not supported by bash activator"
                            .format(manager))
        # enable verdi autocomplete upon activation (this is basically an
        # eval inside eval, not idead if this is a good idea)
        self.activate_commands.append("eval \"$(verdi completioncommand)\"")

        # setup additional deactivation commands
        self.deactivate_commands.append("complete -r verdi")

        # define environment variables to be set
        aiida_path = self.get_aiida_path_from_spec(project_spec)
        self.environment_variables = [
            ('AIIDA_PATH', aiida_path),
            ('AIIDA_PROJECT_ACTIVE', env_name),
        ]

    @classmethod
    def _setup(cls, executable):
        """
        Make aiida-project available in the bash shell.

        :param executable: path to the aiida-project executable file
        :type executable: pathlib.Path
        :returns: multiline string to be evaluated by the calling shell
        :rtype: str
        """
        setup_string = \
        (
            cls.set_var.format('AIIDA_PROJECT_EXE', executable),  # noqa: E122
            'function _aiida_project_activate() {',
            '  local mode=$1',  # activate / deactivate (must be first arg!)
            '  shift',          # remove $1 from the list of args $@
            '  cmd="$("$AIIDA_PROJECT_EXE" "$mode" bash "$@")" || return $?',
            '  eval "$cmd"',
            '}',
            'function aiida-project-bash() {',
            '  if [ "$#" -lt 1 ]; then',
            '    "$AIIDA_PROJECT_EXE"',
            '    return $?',
            '  fi',
            '  case "$1" in',
            '    activate|deactivate)',
            '      _aiida_project_activate "$@"',
            '    ;;',
            '  *)',
            '      "$AIIDA_PROJECT_EXE" "$@"',
            '    ;;',
            '  esac',
            '}',
        )
        return "\n".join(setup_string)

    def check_conda_avail(self):
        """check if conda command is available in shell."""
        conda_available = utils.check_command_avail('conda')
        if not conda_available:
            raise Exception("unable to activate environment because "
                            "conda does not seem to be available.")

    def check_virtualenv_path(self, project_spec):
        """check if activate script for virtualenv exists."""
        path_to_env = pathlib.Path(project_spec['env_sub']).absolute()
        path_to_activation_script = path_to_env / 'bin' / 'activate'
        if not path_to_activation_script.exists():
            raise Exception("Unable to load project. No activation script "
                            "found at location {}"
                            .format(path_to_activation_script))
        else:
            return str(path_to_activation_script.absolute())


def get_activator(shell):
    if shell not in constants.SUPPORTED_SHELLS:
        raise Exception("Unsupported shell type `{}` (currently supported "
                        "shell types: {})"
                        .format(shell, constants.SUPPORTED_SHELLS))
    activator_map = {
        constants.SHELL_NAME_BASH: ActivateEnvBash,
    }
    return activator_map[shell]
