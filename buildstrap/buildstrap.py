#!/usr/bin/env python

'''
Buildstrap: generate and run buildout in your projects

::

    Usage: {} [-v...] [run|show] [options] <package> <requirements> [<target>=<requirements>...]

    Options:
        run                         run buildout once buildout.cfg has been generated
        show                        show the buildout.cfg (same as using `-o -`)
        <package>                   use this name for the package being developed
        <requirements>              use this requirements file as main requirements
        <target>=<requirements>     create a target with given requirements
        -i,--interpreter <python>   use this python version
        -o,--output <buildout.cfg>  file to output [default: buildout.cfg]
        -r,--root <path>            path to the project root (where buildout.cfg will
                                    be generated) (defaults to ./)
        -s,--src <path>             path to the sources (default is same as root path)
                                    relative to the root path if not absolute
        -e,--env <path>             path to the environment data [default: var]
                                    relative to directory if not absolute
        -b,--bin <path>             path to the bin directory [default: bin]
                                    relative to directory if not absolute
        -f,--force                  force overwrite output file if it exists
        -v,--verbose                increase verbosity
        -h,--help                   show this message
        --version                   show version

For more detailed help, please read the documentation:

::

    man buildstrap

or on https://readthedocs.org/buildstrap
'''

import os, sys

from contextlib import contextmanager
from collections import OrderedDict
from configparser import ConfigParser
from pprint import pprint
from docopt import docopt

from zc.buildout.buildout import main as buildout

import pkg_resources

__version__ = pkg_resources.require('buildstrap')[0].version

class ListBuildout(list):
    '''Makes it possible to print a list the way buildout expects it.

    Because buildout uses a custom built parser for parsing ini style files,
    that has a major difference in list handling from the standard config
    parser.

    The standard configparser doesn't anything about lists, and outputs
    python's internal representation of strings: ``['a', 'b', 'c']`` as values.
    And the standard configparser consider multiline values as a multiline
    string.

    On the other hand, buildout considers multiline values as lists, one value
    per line.

    This class uses a context manager to define the behaviour of the string conversion
    method. The default behaviour is the same as the standard list. But when within
    the context of the ``generate_context`` method, it prints lists as multiline string,
    one value per line, the way buildout expects it.
    '''
    _generating_state = False

    @classmethod
    @contextmanager
    def generate_context(cls):
        '''Context manager to change the string conversion behaviour on this class'''
        cls._generating_state = True
        yield
        cls._generating_state = False

    def __str__(self):
        '''Replaces standard behaviour of list string output, so it prints as buildout
        expects when generating the buildout file'''
        if self._generating_state is True:
            if len(self) == 1:
                return self[0]
            else:
                return '\n'.join(self)
        else:
            return super(ListBuildout, self).__str__()

def build_part_pip(target, requirements):
    '''Generates the dict representation of the part that will parse the requirements

    This will output a part that uses the ``collective.recipe.pip`` recipe to
    parse the requirements as expose it as the eggs attribute of the part.

    ::

        [<target>-pip]
        recipe=collective.recipe.pip
        configs=<requirements>

    Multiple requirements can be used, separated by commas.

    Args:
        target: name of the part's role
        requirements: list of file names of the requirements to parse

    Returns:
        dict representation of the part

    '''
    return {
        '{}-pip'.format(target): OrderedDict(
            recipe  = 'collective.recipe.pip',
            configs = ListBuildout(['${{buildout:develop}}/{}'.format(r) for r in requirements])
        )
    }

def build_part_target(target, packages=list(), interpreter=None):
    '''Generates a part that will export requirements as eggs

    This will output a part that export the eggs parsed by the 'pip' part using the
    ``zc.recipe.egg`` recipe, to populate the environment. The generated part follows
    the following template::

        [<target>]
        recipe=zc.recipe.egg
        eggs=${<target>-pip:eggs}
             <packages>
        interpreter=<interpreter>

    If no ``packages`` argument is given, the list only contains the reference to
    the requirements egg list, otherwise the list of packages gets appended.
    If no interpreter argument is given, the directive is ignored.

    Args:
        target: name to be used for the part
        interpreter: if given, setup the interpreter directive, using the name
           of a python interpreter as a string.
        packages: if given, adds that package to the list of requirements.

    Returns:
        dict representation of the part
    '''
    eggs = [ '${{{}-pip:eggs}}'.format(target) ]
    eggs += packages

    part = {
        target: OrderedDict(
            recipe = 'zc.recipe.egg',
            eggs   = ListBuildout(eggs)
        )
    }

    if interpreter:
        part[target].update({'interpreter': interpreter})

    return part

