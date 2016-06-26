#!/usr/bin/env python

'''
Buildstrap: generate and run buildout in your projects ::

    Usage: {} [-v...] [options] [run|show|debug|generate] [-p part...]<package> <requirements>...

    Options:
        run                         run buildout once buildout.cfg has been generated
        show                        show the buildout.cfg (same as using `-o -`)
        debug                       print internal representation of buildout config
        generate                    create the buildout.cfg file (default action)
        <package>                   use this name for the package being developed
        <requirements>              use this requirements file as main requirements
        -p,--part <part>            choose part template to use (use "list" to show all)
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
        -c,--config <path>          path to the configuration directory
                                    [default: ~/.config/buildstrap]
        -v,--verbose                increase verbosity
        -h,--help                   show this message
        --version                   show version

For more detailed help, please read the documentation
on https://readthedocs.org/buildstrap
'''

import os, sys

from contextlib import contextmanager
from collections import OrderedDict
from configparser import ConfigParser
from pprint import pprint
from docopt import docopt

from zc.buildout.configparser import parse
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

def build_part_target(target, packages=list(), interpreter=None):
    '''Generates a part to run the currenctly develop package

    This will output a part, that will make a script based on the current package
    developed, using the ``zc.recipe.egg`` recipe, to populate the environment.
    The generated part follows the following template::

        [<target>]
        recipe=zc.recipe.egg
        eggs=<package>
        interpreter=<interpreter>

    If no ``packages`` argument is given, the list only contains the reference to
    the requirements egg list, otherwise the list of packages gets appended.
    If no interpreter argument is given, the directive is ignored.

    Args:
        target: name to be used for the part
        interpreter: if given, setup the interpreter directive, using the name
           of a python interpreter as a string.
        packages: if given, adds that package to the list of requirements.

    Raises:
        TypeError: if the packages is not a list of string

    Returns:
        dict representation of the part
    '''
    if not isinstance(packages, list):
        raise TypeError('packages argument should be a list!')

    eggs = [ '${buildout:requirements-eggs}' ]
    eggs += packages

    part = {
        target: OrderedDict([
            ('recipe' , 'zc.recipe.egg'),
            ('eggs'   , ListBuildout(eggs)),
        ])
    }

    if interpreter:
        part[target].update({'interpreter': interpreter})

    return part


def list_part_templates(config_path):
    '''Iterates over the available part templates

    Will get through both package's templates path and user config path to
    check for ``.part.cfg`` files.

    Args:
        config_path: path to the user's part template directory

    Returns:
        iterator over the list of templates

    '''
    user_config_path = os.path.join(os.path.expanduser(config_path))
    pkg_config_path = os.path.join(os.path.dirname(__file__), 'templates')

    templates = []
    if os.path.exists(pkg_config_path):
        templates += os.listdir(os.path.join(pkg_config_path))
        print('Using parts from {}'.format(pkg_config_path), file=sys.stderr)
    if os.path.exists(user_config_path):
        templates += os.listdir(user_config_path)
        print('Using parts from {}'.format(user_config_path), file=sys.stderr)

    for fname in templates:
        if 'list' in fname:
            print('Warning: a part template named list.cfg exists, and cannot be called. Please change its name!', file=sys.stderr)
        if '.part.cfg' in fname:
            yield fname.replace('.part.cfg', '')
        else:
            print('Warning: file named {} does not end with .part.cfg and is ignored!'.format(fname), file=sys.stderr)

def build_part_template(name, config_path):
    '''Creates a part out of a template file

    Will resolve a part file based on its name, by looking through both package's
    static directory, and through user defined configuration path.

    The template file will feature a section (which name is the same as the file name)
    and will be parsed, and then added to the buildout file *as is*. It will also be
    named with the ``.part.cfg`` extension.

    Args:
        name: name of the template file (without extension)
        config_path: directory where to look for the template file

    Returns:
        dict representation of a part

    Raises:
        FileNotFoundError if no template can be found.
    '''
    template_name = '{}.part.cfg'.format(name)
    template_path = os.path.join(os.path.expanduser(config_path))

    try:
        template_file = open(template_path, 'r')
    except FileNotFoundError:
        try:
            template_path = os.path.join(os.path.dirname(__file__), 'templates', template_name)
            template_file = open(template_path, 'r')
        except FileNotFoundError:
            template_file = None

    if not template_file:
        raise FileNotFoundError('Missing template file {}.part.cfg in {}'.format(name, config_path))

    res = parse(open(template_path, 'r'), name)
    # make items order predictible
    for k,v in res.items():
        if isinstance(v, dict):
            res[k] = OrderedDict(sorted(v.items(), key=lambda t: t[0]))
    return res

