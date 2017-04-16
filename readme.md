# ISSAT Time table

This is a scrot

![Alt Text](scrot.png)


This is the code that I use to quickly check my timetable on my terminal.

**This script is a little hack, therfore it is not tested so weird errors may popup :(**

**Note: This only supports python3 though it may work on 2**

## Installing the code

So first clone the repo

	$ git clone https://github.com/mohamed-aziz/issat-timetable.git

My advice is to create a virtual environment using the virtualenv program, though you can skip this step:

	$ virtualenv timetable
	$ source timetable/bin/activate

If you create the virtualenv please set the TB_VENV_PATH environment variable, so that you won't need to worry about working on your venv every time (ideally set this in your .bashrc, .zshrc or whatever)

	(venv) $ export TB_VENV_PATH='<yourvenvpath>/bin/activate_this.py'

Then you can install the code requirements:

	(venv) $ pip install -r requirements_dev.txt

## Using the code

Just run your issatso.py file;

To list all the groups:

	$ python3 issatso.py lsgroups

To get your week timetable:

	$ python3 issatso.py lstable "Your group"

You can use commands like:

	$ python3 issatso.py lstable "Your group" --today
	$ python3 issatso.py lstable "Your group" --day vendredi

You can also specify your sub-group, using the <code>--subgroup</code> parameter.

Tired of typing all that, alias it :)

	alias t='python3 ~/Projects/issatso/issatso.py lstable "Your group" --today'

just put that in your .bashrc or .zshrc or whatever.

To output your data into json so that you use the output in other programs, just use <code>--json</code> flag.

There is also a web api which is up on [here](http://uspace.aziz.tn/issatso/) or you can run it yourself using your favourite wsgi webserver (I use gunicorn which is on the requirements file).

In the future there will be an Emacs version.