def build_part_buildout(root_path='.', src_path=None, env_path=None, bin_path=None):
    '''Generates the buildout part

    This part is the entry point of a buildout configuration file, setting up
    general values for the environment. Here we setup paths and defaults for
    buildout's behaviour. Please refer to buildout documentation for more.

    This will output a buildout header that can be considered as a good start::

        [buildout]
        newest=false
        parts=
        directory=.
        develop=${buildout:directory}
        eggs-directory=${buildout:directory}/var/eggs
        develop-eggs-directory=${buildout:directory}/var/develop-eggs
        parts-directory=${buildout:directory}/var/parts

    Parameter ``root_path`` will change the path to the project's root, which is where
    the enviroment will be based on. If you're placing the ``buildout.cfg`` file in another
    directory than the root of the project, set it to the path that can get you from
    the buildout.cfg into the project, and it will all work ok.

    Parameter ``src_path`` will change the path to the sources, so if you've got your
    sources in ``./src``, you can set it up to src and it will generate::

        develop=./src

    Beware that all non-absolute paths given to ``src_path`` are relative to the
    ``root_path``.

    For parameter ``bin_path`` and ``env_path``, it will respectively change path to the
    generated ``bin`` directory and ``env`` directory, after running buildout.

    Args:
        root_path: path string to the root of the project (from which all other paths are relative to)
        src_path: path string to the sources (where ``setup.py`` is)
        env_path: path string to the environment (where dependencies are downloaded)
        bin_path: path string to the runnable scripts

    Returns:
        the buildout part as a dict
    '''
    buildout = OrderedDict()
    buildout['newest'] = 'false'
    buildout['parts'] = ''
    if root_path:
        buildout['directory'] = root_path
    if not env_path:
        env_path = os.path.join('${buildout:directory}', 'var')
    if not os.path.isabs(env_path):
            env_path = os.path.join('${buildout:directory}', env_path)
    if not bin_path:
        bin_path = os.path.join('${buildout:directory}', 'bin')
    if not os.path.isabs(bin_path):
        bin_path = os.path.join('${buildout:directory}', bin_path)
    buildout['develop'] = src_path if src_path else '.'
    buildout['eggs-directory'] = os.path.join(env_path, 'eggs')
    buildout['develop-eggs-directory'] = os.path.join(env_path, 'develop-eggs')
    buildout['parts-directory'] = os.path.join(env_path, 'parts')
    buildout['bin-directory'] = bin_path
    return {'buildout': buildout}

