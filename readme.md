# ISSAT Time table

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

## Web API

I wrote a web API for people to use in their projects, it's up here [here](http://uspace.aziz.tn/issatso/)
you can use it for free though I don't guarantee the stability of the server.

The API is documented in index.html, though I suggest reading the code which
won't be much of a challenge because Python WSGI is fucking poetry, anyways
if you want to run the code on your own I suggest
using gunicorn to deploy it (memory wise it is one of the best python wsgi server),
also the api internally uses redis which means that it's thread safe (it wasn't always like this
with previous versions of this code), no unit tests sadly.


## Terminal application

**This only supports python3 due to the ugly virtualenv hack.**

**Also the code is a fucking hack and needs full rewrite sometime?**


This is a scrot:

![Alt Text](scrot.png)

Just run your issatso.py file;

To list all the groups:

	$ python3 issatso.py lsgroups

To get your week timetable:

	$ python3 issatso.py lstable "Your group"

You can use commands like:

	$ python3 issatso.py lstable "Your group" --today
	$ python3 issatso.py lstable "Your group" --day vendredi
    $ python3 issatso.py lstable "Your group" --subgroup 2  --day vendredi

Tired of typing all that, alias it :)

	alias t='python3 ~/Projects/issatso/issatso.py lstable "Your group" --today'

just put that in your .bashrc or .zshrc or whatever.

To output your data into json so that you can use the output in other programs, just use <code>--json</code> flag.

I will write an emacs plugin when I have time for this.
