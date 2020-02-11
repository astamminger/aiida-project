# AiiDA Project Manager Utility

Utility programm for AiiDA which allows to setup and manage independent
AiiDA projects running in isolated python environments from the commandline.

* Setup independent python environments supporting `conda` or `virtualenv`
* Install packages either from package index or directly from available
  github repositories

## Usage

### Creating a new environment

After installing ``aiida-project`` a new AiiDA environment can be setup using
the ``aiida-project create`` command (run ``aiida-project create --help`` for
further information on this command). For instance, to install a new environment
run
```
$ aiida-project create --manager conda --aiida 1.0.0 --python 3.6 --path /tmp aiida-env
```
The command shown above will install a new ``conda`` environment with
name ``aiida-env`` to ``/tmp/aiida-env`` running ``AiiDA v1.0.0`` using
``Python 3.6``.

### Activating a created environment

To activate a created environment the activate / deactivate commands need
to be made available first by running the following command
```
$ eval "$(aiida-project init bash)"
```
(Note that currently only ``bash`` is supported!) After running this
command AiiDA environments installed using ``aiida-project`` can be activated
by simply executing ``aiida-project activate`` followed by the environment
name you want to activate, i.e.
```
$ aiida-project activate aiida-env
```

### Deactivating loaded environments

To deactivate an activate environment run
```
$ aiida-project deactivate
```
without the environment name. This will deactivate the currently active
environment.