def build_parts(packages, requirements, extra_requirements=[], interpreter=None,
        root_path='.', src_path=None, env_path=None, bin_path=None):
    '''Builds up the different parts of the buildout configuration

    this is the workhorse of this code. It will build and return an internal
    dict representation of a buildout configuration, following the values given
    by the arguments. The buildout configuration can be seen as a succession of
    parts, each one being a section in the configuration file. For more, please
    refer to buildout's documentation.

    First, it generates the ``[buildout]`` part within the dict representation.

    Then it generates the parts that will follow the ``zc.recipe.egg`` to build
    the environment once buildout is called. Those will refer to what we call
    the ``pip`` parts that are parsing requirements files and exposing the
    dependencies to be used.

    The first two arguments are defining the minimal possible configuration,
    which is a single part (matching a single requirements file). Not having it
    would not mean much for the buildout configuration, thus the requirement of
    those two parameters.

    So the first part to be generated is the one defined by ``packages`` and
    ``requirements`` parameters. If both contain a single element (``marvin`` and
    ``requirements.txt``), it will output that part as the dict equivalent of::

        [marvin-pip]
        recipe=collective.recipe.pip
        configs=requirements.txt

        [marvin]
        recipe=zc.recipe.egg
        eggs=${marvin-eggs}
             package_name

    But both can be comma separated list (as a *string*) of package names and
    requirements files, so if you give packages and requirements being
    respectively:

     * ``dent,prefect,beeblebrox`` and
     * ``requirements.txt,requirements-dev.txt``

    it will generate::

        [dent-pip]
        recipe=collective.recipe.pip
        configs=requirements.txt
                requirements-dev.txt

        [dent]
        recipe=zc.recipe.egg
        eggs=${foobar-eggs}
             dent
             prefect
             beeblebrox

    Then you have the ``extra_requirements`` that are following the following format:
    ``<part_name>=<requirements>``. The ``<part_name>`` side here will be excusively used as a
    name for the part (so they can be anything), and the ``<requirements>`` side is a comma
    separated list of requirements files.

    So for example, you could have ``test=requirements-test.txt`` that would result in::

        [test-pip]
        recipe=collective.recipe.pip
        configs=requirements-test.txt

        [test]
        recipe=zc.recipe.egg
        eggs=${test-eggs}

    And if you specify more, like with:

    * ``['test=requirements.txt,requirements-test.txt', 'doc=requirements-doc.txt']``

    it will generate::

        [test-pip]
        recipe=collective.recipe.pip
        configs=requirements.txt,
                requirements-test.txt

        [test]
        recipe=zc.recipe.egg
        eggs=${test-eggs}

        [doc-pip]
        recipe=collective.recipe.pip
        configs=requirements-test.txt

        [doc]
        recipe=zc.recipe.egg
        eggs=${doc-eggs}

    Finally, as each part is being generated, it's also added to the list of parts
    to be ran by buildout, so for the last example, the ``parts`` attribute of the
    ``buildout`` dict will be like::

        [buildout]
        …
        parts=test
              doc

    Args:
        packages: the list of packages to target as first part (list or comma separated string)
        requirements: the list of requirements to target as first part (list or comma separated string)
        extra_requirements: the list of other parts, formated as ``part_name=requirements``
         where requirements is a comma separated list of requirements.
        interpreter: string name of the python interpreter to use
        root_path: path string to the root of the project (from which all other paths are relative to)
        src_path: path string to the sources (where ``setup.py`` is)
        env_path: path string to the environment (where dependencies are downloaded)
        bin_path: path string to the runnable scripts

    Returns:
        dict instance configured with all parts.
    '''
    pips = OrderedDict()
    parts = OrderedDict()
    targets = []

    if not isinstance(packages, list):
        packages = packages.split(',')

    if not isinstance(packages, list):
        requirements = requirements.split(',')

    if len(packages) == 0:
        raise ValueError("There shall be at least one package to setup.")

    if len(requirements) == 0:
        raise ValueError("There shall be at least one requirement to setup.")

    first_part_name = packages[0]

    parts.update(build_part_buildout(root_path, src_path, env_path, bin_path))

    # build main package part
    parts.update(build_part_target(first_part_name, packages, interpreter))
    targets.append(first_part_name)
    # build main package requirements
    pips.update(build_part_pip(first_part_name, requirements.split(',')))

    for arg in extra_requirements:
        target, requirements = arg.split('=')
        targets.append(target)
        # add parts
        pips.update(build_part_pip(target, requirements.split(',')))
        parts.update(build_part_target(target, interpreter=interpreter))

    parts['buildout']['parts'] = ListBuildout(targets)
    parts.update(pips)

    return parts

def generate_buildout_config(parts, output, force=False):
    '''Generates the buildout configuration

    Using the custom ``ListBuildout`` context, lists will be printed as multilines.
    If output is set to ``-`` it will print to stdout the file.

    Args:
        parts: dict based representation of the buildout file to generate
        output: name of the file to output
        force: if set, it won't care whether the file exists

    Raises:
        FileExistsError: when a file already exists.
    '''
    with ListBuildout.generate_context():
        parser = ConfigParser()
        parser.read_dict(parts)

        if output == '-':
            parser.write(sys.stdout)
            return

        if not force and os.path.exists(output):
            raise FileExistsError('Cannot overwrite {}: file already exists! Use --force if necessary.'.format(output))

        with open(output, 'w') as out:
            parser.write(out)

def buildstrap(args):
    '''Parses the command line arguments, build the parts, generate the config and runs buildout

    refer to the __doc__ of this module for all arguments.

    Args:
        args: arguments to parse

    Returns:
        0 on success, 1 otherwise
    '''
    try:
        if args['--verbose'] >= 2:
            print(args, file=sys.stderr)

        parts = build_parts(
                args['<package>'],
                args['<requirements>'],
                args['<target>=<requirements>'],
                args['--interpreter'],
                args['--root'],
                args['--src'],
                args['--env'],
                args['--bin'])

        if args['show']:
            args['--output'] = '-'

        generate_buildout_config(parts, args['--output'], args['--force'])

        if args['run']:
            buildout(['-c', args['--output']])

        return 0
    except Exception as err:
        print('Fatal error: {}'.format(err), file=sys.stderr)
        if args['--verbose']:
            print('-----------------------------------', file=sys.stderr)
            import traceback
            traceback.print_exc()
        return 1


def run(): # pragma: no cover
    '''Parses arguments, gets current command name and version number'''
    sys.exit(buildstrap(docopt(__doc__.format(os.path.basename(sys.argv[0])),
        version='Buildstrap v{}'.format(__version__))))


if __name__ == "__main__": # pragma: no cover
    '''well there's always a good place to start'''
    run()
