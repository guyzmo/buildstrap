# Buildout configuration

Before going into more details, let's have briefly a look at a `buildout.cfg`
configuration. Each section of the configuration file are called `part`s in
buildout slang. The part configures a directive to run using a recipe. There
are [many recipes you can lookup][recipes], but in a `buildout.cfg` freshly
baked by buildstrap, you'll only see two:

* `zc.recipe.egg`: which takes care of downloading and installing dependencies into
    the self-contained environment ;
* `gp.vcsdevelop`: which parses a `requirements.txt` file and exposes the
    dependencies, so `zc.recipe.egg` can do its job (in the context of buildstrap).

Then, to setup the environment, there's a section named `[buildout]` that
contains everything needed to setup the self contained environment, like the
list of parts to run (remove one from there and it'll be ignored), the paths to
the used directories…

Once the buildout configuration file, `buildout.cfg` has been generated, you can tweak
it as much as you like to suit your needs. Buildout is much more than just setting up
a self contained environment!

If you want to read more about buildout, [check its documentation][doc], or for more
in depth info, [check `buildout.cfg` manual][doc-conf].

[recipes]:http://www.buildout.org/en/latest/docs/recipelist.html
[doc]:http://www.buildout.org/en/latest/docs/
[doc-conf]:https://github.com/buildout/buildout/blob/master/src/zc/buildout/buildout.txt

