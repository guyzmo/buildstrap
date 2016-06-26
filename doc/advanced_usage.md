# Usage

```
Usage: buildstrap [-v...] [options] [run|show|debug|generate] [-p part...]<package> <requirements>...

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
```

# Multiple requirements.txt

Many projects offer multiple `requirements.txt` files, one for each task of
the development cycle (which usually are running, testing, documenting).

Well, just tell buildstrap what the extra requirements are:

```
% buildstrap run buildstrap -p pytest -p sphinx requirements.txt requirements-doc.txt requirements-test.txt
```

and that will generate the following buildout.cfg configuration:

```
[buildout]
newest = false
parts = buildstrap
        pytest
        sphinx
package = buildstrap
extensions = gp.vcsdevelop
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
develop-dir = ${buildout:directory}/var/develop
bin-directory = ${buildout:directory}/bin
requirements = ${buildout:develop}/requirements.txt
        ${buildout:develop}/requirements-doc.txt
        ${buildout:develop}/requirements-test.txt

[buildstrap]
recipe = zc.recipe.egg
eggs = ${buildout:requirements-eggs}
        buildstrap

[pytest]
arguments = ['--cov={}/{}'.format('${buildout:develop}', package) for package in '${buildout:pack
age}'.split(',')] \
        +['--cov-report', 'term-missing', 'tests']+sys.argv[1:]
eggs = ${buildout:requirements-eggs}
recipe = zc.recipe.egg

[sphinx]
eggs = ${buildout:requirements-eggs}
source = ${buildout:directory}/doc
recipe = collective.recipe.sphinxbuilder
build = ${buildout:directory}/doc/_build
```

and you'll find all the tools you'll need in bin:

```
% ls bin
buildout    cm2html   cm2man        cm2xetex  py.test      sphinx         sphinx-autogen  sphinx-quickstart
buildstrap  cm2latex  cm2pseudoxml  cm2xml    py.test-2.7  sphinx-apidoc  sphinx-build
```

# Multiple packages

Some projects will include several packages in the sources, so to support that, just list
all your packages as a comma seperated list, and they will all be included:

```
% buildstrap show dent,prefect,beeblebox requirements.txt
[buildout]
newest = false
parts = dent
package = dent prefect beeblebox
extensions = gp.vcsdevelop
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
develop-dir = ${buildout:directory}/var/develop
bin-directory = ${buildout:directory}/bin
requirements = ${buildout:develop}/requirements.txt

[dent]
recipe = zc.recipe.egg
eggs = ${buildout:requirements-eggs}
        dent
        prefect
        beeblebox
```

Control the output
------------------

If you want to only generate the `buildout.cfg` file, simply use buildstrap with
no subcommand, and you'll get it in your current directory!

```
% buildstrap slartibartfast requirements.txt
% cat buildout.cfg
[buildout]
newest = false
parts = slartibartfast
package = slartibartfast
extensions = gp.vcsdevelop
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
develop-dir = ${buildout:directory}/var/develop
bin-directory = ${buildout:directory}/bin
requirements = ${buildout:develop}/requirements.txt

[slartibartfast]
recipe = zc.recipe.egg
eggs = ${buildout:requirements-eggs}
        slartibartfast

```

but if you want to just test the command and print the configuration to stdout,
without it doing nothing, use the `show` subcommand:

```
% buildstrap show slartibartfast requirements.txt
[buildout]
newest = false
parts = slartibartfast
package = slartibartfast
extensions = gp.vcsdevelop
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
develop-dir = ${buildout:directory}/var/develop
bin-directory = ${buildout:directory}/bin
requirements = ${buildout:develop}/requirements.txt

[slartibartfast]
recipe = zc.recipe.egg
eggs = ${buildout:requirements-eggs}
        slartibartfast

```

and if you want to write the `buildout.cfg` as another file, you can either redirect
the show command with a pipe, or use the `--output` argument:

```
% buildstrap -o foobar.cfg slartibartfast requirements.txt
% cat foobar.cfg
[buildout]
newest = false
parts = slartibartfast
package = slartibartfast
extensions = gp.vcsdevelop
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
develop-dir = ${buildout:directory}/var/develop
bin-directory = ${buildout:directory}/bin
requirements = ${buildout:develop}/requirements.txt

[slartibartfast]
recipe = zc.recipe.egg
eggs = ${buildout:requirements-eggs}
        slartibartfast

```

N.B.: the show command is equivalent to `--output -`.

# Configure the path

For your project, there are three important path to configure:

* where your project root is,
* where your sources are (within your project),
* where your environment will be.

When you're using buildstrap on a project, the default are safe, as long as you're
running while you're doing it within the sources of the project. Then what you'll have
is:

* `root_path` → '.'
* `src_path` → `{root_path}` → '.'
* `env_path` → `{root_path}/var` → './var'
* `bin_path` → `{root_path}/bin` → './bin'

But sometimes, you want to change the defaults, for the best (or the worst
— most often, the worst, though).

So, you can set all those paths to values other than the default, and have it
all in a very different setup than the default.

## Root path: `--root`

The project's root is where typically all other paths are being relative to.
It's where you'll expect to find the `buildout.cfg` file, and where the
environment directory will be.

