import json
import pickle
from os import path

import requests
from bs4 import BeautifulSoup

from werkzeug.exceptions import HTTPException
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response
from werkzeug.wsgi import responder


url = Map([
    Rule(
        '/groupes/<groupe>', endpoint='groupes'),
    Rule(
        '/groupes', endpoint='all_groupes'),
])

FPATH = lambda p: path.join(path.expanduser('~'), 'emplois', p)  # noqa


def save_days(group):
    content = requests.post(
        'http://www.issatso.rnu.tn/emplois/empetd.php',
        data={'etd': '%s-1' % group})
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
                'matiere': eachRow.find_all('td')[4].font.text,
                'enseignant': eachRow.find_all('td')[5].font.text,
                'type': eachRow.find_all('td')[6].font.text,
                'salle': eachRow.find_all('td')[7].font.text,
            })
    del days[0]
    return days


def all_groupes(response):
    try:
        gen = pickle.load(open(FPATH('all'), 'rb'))
    except FileNotFoundError:
        gen = list(
            map(lambda x: x.text,
                BeautifulSoup(
                    requests.get(
                        'http://www.issatso.rnu.tn/emplois/etudiants.php')
                    .text, 'html.parser').find('select', {'id': 'etd'})
                .find_all('option')))
        del gen[-1]

        try:
            pickle.dump(gen, open(FPATH('all'), 'wb'))
        except requests.exceptions.ConnectionError:
            return Response(status=500)
    return Response(
        json.dumps(
            gen, ensure_ascii=False, sort_keys=True, indent=4),
        content_type='application/json')


def groupes(response, groupe):
    try:
        days = pickle.load(open(FPATH(groupe), 'rb'))
    except FileNotFoundError:
        try:
            days = save_days(groupe)
            # print(FPATH(groupe))
            pickle.dump(days, open(FPATH(groupe), 'wb'))
        except requests.exceptions.ConnectionError:
            return Response(status=500)

    return Response(
        json.dumps(
            days, ensure_ascii=False, sort_keys=True, indent=4),
        content_type='application/json')


views = {'groupes': groupes, 'all_groupes': all_groupes}


@responder
def application(environ, response):
    urls = url.bind_to_environ(environ)
    try:
        endpoint, args = urls.match()
        return Response.force_type(
            urls.dispatch(
                lambda e, v: views[e](response, **v),
                catch_http_exceptions=True))
    except HTTPException as e:
        return e


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    run_simple('localhost', 4000, application, use_debugger=True)
