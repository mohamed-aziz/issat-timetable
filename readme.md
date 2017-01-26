
# ISSAT Time table

This is the code I use to quickly check my timetable on my terminal.

**This a fast script therfore it is not tested so weird errors may popup :(**

## Installing the code

So first clone the repo

	$ git clone https://github.com/mohamed-aziz/issat-timetable.git
	
My advice is to create a virtual environment using the virtualenv program, though you can skip this step:

	$ virtualenv timetable
	$ source timetable/bin/activate

If you create the virtualenv please set the $TB_VENV_PATH environment variable, so that you won't need to worry about working on your venv every time.
	
	(venv) $ export $TB_VENV_PATH='<yourvenvpath>/bin/activate_this.py'

Then you can install the code requirements:

	(venv) $ pip install -r requirements_dev.txt
	
## Using the code

Just run your issatso.py file;

To list all the groups:

	$ python issatso.py lsgroups

To get your week timetable:

	$ python issatso.py lstable "Your group"

You can use commands like:

	$ python issatso.py lstable "Your group" --today
	$ python issatso.py lstable "Your group" --day vendredi

Tired of typing all that, alias it :)

	alias t='python ~/Projects/issatso/issatso.py lstable "Your group" --today'

just put that in your .bashrc or .zshrc or whatever.
	