When passed, it's setting up the `directory` directive of the `buildout.cfg`
file, otherwise it's keeping the default.

```
% buildstrap -r /tmp/buildstrap-env/ show buildstrap requirements.txt
[buildout]
newest = false
parts = buildstrap
package = buildstrap
extensions = gp.vcsdevelop
directory = /tmp/buildstrap-env/
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
develop-dir = ${buildout:directory}/var/develop
bin-directory = ${buildout:directory}/bin
requirements = ${buildout:develop}/requirements.txt

[buildstrap]
recipe = zc.recipe.egg
eggs = ${buildout:requirements-eggs}
        buildstrap
```

## Sources path: `--src`

Though, if you change the root directory, chances are (like in the former example) that
it won't be where your sources are. Then, running `buildout` will end up in throwing an
exception:

    FileNotFoundError: [Errno 2] No such file or directory: '/tmp/builstrap-env/./setup.py'

The source path is where you'll have your `setup.py` file that defines your project.
So, if your `setup.py` is not at the root of your project, you definitely want to
use the `--src` argument.

```
% buildstrap -r /tmp/buildstrap-build -s `pwd`/buildstrap show buildstrap requirements.txt
[buildout]
newest = false
parts = buildstrap
package = buildstrap
extensions = gp.vcsdevelop
directory = /tmp
develop = /absolute/path/to/buildstrap
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
develop-dir = ${buildout:directory}/var/develop
bin-directory = ${buildout:directory}/bin
requirements = ${buildout:develop}/requirements.txt

[buildstrap]
recipe = zc.recipe.egg
eggs = ${buildout:requirements-eggs}
        buildstrap

```

*Nota Bene*: if you do not want to use a path relative to the `root` path, then
use an absolute path, or you'll have surprises! As you can see in the example above
the path is made absolute by using the `pwd` command.

So running this command with buildout will do:

```
% buildout
Creating directory '/tmp/buildstrap-build/var/eggs'.
Getting distribution for 'gp.vcsdevelop'.
warning: no previously-included files matching '*' found under directory 'docs/_build'
Got gp.vcsdevelop 2.2.3.
Creating directory '/tmp/buildstrap-build/bin'.
Creating directory '/tmp/buildstrap-build/var/parts'.
Creating directory '/tmp/buildstrap-build/var/develop-eggs'.
Develop: '/home/guyzmo/Workspace/Projects/buildstrap'
Getting distribution for 'zc.recipe.egg>=2.0.0a3'.
Got zc.recipe.egg 2.0.3.
Unused options for buildout: 'package'.
Installing buildstrap.
Generated script '/tmp/buildstrap-build/bin/buildout'.
Generated script '/tmp/buildstrap-build/bin/buildstrap'.
```

## Environment path: `--env`

As seen in the previous example, the script is generating a bunch of directories used
for setting up the environment in `{root_path}/var/`. You might want them to be named
differently, so they're not seen in listings for example:

```
% buildstrap -r /tmp -s `pwd`/buildstrap -e .var show buildstrap requirements.txt
[buildout]
newest = false
parts = buildstrap
package = buildstrap
extensions = gp.vcsdevelop
directory = /tmp
develop = /home/guyzmo/Workspace/Projects/buildstrap/buildstrap
eggs-directory = ${buildout:directory}/.var/eggs
develop-eggs-directory = ${buildout:directory}/.var/develop-eggs
parts-directory = ${buildout:directory}/.var/parts
develop-dir = ${buildout:directory}/.var/develop
bin-directory = ${buildout:directory}/bin
requirements = ${buildout:develop}/requirements.txt

[buildstrap]
recipe = zc.recipe.egg
eggs = ${buildout:requirements-eggs}
        buildstrap

```

or you might want to put it at any other place, by using an absolute path:

```
% buildstrap -r /tmp -s `pwd`/buildstrap -e /tmp/buildstrap-var show buildstrap requirements.txt
[buildout]
directory = /tmp
develop = /home/guyzmo/Workspace/Projects/buildstrap/buildstrap
eggs-directory = /tmp/buildstrap-var/eggs
develop-eggs-directory = /tmp/buildstrap-var/develop-eggs
parts-directory = /tmp/buildstrap-var/parts
develop-dir = /tmp/buildstrap-var/develop
bin-directory = ${buildout:directory}/bin
…
```

## Bin path: `--bin`

Finally, you might not like the default of having the `bin` directory at the
`root` path position, so you can put it within var the following way:

```
% buildstrap -b var/bin show buildstrap requirements.txt
[buildout]
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
develop-dir = ${buildout:directory}/var/develop
bin-directory = ${buildout:directory}/var/bin
…
```

or same as before, to somewhere other place non relative to the sources:

```
% buildstrap -r /tmp -s `pwd`/buildstrap -e /tmp/buildstrap-var -b /tmp/buildstrap-bin show buildstrap requirements.txt
[buildout]
develop = .
directory = /tmp/buildstrap-env/
eggs-directory = /tmp/buildstrap-var/eggs
develop-eggs-directory = /tmp/buildstrap-var/develop-eggs
parts-directory = /tmp/buildstrap-var/parts
develop-dir = /tmp/buildstrap-var/develop
bin-directory = /tmp/buildstrap-bin
…
```

