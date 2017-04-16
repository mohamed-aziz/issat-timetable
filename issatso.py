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
    import requests # noqa
    from bs4 import BeautifulSoup # noqa
    from tabulate import tabulate # noqa
    import click # noqa
    import pickle # noqa
    import datetime # noqa
    from os import path # noqa
    import json # noqa
    import re # noqa
    from copy import deepcopy # noqa
except ImportError as e:
    print('Exited with error: {error}'.format(error=e))
    exit(127)

# exapnduser('~') works also on windows
FPATH = path.join(path.expanduser('~'), '.tb_data.p')

corrTable = {
    'lundi': 0,
    'mardi': 1,
    'mercredi': 2,
    'jeudi': 3,
    'vendredi': 4,
    'samedi': 5
}


@click.group()
def table():
    pass


@table.command()
def lsgroups(**kwargs):
    # magical, maybe ?
    gen = list(
        map(lambda x: x.text,
            BeautifulSoup(
                requests.get('http://www.issatso.rnu.tn/emplois/etudiants.php')
                .text, 'html.parser').find('select', {'id': 'etd'}).find_all(
                    'option')))
    del gen[-1]
    print(tabulate([[f] for f in gen], tablefmt='fancy_grid'))

def get_days(rows):
    EXPR = re.compile('\d+\-(\w+)')
    days = list()
    for eachRow in rows:
        # if this a day?
        # import pdb; pdb.set_trace()
        if eachRow.find_all('td')[1].center.text == '':
            if EXPR.match(eachRow.td.center.text) is None:
                break
            days.append({'name': EXPR.match(eachRow.td.center.text).group(1), 'seances': []})
        else:
            # so this is not a new day?
            days[-1]['seances'].append({
                'name': eachRow.find_all('td')[1].center.text,
                'debut': eachRow.find_all('td')[2].center.text,
                'fin': eachRow.find_all('td')[3].center.text,
                'matiere': eachRow.find_all('td')[4].center.text,
                'enseignant': eachRow.find_all('td')[5].center.text,
                'type': eachRow.find_all('td')[6].center.text,
                'salle': eachRow.find_all('td')[7].center.text,
                'semaine': eachRow.find_all('td')[8].center.text,
            })

    return days


@table.command()
@click.argument('group')
@click.option('--day', type=str)
@click.option('--subgroup', type=int)
@click.option('--today', is_flag=True)
@click.option('--json', is_flag=True)
def lstable(**kwargs):
    try:
        # get csrf token (jeton) and groups ids
        try:
            # cookies meh..
            s = requests.Session()
            soup = BeautifulSoup(s.get('http://www.issatso.rnu.tn/fo/emplois/emploi_groupe.php').content, 'html.parser')
        except requests.exceptions.ConnectionError:
            exit(1)
        else:
            # make a lookup dict for group name -> id
            group_lookup_table = {elem.text: elem.attrs['value'] for elem in soup.find('form', id='form1').find('select', attrs={'name': 'id'}, ).findAll('option')}
            csrf_token = soup.find('form', id='form1').find('input', id='jeton').attrs['value']
            content = s.get(
                'http://www.issatso.rnu.tn/fo/emplois/emploi_groupe.php',
                params={
                    'id': '%s' % group_lookup_table[kwargs['group']], 'jeton': csrf_token, 'first_version': '1'})

    except KeyError:
        print('Group not found.')
        exit(1)
    except requests.exceptions.ConnectionError:
        # fallback to the old data, if any
        # else fail
        try:
            days = pickle.load(open(FPATH, 'rb'))
        except FileNotFoundError:
            print('Could not connect to the institute website nor I did find local data.')
            exit(127)
    else:
        if kwargs['subgroup']:
            group = '{0}-{1}'.format(kwargs['group'], str(kwargs['subgroup']))
        else:
            group = kwargs['group']
        print(group)
        soup = BeautifulSoup(content.content, 'html.parser')
        table = soup.find_all('table')[6]
        rows = table.find('tbody').find_all('tr')
        # grab always the first group and replace the intersection if
        # any other group exists
        days = get_days(rows[1:])
        if (rows[0].td.center.text.lower() != group.lower()):
            for i, row in enumerate(rows):
                if row.td.center.text.lower() == group.lower():
                    rows = rows[i+1:]
                    break
            intersection = get_days(rows)
            # change seances?
            for day in intersection:
                for i, day1 in enumerate(days):
                    if day1['name'] == day['name']:
                        copiedday = deepcopy(day1)
                        for sea in day['seances']:
                            for j, sea1 in enumerate(day1['seances']):
                                if sea['name'] == sea1['name'] and sea['semaine'] != sea1['semaine']:
                                    copiedday['seances'][j] = sea
                                    break
                        days[i] = copiedday

    currDay = kwargs.get('day')
    today = kwargs.get('today')
    to_json = kwargs.get('json')
    if to_json:
        print(json.dumps(days, ensure_ascii=False, sort_keys=True, indent=4))
        exit(0)
    # save data
    pickle.dump(days, open(FPATH, 'wb'))
    if currDay:
        day = days[corrTable[currDay.upper()]]
    if today:
        day = days[datetime.datetime.today().weekday() % 6]
    if currDay or today:
        print(
            tabulate(
                [[
                    day['name'] if i == 0 else '', eachScance['name'],
                    eachScance['debut'], eachScance['fin'], eachScance[
                        'salle'], eachScance['type'], eachScance[
                            'matiere'], eachScance['semaine']
                ]
                for i, eachScance in enumerate(day['seances'])],
                tablefmt='fancy_grid',
                headers=['Jour', 'Nom séance', 'debut', 'fin', 'type', 'matière', 'semaine']
            ))
    else:
        print(
            tabulate(
                [[
                    day['name'] if i == 0 else '', eachScance['name'],
                    eachScance['debut'], eachScance['fin'], eachScance[
                        'salle'], eachScance['type'], eachScance[
                            'matiere'], eachScance['semaine']
                ]
                for day in days
                for i, eachScance in enumerate(day['seances'])],
                tablefmt='fancy_grid',
                headers=['Jour', 'Nom séance', 'debut', 'fin', 'type', 'matière', 'semaine']))


if __name__ == '__main__':
    table()
