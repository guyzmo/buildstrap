Usage
=====

```
Usage: buildstrap [-v...] [run|show] [options] <package> <requirements> [<target>=<requirements>...]

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
```

Multiple requirements.txt
-------------------------

Many projects offer multiple `requirements.txt` files, one for each task of
the development cycle (which usually are running, testing, documenting).

Well, just tell buildstrap what the extra requirements are:

```
% buildstrap run buildstrap requirements.txt doc=requirements-doc.txt test=requirements-test.txt
```

and that will generate the following buildout.cfg configuration:

```
[buildout]
newest = false
parts = buildstrap
		doc
		test
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts

[buildstrap]
recipe = zc.recipe.egg
eggs = ${buildstrap-pip:eggs}
		buildstrap

[doc]
recipe = zc.recipe.egg
eggs = ${doc-pip:eggs}

[test]
recipe = zc.recipe.egg
eggs = ${test-pip:eggs}

[buildstrap-pip]
configs = ${buildout:develop}/requirements.txt
recipe = collective.recipe.pip

[doc-pip]
configs = ${buildout:directory}/requirement-doc.txt
recipe = collective.recipe.pip

[test-pip]
configs = ${buildout:directory}/requirement-test.txt
recipe = collective.recipe.pip
```

and you'll find all the tools you'll need in bin:

```
% ls bin
buildout    cm2html   cm2man        cm2xetex  py.test      sphinx-apidoc   sphinx-build
buildstrap  cm2latex  cm2pseudoxml  cm2xml    py.test-2.7  sphinx-autogen  sphinx-quickstart
```

Multiple packages
-----------------

Some projects will include several packages in the sources, so to support that, just list
all your packages as a comma seperated list, and they will all be included:

```
% buildstrap run dent,prefect,beeblebox requirements.txt

[buildout]
newest = false
parts = dent
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts

[dent]
recipe = zc.recipe.egg
eggs = ${dent-pip:eggs}
		dent
		prefect
		beeblebox

[dent-pip]
recipe = collective.recipe.pip
configs = ${buildout:develop}/requirements.txt
```

Multiple requirements files
---------------------------

