# Buildstrap: generate a buildout config for any \*env project

[![WTFPL](http://www.wtfpl.net/wp-content/uploads/2012/12/wtfpl-badge-2.png)](http://wtfpl.org)
[![Python3](https://img.shields.io/pypi/pyversions/buildstrap.svg)](https://pypi.python.org/pypi/buildstrap)
[![Issues](https://img.shields.io/github/issues/guyzmo/buildstrap.svg)](https://github.com/guyzmo/buildstrap)
[![Build](https://travis-ci.org/guyzmo/buildstrap.svg)](https://travis-ci.org/guyzmo/buildstrap)
[![Code Climate](https://codeclimate.com/github/guyzmo/buildstrap/badges/gpa.svg)](https://codeclimate.com/github/guyzmo/buildstrap)
[![Coverage](https://codeclimate.com/github/guyzmo/buildstrap/badges/coverage.svg)](https://codeclimate.com/github/guyzmo/buildstrap)

There's pyenv, pyvenv, venv, virtualenv… and who knows how many other ways to
deal with development of python programs in a per-project self-contained
manner.

While most of the python community tried to keep up, and got their shell
configuration or global pip changing regularly, some have been quietly enjoying
python development the same way for the last ten years, using [buildout] for
their development.

Though, it's a fact that buildout is not the standard way to do things, even if
it's a very convenient tool. So to keep your repositories compatible with most
\*env tools available — or get buildout with other projects. I wrote this tool
to make it easy to create a buildout environment within the project.

[buildout]:https://github.com/buildout/buildout/

# Quickstart Guide

Here we'll see the most common usages, and refer to [the full documentation for
more details][doc].

[doc]:https://buildstrap.readthedocs.org/

## Usage

when you got a repository that has requirements files, at the root of your project's
directory, call buildstrap using:

```
% buildstrap run project requirements.txt
```

where `project` as second argument is the name of the package as you've set it
up in your `setup.py` — and as you'd import it from other python code.  

Running that command will generate the `buildout.cfg` file, and run `buildout`
in your current directory. Then you'll find all your scripts available in the
newly created `bin` directory of your project.

If you have several `requirements.txt` files, depending on the task you want to
do, it's easy:

```
% buildstrap run project -p pytest -p sphinx requirements.txt requirements-test.txt requirements-doc.txt
```

which will create three sections in your `buildout.cfg` file, and get all the
appropriate dependencies.

Here's a real life example:

```
% git hub clone kennethreitz/requests    # cf 'Nota Bene'
% cd requests
% buildstrap run requests requirements.txt
…
% bin/py.test
… (look at the tests result)
% bin/python3
>>> import requests
>>>
```

or another one:

```
% git hub clone jkbrzt/httpie            # cf 'Nota Bene'
% cd httpie
% buildstrap run httpie requirements-dev.txt
…
% bin/py.test
… (look at the tests result)
% bin/http --version
1.0.0-dev
```

## Installation

it's as easy as any other python program:

```
% pip install buildstrap
```

or from the sources:

```
% git hub clone guyzmo/buildstrap
% cd buildstrap
% python3 setup.py install
```

## Development

for development you just need to do:

```
% pip install buildstrap
% git clone https://github.com/guyzmo/buildstrap
% cd buildstrap
% builstrap run buildstrap -p pytest -p sphinx requirements.txt requirement-test.txt requirement-doc.txt
…
% bin/buildstrap
```

Yeah, I'm being evil here 😈

You can have a look at the [sources documentation][srcdoc].

[srcdoc]:http://buildstrap.readthedocs.io/en/latest/buildstrap.html

## Nota Bene

You might wonder where does the `git hub clone` command comes from, and I'm
using here another project I wrote: [guyzmo/git-repo](https://github.com/guyzmo/git-repo).

Simply put, `git hub clone user/project` is equivalent to `git clone https://github.com/user/project`.

## License

    Copyright © 2016 Bernard `Guyzmo` Pratz <guyzmo+buildstrap+pub@m0g.net>
    This work is free. You can redistribute it and/or modify it under the
    terms of the Do What The Fuck You Want To Public License, Version 2,
    as published by Sam Hocevar. See the LICENSE file for more details.



