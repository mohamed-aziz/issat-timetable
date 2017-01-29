from os import getenv
if getenv('TB_VENV_PATH'):
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
except ImportError as e:
    print('Exited with error: {error}'.format(error=e))
    exit(127)

FPATH = path.join(path.expanduser('~'), '.tb_data.p')

corrTable = {
    'LUNDI': 0,
    'MARDI': 1,
    'MERCREDI': 2,
    'JEUDI': 3,
    'VENDREDI': 4,
    'SAMEDI': 5
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


@table.command()
@click.argument('group')
@click.option('--day', type=str)
@click.option('--today', is_flag=True)
def lstable(**kwargs):
    try:
        content = requests.post(
            'http://www.issatso.rnu.tn/emplois/empetd.php',
            data={'etd': '%s-1' % kwargs['group']})
    except requests.exceptions.ConnectionError:
        # fallback to the old data, if any
        # else fail
        try:
            days = pickle.load(open(FPATH, 'rb'))
        except FileNotFoundError:
            print('Could not connect to the institute website nor I did find local data.')
            exit(127)
    else:
        soup = BeautifulSoup(content.content, 'html.parser')

        table = soup.find_all('table')[1]

        tr = table.find_all('tr')[2]

        days = list()

        for eachRow in tr.find_all('tr'):
            # if this a day?
            if eachRow.strong is not None:
                days.append({'name': eachRow.strong.text, 'seances': []})
            else:
                # so this is not a new day?
                days[-1]['seances'].append({
                    'name': eachRow.find_all('td')[1].font.text,
                    'debut': eachRow.find_all('td')[2].font.text,
                    'fin': eachRow.find_all('td')[3].font.text,
                    'matiere': eachRow.find_all('td')[4].font.text.encode('utf-8'),
                    'enseignant': eachRow.find_all('td')[5].font.text,
                    'type': eachRow.find_all('td')[6].font.text,
                    'salle': eachRow.find_all('td')[7].font.text,
                })

        del days[0]
    currDay = kwargs.get('day')
    today = kwargs.get('today')
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
                            'matiere'].decode('utf-8')
                ]
                for i, eachScance in enumerate(day['seances'])],
                tablefmt='fancy_grid'))
    else:
        print(
            tabulate(
                [[
                    day['name'] if i == 0 else '', eachScance['name'],
                    eachScance['debut'], eachScance['fin'], eachScance[
                        'salle'], eachScance['type'], eachScance[
                            'matiere'].decode('utf-8')
                ]
                for day in days
                for i, eachScance in enumerate(day['seances'])],
                tablefmt='fancy_grid'))


if __name__ == '__main__':
    table()
