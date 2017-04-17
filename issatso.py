# coding: utf-8

__license__ = 'GPLv3'
__author__ = 'Mohamed Aziz Knani <medazizknani@gmail.com>'

from os import getenv
if getenv('TB_VENV_PATH'):
    # use the virtual environment
    VENV_PATH = getenv('TB_VENV_PATH')
    exec(
        compile(open(VENV_PATH, 'r').read(), VENV_PATH, 'exec'), {
            '__file__': VENV_PATH,
            '__name__': '__main__'
        }
    )

try:
    import requests
    from tabulate import tabulate
    import click
    import pickle
    import datetime
    from os import path
    import json
    from urllib.parse import urljoin
    from functools import wraps
except ImportError as e:
    print('Exited with error: {error}'.format(error=e))
    exit(127)

# exapnduser('~') works also on windows
FPATH = lambda x: path.join(path.expanduser('~'), x)

corrTable = requests.structures.CaseInsensitiveDict({
    'lundi': 0,
    'mardi': 1,
    'mercredi': 2,
    'jeudi': 3,
    'vendredi': 4,
    'samedi': 5
})

API_LINK = 'http://uspace.aziz.tn/issatso/api/v1/'


@click.group()
def table():
    pass

def save_data(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            ret = func(*args, **kwargs)
            if isinstance(ret, tuple):
                name, data = ret
                pickle.dump(data, open(FPATH(name), 'wb'))
                return data
        except requests.exceptions.ConnectionError:
            print('Could not connect to host.')
            exit(127)
        except FileNotFoundError:
            print('Could not find cached data on your hard drive.')
            exit(127)
    return wrapper


def load_groups():
    try:
        gen = requests.structures.CaseInsensitiveDict(requests.get(urljoin(API_LINK, 'groupes')).json())
    except requests.exceptions.ConnectionError:
        gen = pickle.load(open(FPATH('.tb_all.p'), 'rb'))
    return gen


def tabulate_it(days):
    return tabulate(
        [[
            day['name'] if i == 0 else '', eachScance['name'],
            eachScance['debut'], eachScance['fin'], eachScance['salle'], eachScance['type'], eachScance['matiere'], eachScance['semaine']
            ]
         for day in days
         for i, eachScance in enumerate(day['seances'])],
        tablefmt='fancy_grid',
        headers=['Jour', 'Nom séance', 'debut', 'fin', 'type', 'matière', 'semaine'])


@table.command()
@save_data
def lsgroups(**kwargs):
    gen = load_groups()
    print(tabulate([[f] for f in gen.keys()], tablefmt='fancy_grid'))
    return '.tb_all.p', gen


@table.command()
@click.argument('group')
@click.option('--day', type=str)
@click.option('--subgroup', type=int)
@click.option('--today', is_flag=True)
@click.option('--json', is_flag=True)
@click.option('--cached', is_flag=True)
@save_data
def lstable(**kwargs):
    try:
        # ugly hack.
        if kwargs['cached'] and path.exists(FPATH('.tb_data.p')):
            raise requests.exceptions.ConnectionError
        lookup_table = load_groups()
        params = dict()
        if kwargs['subgroup'] is not None:
            params['groupe'] = kwargs['subgroup']
        days = requests.get(urljoin(API_LINK, 'groupes/{0}'.format(lookup_table[kwargs['group']])), params=params).json()
    except requests.exceptions.ConnectionError:
        # fallback to the old data, if any
        # else fail
        days = pickle.load(open(FPATH('.tb_data.p'), 'rb'))
    except KeyError:
        print('Group not found.')
        exit(127)
    currDay = kwargs.get('day')
    today = kwargs.get('today')
    if kwargs['json']:
        print(json.dumps(days, ensure_ascii=False, sort_keys=True, indent=4))
        return days
    if currDay:
        print(tabulate_it([days[corrTable[currDay]]]))
    elif today:
        print(tabulate_it([days[datetime.datetime.today().weekday() % 6]]))
    else:
        print(tabulate_it(days))
    return '.tb_data.p', days

if __name__ == '__main__':
    table()
