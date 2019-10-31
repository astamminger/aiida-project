# -*- coding: utf-8 -*-

"""
Activate AiiDA projects and export required variables
"""


class ActivateEnvBase(object):
    """Base class for activating AiiDA projects."""

    # paths and stuff should not change -> implement ShellActivators
    # doing the heavy lifting and dynamically connect them to
    # EnvironmentActivators which then simply need to determine the correct
    # paths and commands and pass them to the ShellActivator
