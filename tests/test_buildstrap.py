#!/usr/bin/env python

#from tempfile import TemporaryDirectory

#from testfixtures import Replace, ShouldRaise, compare
#from testfixtures.popen import MockPopen

import pytest

from buildstrap.buildstrap import *

from pprint import pprint

def test_list():
    l_nil = []
    l_one = ['a']
    l_two = ['a', 'b']
    l_thr = ['a', 'b', 'c']

    lb_nil = ListBuildout([])
    lb_one = ListBuildout(['a'])
    lb_two = ListBuildout(['a', 'b'])
    lb_thr = ListBuildout(['a', 'b', 'c'])

    assert str(lb_nil) == str(l_nil)
    assert str(lb_one) == str(l_one)
    assert str(lb_two) == str(l_two)
    assert str(lb_thr) == str(l_thr)

    with ListBuildout.generate_context():
        assert str(lb_nil) != str(l_nil)
        assert str(lb_one) != str(l_one)
        assert str(lb_two) != str(l_two)
        assert str(lb_thr) != str(l_thr)

        assert str(lb_nil) == '\n'.join(l_nil)
        assert str(lb_one) == '\n'.join(l_one)
        assert str(lb_two) == '\n'.join(l_two)
        assert str(lb_thr) == '\n'.join(l_thr)


class TestFun__build_part_target:
    def test_build_part_target__target(self):
        assert build_part_target('a') == {
            'a': OrderedDict([
                    ('recipe', 'zc.recipe.egg'),
                    ('eggs', ['${buildout:requirements-eggs}'])
                ])
            }

    def test_build_part_target__target_one_pkg(self):
        assert build_part_target('a', ['b']) == {
            'a': OrderedDict([
                    ('recipe', 'zc.recipe.egg'),
                    ('eggs', ['${buildout:requirements-eggs}', 'b'])
                ])
            }

    def test_build_part_target__target_mult_pkg(self):
        assert build_part_target('a', ['b1', 'b2', 'b3', 'b4']) == {
            'a': OrderedDict([
                    ('recipe', 'zc.recipe.egg'),
                    ('eggs', ['${buildout:requirements-eggs}', 'b1', 'b2', 'b3', 'b4']),
                ])
            }

    def test_build_part_target__target_inter(self):
        assert build_part_target('a', interpreter='c') == {
            'a': OrderedDict([
                    ('recipe', 'zc.recipe.egg'),
                    ('eggs', ['${buildout:requirements-eggs}']),
                    ('interpreter', 'c')
                ])
            }

    def test_build_part_target__target_one_pkg_inter(self):
        assert build_part_target('a', ['b'], 'c') == {
            'a': OrderedDict([
                    ('recipe', 'zc.recipe.egg'),
                    ('eggs', ['${buildout:requirements-eggs}', 'b']),
                    ('interpreter', 'c')
                ])
            }

    def test_build_part_target__target_mult_pkg_inter(self):
        assert build_part_target('a', ['b1', 'b2', 'b3', 'b4'], 'c') == {
            'a': OrderedDict([
                    ('recipe', 'zc.recipe.egg'),
                    ('eggs', ['${buildout:requirements-eggs}', 'b1', 'b2', 'b3', 'b4']),
                    ('interpreter', 'c')
                ])
            }

##

class TestFun__build_part_template:
    def test_exists(self):
        assert build_part_template('pytest', '') == {
                'pytest': OrderedDict([
                    ('arguments', "['--cov={}/{}'.format('${buildout:develop}', "
                                 'package) for package in '
                                 "'${buildout:package}'.split(',')] \\\n"
                                 "+['--cov-report', 'term-missing', "
                                 "'tests']+sys.argv[1:]"),
                    ('eggs', '${buildout:requirements-eggs}'),
                    ('recipe', 'zc.recipe.egg'),
                ])
            }
        assert build_part_template('sphinx', '') == {
                'sphinx': OrderedDict([
                    ('build', '${buildout:directory}/doc/_build'),
                    ('eggs', '${buildout:requirements-eggs}'),
                    ('recipe', 'collective.recipe.sphinxbuilder'),
                    ('source', '${buildout:directory}/doc'),
                ])
            }

    def test_doesnotexists(self):
        with pytest.raises(FileNotFoundError):
            build_part_template('doesnotexists', '')

