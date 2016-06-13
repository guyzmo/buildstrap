#!/usr/bin/env python

"""
Buildstrap: generate and run buildout in your projects

Usage: {} [-v...] [run] [-i <interpreter>] [-f] [-o <buildout.cfg>] <package> <requirements> [<target>=<requirements>...]

Options:
    run                         run buildout once buildout.cfg has been generated
    <package>                   use this name for the package being developed
    <requirements>              use this requirements file as main requirements
    <target>=<requirements>     create a target with given requirements
    -i,--interpreter <python>   use this python version
    -o,--output <buildout.cfg>  file to output [default: buildout.cfg]
    -f,--force                  force overwrite output file if it exists
    -v,--verbose                increase verbosity
    -h,--help                   show this message
    --version                   show version

"""

import os, sys

from collections import OrderedDict
from configparser import ConfigParser
from pprint import pprint
from docopt import docopt

from zc.buildout.buildout import main as buildout

def get_partname_pip(target, requirements):
    return '{}-{}'.format(target, requirements)

def get_list_arg(list_arg):
    if len(list_arg) == 1:
        return list_arg[0]
    else:
        return '\n'.join(list_arg)

def build_part_pip(target, requirements):
    return {
        get_partname_pip(target, requirements): OrderedDict(
            recipe  = 'collective.recipe.pip',
            configs = get_list_arg(requirements.split(','))
        )
    }

def build_part_target(target, requirements, interpreter, package=None):
    partname_pip = get_partname_pip(target, requirements)
    eggs = [ '${{{}:eggs}}'.format(partname_pip) ]
    if package:
        eggs.append(package)

    part = {
        target: OrderedDict(
            recipe = 'zc.recipe.egg',
            eggs   = get_list_arg(eggs)
        )
    }

    if interpreter:
        part[target].update({'interpreter': interpreter})

    return part

def build_part_buildout():
    buildout = OrderedDict()
    buildout['newest'] = 'false'
    buildout['parts'] = ''
    buildout['develop'] = '.'
    buildout['eggs-directory'] = '${buildout:directory}/var/eggs'
    buildout['develop-eggs-directory'] = '${buildout:directory}/var/develop-eggs'
    buildout['parts-directory'] = '${buildout:directory}/var/parts'
    return {'buildout': buildout}


def buildstrap(args):
    try:
        pips = OrderedDict()
        parts = OrderedDict()
        targets = []

        parts.update(build_part_buildout())

        # build main package part
        parts.update(
                build_part_target(args['<package>'], args['<requirements>'],
                    args['--interpreter'], args['<package>'])
                )
        targets.append(args['<package>'])
        # build main package requirements
        pips.update(build_part_pip(args['<package>'], args['<requirements>']))

        for arg in args['<target>=<requirements>']:
            target, requirements = arg.split('=')
            targets.append(target)
            # add parts
            pips.update(build_part_pip(target, requirements))
            parts.update(build_part_target(target, requirements, args['--interpreter']))

        parts['buildout']['parts'] = get_list_arg(targets)
        parts.update(pips)

        parser = ConfigParser()
        parser.read_dict(parts)
        if args['--output'] == '-':
            parser.write(sys.stdout)
            return 0

        if not args['--force'] and os.path.exists(args['--output']):
            raise FileExistsError('Cannot overwrite {}: file already exists! Use --force if necessary.'.format(args['--output']))

        with open(args['--output'], 'w') as out:
            parser.write(out)

        if args['run']:
            buildout(['-c', args['--output']])

        return 0
    except Exception as err:
        print('Fatal error: {}'.format(err))
        if args['--verbose']:
            print('-----------------------------------')
            import traceback
            traceback.print_exc()


def run():
    sys.exit(buildstrap(docopt(__doc__)))


if __name__ == "__main__":
    run()