def build_part_buildout(root_path=None, src_path=None, env_path=None, bin_path=None):
    '''Generates the buildout part

    This part is the entry point of a buildout configuration file, setting up
    general values for the environment. Here we setup paths and defaults for
    buildout's behaviour. Please refer to buildout documentation for more.

    This will output a buildout header that can be considered as a good start::

        [buildout]
        newest=false
        parts=
        package=
        extensions=gp.vcsdevelopc
        directory=.
        develop=${buildout:directory}
        eggs-directory=${buildout:directory}/var/eggs
        develop-eggs-directory=${buildout:directory}/var/develop-eggs
        develop-dir=${buildout:directory}/var/develop
        parts-directory=${buildout:directory}/var/parts
        requirements=

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
    buildout['package'] = ''
    buildout['extensions'] = 'gp.vcsdevelop'
    if root_path:
        buildout['directory'] = root_path
    if not env_path:
        env_path = 'var'
    if not os.path.isabs(env_path):
            env_path = os.path.join('${buildout:directory}', env_path)
    if not bin_path:
        bin_path = 'bin'
    if not os.path.isabs(bin_path):
        bin_path = os.path.join('${buildout:directory}', bin_path)
    buildout['develop'] = src_path if src_path else '.'
    buildout['eggs-directory'] = os.path.join(env_path, 'eggs')
    buildout['develop-eggs-directory'] = os.path.join(env_path, 'develop-eggs')
    buildout['parts-directory'] = os.path.join(env_path, 'parts')
    buildout['develop-dir'] = os.path.join(env_path, 'develop')
    buildout['bin-directory'] = bin_path
    buildout['requirements'] = ListBuildout([])
    return {'buildout': buildout}


def build_parts(packages, requirements, part_templates=[], interpreter=None, 
        config_path=None, root_path='.', src_path=None, env_path=None, bin_path=None):
    '''Builds up the different parts of the buildout configuration

    this is the workhorse of this code. It will build and return an internal
    dict representation of a buildout configuration, following the values given
    by the arguments. The buildout configuration can be seen as a succession of
    parts, each one being a section in the configuration file. For more, please
    refer to buildout's documentation.

    First, it generates the ``[buildout]`` part within the dict representation.
    Within it, it will setup the ``packages`` value so we keep track of which
    packages you want to build, the ``requirements`` value will be used to find
    and download all the eggs that are needed as dependencies. the ``parts`` list
    will keep track of each generated part, only one part being generated for the
    code under development (even if there are several packages).

    The first argument will define the first part's name (the one that will be
    used to generate a script if an entry point has been defined within the ``setup.py``).
    Thus, it will append the package name to the list of packages within the ``[buildout]``
    section, and be added to the list of eggs that will be run::

        [buildout]
        package = marvin
        parts = marvin
        …
        

        [marvin]
        recipe = zc.recipe.egg
        eggs = ${buildout:requirements-eggs}
             marvin

    The second argument is the list of requirements to be parsed and fed to ``gp.vcsdevelop``
    so it can work out downloading all your dependencies::

        [buildout]
        requirements = requirements.txt
        …

    Both can be lists (or comma separated list — as a *string*) of package names and
    requirements files, so if you give packages and requirements being respectively:

     * ``dent,prefect,beeblebrox`` and
     * ``requirements.txt,requirements-dev.txt``

    it will generate::

        [buildout]
        …
        parts = marvin
        package = marvin prefect beeblebrox
        requirements = requirements.txt
                requirements-dev.txt

        [marvin]
        recipe = zc.recipe.egg
        eggs = ${buildout:requirements-eggs}
             marvin

    The third argument enables to load a part template. It will load the part from
    the static path within the package, or from ``config_path``, which defaults to
    the user's home config directory.

    Args:
        packages: the list of packages to target as first part (list or comma separated string)
        requirements: the list of requirements to target as first part (list or comma separated string)
        part_templates: list of templates to load
        interpreter: string name of the python interpreter to use
        config_path: path string to the configuration directory where to find the template parts files.
        root_path: path string to the root of the project (from which all other paths are relative to)
        src_path: path string to the sources (where ``setup.py`` is)
        env_path: path string to the environment (where dependencies are downloaded)
        bin_path: path string to the runnable scripts

    Returns:
        OrderedDict instance configured with all parts.
    '''
    parts = OrderedDict()
    targets = []

    if not isinstance(packages, list):
        packages = packages.split(',')

    if not isinstance(requirements, list):
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

    parts.update(build_part_target(first_part_name, packages, interpreter))

    for template_name in part_templates or []:
        parts[template_name] = build_part_template(template_name, config_path)[template_name]
        targets.append(template_name)

    for r in requirements:
        parts['buildout']['requirements'] += ListBuildout([os.path.join('${buildout:develop}', r)])
    parts['buildout']['parts'] = ListBuildout(targets)
    parts['buildout']['package'] = ' '.join(packages)

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
            raise FileExistsError('\n'.join([
                    'Cannot overwrite {}: file already exists! Use --force if necessary.'.format(output),
                    'As a buildout configuration exists, you might want to run buildout directly!'
                    ]))

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
        if args['--verbose'] >= 2: # pragma: no cover
            print(args, file=sys.stderr)

        parts = build_parts(
                args['<package>'],
                args['<requirements>'],
                args['--part'],
                args['--interpreter'],
                args['--config'],
                args['--root'],
                args['--src'],
                args['--env'],
                args['--bin'])

        if args['debug']:
            pprint(parts)
            return 0

        if args['show']:
            args['--output'] = '-'

        generate_buildout_config(parts, args['--output'], args['--force'])

        if args['run']:
            buildout(['-c', args['--output']])

        return 0
    except Exception as err: # pragma: no cover
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
