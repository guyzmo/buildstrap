# Buildstrap: self contained env with ♥

For those who want to hack on any project without having to hack around your
shell environment, mess with your python tools, pollute your home dotfiles,
buildstrap is for you.

This project will bring the power of [buildout], by generating in a simple
command all you need to setup a buildout configuration, that will then create
a self contained python environment for all your hacking needs.

It's as simple as:

```
% git clone https://github.com/guyzmo/buildstrap
% cd buildstrap
% buildstrap run buildstrap requirements.txt
…
% bin/buildstrap --version
0.1.1
```

What is being done here, is that you tell buildstrap the package's name,
and the requirements files to parse, and it will generate the the following
`buildout.cfg` file:

```
[buildout]
newest = false
parts = buildstrap
develop = .
eggs-directory = ${buildout:directory}/var/eggs
develop-eggs-directory = ${buildout:directory}/var/develop-eggs
develop-dir = ${buildout:directory}/var/develop
parts-directory = ${buildout:directory}/var/parts
requirements = ${buildout:develop}/requirements.txt

[buildstrap]
eggs = ${buildout:requirements-eggs}
	buildstrap
recipe = zc.recipe.egg
```

That file is then used to configure buildout so it creates the environment
in your project's directory. You'll find all your dependencies downloaded
into `/var`, and all the scripts you need populated in `/bin`.

So, it's only two directories to add to your `.gitignore`, and to delete
when you want to make your workspace clean again. Then you can choose to
either keep (and eventually tweak) your `buildout.cfg` file, or throw it
away.

Yes, it's as easy as it sounds!

[buildout]:https://github.com/buildout/buildout

```eval_rst

.. toctree::
   quickstart
   buildout
   advanced_usage
   buildstrap

```