Some other projects will use several requirements file for a single task (because for
whatever crazy reason, they don't want to use the `-r other_requirements.txt` syntax).
Well just list all the requirements as a comma separated list:

```
% buildstrap run mostly_harmless requirements.txt,other_requirements.txt
```

Which will generate the matching environment, with the following buildout.cfg:

```
[buildout]
newest = false
parts = mosty_harmless
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts

[mosty_harmless]
eggs = ${mosty_harmless-pip:eggs}
		mosty_harmless
recipe = zc.recipe.egg

[mosty_harmless-pip]
recipe = collective.recipe.pip
configs = ${buildout:develop}/requirements.txt
          ${buildout:directory}/other_requirements.txt
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
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts

[slartibartfast]
eggs = ${slartibartfast-pip:eggs}
       slartibartfast
recipe = zc.recipe.egg

[slartibartfast-pip]
configs = ${buildout:develop}/requirements.txt
recipe = collective.recipe.pip
```

but if you want to just test the command and print the configuration to stdout,
without it doing nothing, use the `show` subcommand:

```
% buildstrap show slartibartfast requirements.txt
[buildout]
newest = false
parts = slartibartfast
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts

[slartibartfast]
eggs = ${slartibartfast-pip:eggs}
       slartibartfast
recipe = zc.recipe.egg

[slartibartfast-pip]
configs = ${buildout:develop}/requirements.txt
recipe = collective.recipe.pip
```

and if you want to write the `buildout.cfg` as another file, you can either redirect
the show command with a pipe, or use the `--output` argument:

```
% buildstrap -o foobar.cfg slartibartfast requirements.txt
% cat foobar.cfg
[buildout]
newest = false
parts = slartibartfast
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts

[slartibartfast]
eggs = ${slartibartfast-pip:eggs}
       slartibartfast
recipe = zc.recipe.egg

[slartibartfast-pip]
configs = ${buildout:develop}/requirements.txt
recipe = collective.recipe.pip
```

N.B.: the show command is equivalent to `--output -`.

Configure the path
------------------

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

But sometimes, you want to change the configuration, for the best (or the worst
— most often, the worst, though).

So, you can set all those paths to values other than the default, and have it
all in a very different setup than the default.

### Root path: `--root`

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
develop = .
directory = /tmp/buildstrap-env/
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts

[buildstrap]
eggs = ${buildstrap-pip:eggs}
       buildstrap
recipe = zc.recipe.egg

[buildstrap-pip]
configs = ${buildout:develop}/requirements.txt
recipe = collective.recipe.pip
```

### Sources path: `--src`

Though, if you change the root directory, chances are (like in the former example) that
it won't be where your sources are. Then, running `buildout` will end up in throwing an
exception:

    FileNotFoundError: [Errno 2] No such file or directory: '/tmp/builstrap-env/./setup.py'

The source path is where you'll have your `setup.py` file that defines your project.
So, if your `setup.py` is not at the root of your project, you definitely want to
use the `--src` argument.

```
% buildstrap -r /tmp -s `pwd`/buildstrap show buildstrap requirements.txt
[buildout]
newest = false
parts = buildstrap
develop = .
directory = /tmp/buildstrap-env/
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
…
```

*Nota Bene*: if you do not want to use a path relative to the `root` path, then
use an absolute path, or you'll have surprises! As you can see in the example above
the path is made absolute by using the `pwd` command.

So running this command with buildout will do:

```
% buildout
Creating directory '/tmp/buildstrap-build/var/eggs'.
Creating directory '/tmp/buildstrap-build/bin'.
Creating directory '/tmp/buildstrap-build/var/parts'.
Creating directory '/tmp/buildstrap-build/var/develop-eggs'.
Develop: '/path/to/sources/of/buildstrap'
Getting distribution for 'collective.recipe.pip'.
warning: no files found matching '*.rst' under directory 'collective'
Got collective.recipe.pip 0.3.4.
Getting distribution for 'zc.recipe.egg>=2.0.0a3'.
Got zc.recipe.egg 2.0.3.
Installing buildstrap-pip.
Installing buildstrap.
Generated script '/tmp/buildstrap-build/bin/buildout'.
Generated script '/tmp/buildstrap-build/bin/buildstrap'.
```

### Environment path: `--env`

As seen in the previous example, the script is generating a bunch of directories used
for setting up the environment in `{root_path}/var/`. You might want them to be named
differently, so they're not seen in listings for example:

```
% buildstrap -r /tmp -s `pwd`/buildstrap -e .var show buildstrap requirements.txt
[buildout]
newest = false
parts = buildstrap
develop = .
directory = /tmp/buildstrap-env/
eggs-directory = ${buildout:directory}/.var/eggs
develop-eggs-directory = ${buildout:directory}/.var/develop-eggs
parts-directory = ${buildout:directory}/.var/parts
…
```

or you might want to put it at any other place, by using an absolute path:

```
% buildstrap -r /tmp -s `pwd`/buildstrap -e /tmp/buildstrap-var show buildstrap requirements.txt
[buildout]
newest = false
parts = buildstrap
develop = .
directory = /tmp/buildstrap-env/
eggs-directory = /tmp/buildstrap-var/eggs
develop-eggs-directory = /tmp/buildstrap-var/develop-eggs
parts-directory = /tmp/buildstrap-var/parts
…
```

### Bin path: `--bin`

Finally, you might not like the default of having the `bin` directory at the
`root` path position, so you can put it within var the following way:

```
% buildstrap -b var/bin show buildstrap requirements.txt
[buildout]
newest = false
parts = buildstrap
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
parts-directory = ${buildout:directory}/var/parts
bin-directory = ${buildout:directory}/var/bin
…
```

or same as before, to somewhere other place non relative to the sources:

```
% buildstrap -r /tmp -s `pwd`/buildstrap -e /tmp/buildstrap-var -b /tmp/buildstrap-bin show buildstrap requirements.txt
[buildout]
newest = false
parts = buildstrap
develop = .
directory = /tmp/buildstrap-env/
eggs-directory = /tmp/buildstrap-var/eggs
develop-eggs-directory = /tmp/buildstrap-var/develop-eggs
parts-directory = /tmp/buildstrap-var/parts
bin-directory = /tmp/buildstrap-bin
…
```

