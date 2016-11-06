import requests
from bs4 import BeautifulSoup
from pprint import PrettyPrinter
from tabulate import tabulate

content = requests.post(
    'http://www.issatso.rnu.tn/emplois/empetd.php',
    data={
        'etd': 'Prepa-A1-04-1'
    }
)

soup = BeautifulSoup(
    content.content,
    'html.parser'
)

pp = PrettyPrinter()

table = soup.find_all('table')[1]

tr = table.find_all('tr')[2]


days = list()

for eachRow in tr.find_all('tr'):
    # if this a day?
    if eachRow.strong is not None:
        days.append(
            {
                'name': eachRow.strong.text,
                'seances': []
            }
        )
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


pp.pprint(
    days
)

print(tabulate(
    [[day['name'] if i == 0 else '', eachScance['name'], eachScance['debut'], eachScance['fin'], eachScance['salle'], eachScance['type'], eachScance['matiere'].decode('utf-8')] for day in days for i, eachScance in enumerate(day['seances'])],
    tablefmt='fancy_grid'
))