##

class TestFun__list_part_template:
    def test_list(self):
        assert list(list_part_templates('')) == ['pytest', 'sphinx']

##

class TestFun__build_part_buildout:
    def test_build_part_buildout__default_ordering(self):
        assert build_part_buildout() == {
                'buildout': OrderedDict([('newest', 'false'),
                    ('parts', ''),
                    ('package', ''),
                    ('extensions', 'gp.vcsdevelop'),
                    ('develop', '.'),
                    ('eggs-directory', '${buildout:directory}/var/eggs'),
                    ('develop-eggs-directory', '${buildout:directory}/var/develop-eggs'),
                    ('parts-directory', '${buildout:directory}/var/parts'),
                    ('develop-dir', '${buildout:directory}/var/develop'),
                    ('bin-directory', '${buildout:directory}/bin'),
                    ('requirements', [])
                    ])
                }

    def test_build_part_buildout__src(self):
        buildout_part = build_part_buildout(src_path='bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['develop']                == 'bar'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/var/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/var/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/var/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bin'

    def test_build_part_buildout__env(self):
        buildout_part = build_part_buildout(env_path='bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/bar/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/bar/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/bar/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bin'

    def test_build_part_buildout__absenv(self):
        buildout_part = build_part_buildout(env_path='/bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '/bar/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '/bar/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '/bar/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bin'

    def test_build_part_buildout__bin(self):
        buildout_part = build_part_buildout(bin_path='bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/var/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/var/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/var/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bar'

    def test_build_part_buildout__absbin(self):
        buildout_part = build_part_buildout(bin_path='/bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/var/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/var/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/var/parts'
        assert buildout_part['buildout']['bin-directory']          == '/bar'

    def test_build_part_buildout__root(self):
        buildout_part = build_part_buildout(root_path='/foo')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/var/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/var/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/var/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bin'

    def test_build_part_buildout__root_src(self):
        buildout_part = build_part_buildout(root_path='/foo', src_path='bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == 'bar'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/var/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/var/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/var/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bin'

    def test_build_part_buildout__root_env(self):
        buildout_part = build_part_buildout(root_path='/foo', env_path='bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/bar/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/bar/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/bar/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bin'

    def test_build_part_buildout__root_absenv(self):
        buildout_part = build_part_buildout(root_path='/foo', env_path='/bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '/bar/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '/bar/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '/bar/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bin'

    def test_build_part_buildout__root_bin(self):
        buildout_part = build_part_buildout(root_path='/foo', bin_path='bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/var/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/var/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/var/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bar'

    def test_build_part_buildout__root_absbin(self):
        buildout_part = build_part_buildout(root_path='/foo', bin_path='/bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/var/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/var/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/var/parts'
        assert buildout_part['buildout']['bin-directory']          == '/bar'

    def test_build_part_buildout__root_env_bin(self):
        buildout_part = build_part_buildout(root_path='/foo', env_path='bar', bin_path='bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/bar/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/bar/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/bar/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/bar'

    def test_build_part_buildout__root_env_absbin(self):
        buildout_part = build_part_buildout(root_path='/foo', env_path='bar', bin_path='/bar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '${buildout:directory}/bar/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '${buildout:directory}/bar/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '${buildout:directory}/bar/parts'
        assert buildout_part['buildout']['bin-directory']          == '/bar'

    def test_build_part_buildout__root_absenv_bin(self):
        buildout_part = build_part_buildout(root_path='/foo', env_path='/bar', bin_path='fubar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '/bar/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '/bar/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '/bar/parts'
        assert buildout_part['buildout']['bin-directory']          == '${buildout:directory}/fubar'

    def test_build_part_buildout__root_absenv_absbin(self):
        buildout_part = build_part_buildout(root_path='/foo', env_path='/bar', bin_path='/fubar')
        assert buildout_part['buildout']['newest']                 == 'false'
        assert buildout_part['buildout']['parts']                  == ''
        assert buildout_part['buildout']['directory']              == '/foo'
        assert buildout_part['buildout']['develop']                == '.'
        assert buildout_part['buildout']['eggs-directory']         == '/bar/eggs'
        assert buildout_part['buildout']['develop-eggs-directory'] == '/bar/develop-eggs'
        assert buildout_part['buildout']['parts-directory']        == '/bar/parts'
        assert buildout_part['buildout']['bin-directory']          == '/fubar'

class TestFun_build_parts:
    def get_buildout_part(self, packages, parts=[], requirements=[]):
        return OrderedDict([
            ('newest', 'false'),
            ('parts', parts),
            ('package', packages),
            ('extensions', 'gp.vcsdevelop'),
            ('directory', '.'),
            ('develop', '.'),
            ('eggs-directory', '${buildout:directory}/var/eggs'),
            ('develop-eggs-directory', '${buildout:directory}/var/develop-eggs'),
            ('parts-directory', '${buildout:directory}/var/parts'),
            ('develop-dir', '${buildout:directory}/var/develop'),
            ('bin-directory', '${buildout:directory}/bin'),
            ('requirements', [os.path.join('${buildout:develop}', r) for r in requirements]),
            ])

    def test_build_parts__packages_uniq__req_uniq(self):
        parts = build_parts(packages='a', requirements='b')
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a', parts=['a'], requirements=['b'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a']

    def test_build_parts__packages_uniq__req_list(self):
        parts = build_parts(packages='a', requirements=['b', 'c', 'd'])
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a', ['a'], ['b', 'c', 'd'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a']

    def test_build_parts__packages_uniq__req_lstr(self):
        parts = build_parts(packages='a', requirements='b,c,d')
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a', ['a'], ['b', 'c', 'd'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a']

    def test_build_parts__packages_list__req_uniq(self):
        parts = build_parts(packages=['a', 'x'], requirements='b')
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a x', ['a'], ['b'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a', 'x']

    def test_build_parts__packages_list__req_list(self):
        parts = build_parts(packages=['a', 'x'], requirements=['b', 'c', 'd'])
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a x', ['a'], ['b', 'c', 'd'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a', 'x']

    def test_build_parts__packages_list__req_lstr(self):
        parts = build_parts(packages=['a', 'x'], requirements='b,c,d')
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a x', ['a'], ['b', 'c', 'd'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a', 'x']

    def test_build_parts__packages_list__req_lstr(self):
        parts = build_parts(packages=['a', 'x'], requirements='b,c,d')
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a x', ['a'], ['b', 'c', 'd'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a', 'x']

    def test_build_parts__packages_lstr__req_uniq(self):
        parts = build_parts(packages='a,x', requirements='b')
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a x', ['a'], ['b'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a', 'x']

    def test_build_parts__packages_lstr__req_list(self):
        parts = build_parts(packages='a,x', requirements=['b', 'c', 'd'])
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a x', ['a'], ['b', 'c', 'd'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a', 'x']

    def test_build_parts__packages_lstr__req_lstr(self):
        parts = build_parts(packages='a,x', requirements='b,c,d')
        pprint(parts)
        assert parts['buildout'] == self.get_buildout_part('a x', ['a'], ['b', 'c', 'd'])
        assert parts['a']['recipe'] == 'zc.recipe.egg'
        assert parts['a']['eggs'] == ['${buildout:requirements-eggs}', 'a', 'x']

from contextlib import contextmanager

class UnitConfig:
    def __init__(self, args, internal, output):
        self.args = args
        self.internal = internal
        self.output = output

unit_config_list = {
        'config_show_buildstrap': UnitConfig(
        args={'--bin': 'bin',
              '--config': '~/.config/buildstrap',
              '--env': 'var',
              '--force': True,
              '--help': False,
              '--interpreter': 'python3',
              '--output': 'irrelevant',
              '--part': ['pytest', 'sphinx'],
              '--root': None,
              '--src': None,
              '--verbose': 0,
              '--version': False,
              '<package>': 'buildstrap',
              '<requirements>': ['requirements.txt', 'requirements-doc.txt', 'requirements-test.txt'],
              'debug': False,
              'generate': False,
              'run': False,
              'show': True},
        internal=OrderedDict([('buildout',
                OrderedDict([('newest', 'false'), 
                            ('parts', ListBuildout(['buildstrap', 'pytest', 'sphinx'])),
                            ('package', 'buildstrap'),
                            ('extensions', 'gp.vcsdevelop'),
                            ('develop', '.'),
                            ('eggs-directory', '${buildout:directory}/var/eggs'),
                            ('develop-eggs-directory', '${buildout:directory}/var/develop-eggs'),
                            ('parts-directory', '${buildout:directory}/var/parts'),
                            ('develop-dir', '${buildout:directory}/var/develop'),
                            ('bin-directory', '${buildout:directory}/bin'),
                            ('requirements', ListBuildout(['${buildout:develop}/requirements.txt', 
                                '${buildout:develop}/requirements-doc.txt', '${buildout:develop}/requirements-test.txt'])),
                            ])),
                ('buildstrap',
                OrderedDict([('recipe', 'zc.recipe.egg'),
                            ('eggs', ListBuildout(['${buildout:requirements-eggs}', 'buildstrap'])),
                            ('interpreter', 'python3')])),
                ('pytest',
                OrderedDict([('recipe', 'zc.recipe.egg'),
                            ('eggs', ListBuildout(['${buildout:requirements-eggs}'])),
                            ('interpreter', 'python3')])),
                ('pytest',
                 OrderedDict([
                              ('arguments', "['--cov={}/{}'.format('${buildout:develop}', "
                                            'package) for package in '
                                            "'${buildout:package}'.split(',')] \\\n"
                                            "+['--cov-report', 'term-missing', "
                                            "'tests']+sys.argv[1:]"),
                              ('eggs', ListBuildout(['${buildout:requirements-eggs}'])),
                              ('recipe', 'zc.recipe.egg'),
                              ])),
                ('sphinx',
                OrderedDict([
                            ('build', '${buildout:directory}/doc/_build'),
                            ('eggs', ListBuildout(['${buildout:requirements-eggs}'])),
                            ('recipe', 'collective.recipe.sphinxbuilder'),
                            ('source', '${buildout:directory}/doc'),
                            ])),
                ]),
        output="\n".join([
                '[buildout]',
                'newest = false',
                'parts = buildstrap',
                '	pytest',
                '	sphinx',
                'package = buildstrap',
                'extensions = gp.vcsdevelop',
                'develop = .',
                'eggs-directory = ${buildout:directory}/var/eggs',
                'develop-eggs-directory = ${buildout:directory}/var/develop-eggs',
                'parts-directory = ${buildout:directory}/var/parts',
                'develop-dir = ${buildout:directory}/var/develop',
                'bin-directory = ${buildout:directory}/bin',
                'requirements = ${buildout:develop}/requirements.txt',
                '	${buildout:develop}/requirements-doc.txt',
                '	${buildout:develop}/requirements-test.txt',
                '',
                '[buildstrap]',
                'recipe = zc.recipe.egg',
                'eggs = ${buildout:requirements-eggs}',
                '	buildstrap',
                'interpreter = python3',
                '',
                '[pytest]',
                "arguments = ['--cov={}/{}'.format('${buildout:develop}', package) for package in '${buildout:package}'.split(',')] \\",
                "	+['--cov-report', 'term-missing', 'tests']+sys.argv[1:]",
                'eggs = ${buildout:requirements-eggs}',
                'recipe = zc.recipe.egg',
                '',
                '[sphinx]',
                'build = ${buildout:directory}/doc/_build',
                'eggs = ${buildout:requirements-eggs}',
                'recipe = collective.recipe.sphinxbuilder',
                'source = ${buildout:directory}/doc',
                '',
                '',
            ])
    ),

    'config_show_min': UnitConfig(
        args={'--bin': 'bin',
              '--config': '~/.config/buildstrap',
              '--env': 'var',
              '--force': True,
              '--help': False,
              '--interpreter': None,
              '--output': 'irrelevant',
              '--part': [],
              '--root': None,
              '--src': None,
              '--verbose': 0,
              '--version': False,
              '<package>': 'buildstrap',
              '<requirements>': ['requirements.txt'],
              'debug': False,
              'generate': False,
              'run': False,
              'show': True},
        internal=OrderedDict([
                ('buildout',
                OrderedDict([('newest', 'false'),
                            ('parts', ListBuildout(['buildstrap'])),
                            ('package', 'buildstrap'),
                            ('extensions', 'gp.vcsdevelop'),
                            ('develop', '.'),
                            ('eggs-directory', '${buildout:directory}/var/eggs'),
                            ('develop-eggs-directory', '${buildout:directory}/var/develop-eggs'),
                            ('parts-directory', '${buildout:directory}/var/parts'),
                            ('develop-dir', '${buildout:directory}/var/develop'),
                            ('bin-directory', '${buildout:directory}/bin'),
                            ('requirements', '${buildout:develop}/requirements.txt'),
                            ])),
                ('buildstrap',
                OrderedDict([('recipe', 'zc.recipe.egg'),
                            ('eggs',
                                ListBuildout(['${buildout:requirements-eggs}', 'buildstrap']))])),
                            ]),
        output='\n'.join(['[buildout]',
                          'newest = false',
                          'parts = buildstrap',
                          'package = buildstrap',
                          'extensions = gp.vcsdevelop',
                          'develop = .',
                          'eggs-directory = ${buildout:directory}/var/eggs',
                          'develop-eggs-directory = ${buildout:directory}/var/develop-eggs',
                          'parts-directory = ${buildout:directory}/var/parts',
                          'develop-dir = ${buildout:directory}/var/develop',
                          'bin-directory = ${buildout:directory}/bin',
                          'requirements = ${buildout:develop}/requirements.txt',
                          '',
                          '[buildstrap]',
                          'recipe = zc.recipe.egg',
                          'eggs = ${buildout:requirements-eggs}',
                          '	buildstrap',
                          '',
                          '',
                    ])
    ),

    'config_show_min_path': UnitConfig(
        args={'--bin': '/bin',
              '--config': '~/.config/buildstrap',
              '--env': '/env',
              '--force': True,
              '--help': False,
              '--interpreter': None,
              '--output': 'irrelevant',
              '--part': [],
              '--root': '/root',
              '--src': '/src',
              '--verbose': 0,
              '--version': False,
              '<package>': 'buildstrap',
              '<requirements>': ['requirements.txt'],
              'debug': False,
              'generate': False,
              'run': False,
              'show': True},
        internal= OrderedDict([
             ('buildout',
              OrderedDict([('newest', 'false'),
                           ('parts', ListBuildout(['buildstrap'])),
                           ('package', 'buildstrap'),
                           ('extensions', 'gp.vcsdevelop'),
                           ('directory', '/root'),
                           ('develop', '/src'),
                           ('eggs-directory', '/env/eggs'),
                           ('develop-eggs-directory', '/env/develop-eggs'),
                           ('parts-directory', '/env/parts'),
                           ('develop-dir', '/env/develop'),
                           ('bin-directory', '/bin'),
                           ('requirements', '${buildout:develop}/requirements.txt'),
                           ])),
             ('buildstrap',
              OrderedDict([('recipe', 'zc.recipe.egg'),
                           ('eggs',
                            ListBuildout(['${buildout:requirements-eggs}', 'buildstrap']))])),
                           ]),
        output='\n'.join(['[buildout]',
                          'newest = false',
                          'parts = buildstrap',
                          'package = buildstrap',
                          'extensions = gp.vcsdevelop',
                          'directory = /root',
                          'develop = /src',
                          'eggs-directory = /env/eggs',
                          'develop-eggs-directory = /env/develop-eggs',
                          'parts-directory = /env/parts',
                          'develop-dir = /env/develop',
                          'bin-directory = /bin',
                          'requirements = ${buildout:develop}/requirements.txt',
                          '',
                          '[buildstrap]',
                          'recipe = zc.recipe.egg',
                          'eggs = ${buildout:requirements-eggs}',
                          '	buildstrap',
                          '',
                          ''])
    ),

    'config_debug_min': UnitConfig(
        args={'--bin': 'bin',
              '--config': '~/.config/buildstrap',
              '--env': 'var',
              '--force': True,
              '--help': False,
              '--interpreter': None,
              '--output': 'irrelevant',
              '--part': [],
              '--root': None,
              '--src': None,
              '--verbose': 0,
              '--version': False,
              '<package>': 'buildstrap',
              '<requirements>': ['requirements.txt'],
              'debug': True,
              'generate': False,
              'run': False,
              'show': False},
        internal=OrderedDict([
                ('buildout',
                OrderedDict([('newest', 'false'),
                            ('parts', ListBuildout(['buildstrap'])),
                            ('package', 'buildstrap'),
                            ('extensions', 'gp.vcsdevelop'),
                            ('develop', '.'),
                            ('eggs-directory', '${buildout:directory}/var/eggs'),
                            ('develop-eggs-directory', '${buildout:directory}/var/develop-eggs'),
                            ('parts-directory', '${buildout:directory}/var/parts'),
                            ('develop-dir', '${buildout:directory}/var/develop'),
                            ('bin-directory', '${buildout:directory}/bin'),
                            ('requirements', ListBuildout(['${buildout:develop}/requirements.txt']))])),
                ('buildstrap',
                OrderedDict([('recipe', 'zc.recipe.egg'),
                            ('eggs',
                                ListBuildout(['${buildout:requirements-eggs}', 'buildstrap']))])),
                            ]),
        output='\n'.join(['[buildout]',
                          'newest = false',
                          'parts = buildstrap',
                          'package = buildstrap',
                          'extensions = gp.vcsdevelop',
                          'develop = .',
                          'eggs-directory = ${buildout:directory}/var/eggs',
                          'develop-eggs-directory = ${buildout:directory}/var/develop-eggs',
                          'parts-directory = ${buildout:directory}/var/parts',
                          'develop-dir = ${buildout:directory}/var/develop',
                          'bin-directory = ${buildout:directory}/bin',
                          'requirements = ${buildout:develop}/requirements.txt',
                          '',
                          '[buildstrap]',
                          'recipe = zc.recipe.egg',
                          'eggs = ${buildout:requirements-eggs}',
                          '	buildstrap',
                          '',
                          '',
                          ])
    ),

    'config_run_min': UnitConfig(
        args={'--bin': 'bin',
              '--config': '~/.config/buildstrap',
              '--env': 'var',
              '--force': True,
              '--help': False,
              '--interpreter': None,
              '--output': 'test_file',
              '--part': [],
              '--root': None,
              '--src': None,
              '--verbose': 0,
              '--version': False,
              '<package>': 'buildstrap',
              '<requirements>': ['requirements.txt'],
              'debug': False,
              'generate': False,
              'run': True,
              'show': False},
        internal=OrderedDict([
                ('buildout',
                OrderedDict([('newest', 'false'),
                            ('parts', ListBuildout(['buildstrap'])),
                            ('package', 'buildstrap'),
                            ('extensions', 'gp.vcsdevelop'),
                            ('develop', '.'),
                            ('eggs-directory', '${buildout:directory}/var/eggs'),
                            ('develop-eggs-directory', '${buildout:directory}/var/develop-eggs'),
                            ('parts-directory', '${buildout:directory}/var/parts'),
                            ('develop-dir', '${buildout:directory}/var/develop'),
                            ('bin-directory', '${buildout:directory}/bin'),
                            ('requirements', '${buildout:develop}/requirements.txt')])),
                ('buildstrap',
                OrderedDict([('recipe', 'zc.recipe.egg'),
                            ('eggs',
                                ListBuildout(['${buildout:requirements-eggs}', 'buildstrap']))])),
                            ]),
        output='\n'.join(['[buildout]',
                          'newest = false',
                          'parts = buildstrap',
                          'package = buildstrap',
                          'extensions = gp.vcsdevelop',
                          'develop = .',
                          'eggs-directory = ${buildout:directory}/var/eggs',
                          'develop-eggs-directory = ${buildout:directory}/var/develop-eggs',
                          'parts-directory = ${buildout:directory}/var/parts',
                          'develop-dir = ${buildout:directory}/var/develop',
                          'bin-directory = ${buildout:directory}/bin',
                          'requirements = ${buildout:develop}/requirements.txt',
                          '',
                          '[buildstrap]',
                          'recipe = zc.recipe.egg',
                          'eggs = ${buildout:requirements-eggs}',
                          '	buildstrap',
                          '',
                          '',
                          ])
    )

}

import io
class StringIO(io.StringIO):
    def __enter__(self, *args, **kwarg):
        self.seek(0)
        self.truncate(0)
        return super(StringIO, self).__enter__(*args, **kwarg)

    def __exit__(self, *args, **kwarg):
        pass

class MockupsMixin:
    @contextmanager
    def mocked_open(self, target):
        import builtins
        import buildstrap.buildstrap

        buf = StringIO()
        orig_open = builtins.open

        def mock_open(fname, *args, **kwarg):
            if fname == target:
                # mimic open() by sending buffer as a generator
                return buf
            else:
                return orig_open(fname, *args, **kwarg)

        builtins.open = mock_open
        yield buf
        builtins.open = orig_open

    @contextmanager
    def mocked_os_path_exists(self, target, value):
        import os
        orig_exists = os.path.exists
        def mock_exists(f):
            if f == target:
                return value
            return orig_exists(f)
        os.path.exists = mock_exists
        yield
        os.path.exists = orig_exists

    @contextmanager
    def mocked_buildout(self):
        import buildstrap.buildstrap
        buildout_orig = buildstrap.buildstrap.buildout
        class MockBuildout:
            def __init__(self):
                self.ran = False
        b = MockBuildout()
        def mock_buildout(*args, **kwarg):
            b.ran = True
            return
        buildstrap.buildstrap.buildout = mock_buildout
        yield b
        buildstrap.buildstrap.buildout = buildout_orig


class TestFun_generate_buildout_config(MockupsMixin):
    def test__config__empty__stdout(self, capsys):
        generate_buildout_config(parts={}, output='-')
        out, err = capsys.readouterr()
        assert out == ''

    def test__config__dummy__stdout(self, capsys):
        generate_buildout_config(parts={'foobar': {'foo': 'bar'}}, output='-')
        out, err = capsys.readouterr()
        assert out == '[foobar]\nfoo = bar\n\n'

    def test__config__empty__file(self, capsys):
        with self.mocked_open('test_file') as buf:
            generate_buildout_config(parts={}, output='test_file')
            assert buf.getvalue() == ''

    def test__config__dummy__fileexists(self):
        with self.mocked_os_path_exists('test_file', True):
            with self.mocked_open('test_file') as buf:
                with pytest.raises(FileExistsError):
                    generate_buildout_config(parts={'foobar': {'foo': 'bar'}}, output='test_file')

    def test__config__dummy__fileexists_force(self):
        with self.mocked_os_path_exists('test_file', True):
            with self.mocked_open('test_file') as buf:
                generate_buildout_config(parts={'foobar': {'foo': 'bar'}}, output='test_file', force=True)
                assert buf.getvalue() == '[foobar]\nfoo = bar\n\n'

    def test__config__value__file(self, capsys):
        with self.mocked_buildout():
            with self.mocked_open('test_file') as buf:
                for name, config in unit_config_list.items():
                    if name.startswith('config_debug_'):
                        continue
                    generate_buildout_config(parts=config.internal, output='test_file')
                    assert buf.getvalue() == config.output

    def test__config__value__stdout(self):
        for name, config in unit_config_list.items():
            with self.mocked_open('test_file') as buf:
                # skip tests for debug command (out of scope for the tested function)
                generate_buildout_config(parts=config.internal, output='test_file')
                assert buf.getvalue() == config.output

class TestFun_test_buildstrap(MockupsMixin):
    def test_buildstrap(self, capsys):
        with self.mocked_buildout() as buildout_mock:
            for name, config in unit_config_list.items():
                with self.mocked_os_path_exists(config.args['--output'], True):
                    with self.mocked_open(config.args['--output']) as buf:
                        buildstrap(config.args)
                        out, err = capsys.readouterr()
                        if config.args['show']:
                            assert out == config.output
                        elif config.args['debug']:
                            import io
                            fake_out = io.StringIO()
                            pprint(config.internal, stream=fake_out)
                            assert out == fake_out.getvalue()
                        elif config.args['run']:
                            assert buildout_mock.ran == True
                            assert buf.getvalue() == config.output
                        else:
                            assert buf.getvalue() == config.output


