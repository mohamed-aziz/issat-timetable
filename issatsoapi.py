__license__ = 'GPLv3'
__author__ = 'Mohamed Aziz Knani <medazizknani@gmail.com>'

import json
import re
from copy import deepcopy

import requests
import redis
from bs4 import BeautifulSoup

from werkzeug.exceptions import HTTPException, NotFound
from werkzeug.routing import Map, Rule
from werkzeug.wrappers import Response, Request

###########
# Constants
###########

EXPIRATION_CACHE = 3600 * 24
EXPR = re.compile('\d+\-(\w+)')

###############
# Helper utils
###############


def get_lookup_table(soup):
    return {
        elem.text: elem.attrs['value']
        for elem in soup.find('form', id='form1').find('select', attrs={'name': 'id'}, ).findAll('option')}


def return_days(rows):
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



def get_days(group, sgrp=None):
    s = requests.Session()
    soup = BeautifulSoup(
        s.get('http://www.issatso.rnu.tn/fo/emplois/emploi_groupe.php').content, 'html.parser')
    lookup_table = get_lookup_table(soup)
    # makes reverse table lookup
    rev_lookup_table = {value: key for key, value in lookup_table.items()}
    csrf_token = soup.find('form',
                           id='form1').find('input', id='jeton').attrs['value']
    content = s.get(
        'http://www.issatso.rnu.tn/fo/emplois/emploi_groupe.php',
        params={
            'id': group,
            'jeton': csrf_token,
            'first_version': '1'})

    soup = BeautifulSoup(content.content, 'html.parser')
    table = soup.find_all('table')[6]
    rows = table.find('tbody').find_all('tr')
    days = return_days(rows[1:])
    if sgrp is not None:
        schema = '{0}-{1}'.format(rev_lookup_table[group], sgrp)
        for i, row in enumerate(rows):
            if row.td.center.text.lower() == schema.lower():
                rows = rows[i+1:]
                break
        intersection = return_days(rows)
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

    return days

####################
# Application class
####################


class TimeTable:
    def __init__(self, config={}):
        self.redis = redis.Redis(config['redis_host'], config['redis_port'])
        self.url_map = Map([
            Rule('/groupes/<groupe>', endpoint='groupes'),
            Rule('/groupes', endpoint='all_groupes'),
        ])

    def on_all_groupes(self, response):
        out = self.redis.get('issatso-timetable-all')
        if out:
            gen = json.loads(out.decode('utf-8'))
        else:
            try:
                gen = get_lookup_table(BeautifulSoup(requests.get('http://www.issatso.rnu.tn/fo/emplois/emploi_groupe.php').content, 'html.parser'))
                self.redis.set('issatso-timetable-all', json.dumps(gen))
            except requests.exceptions.ConnectionError:
                return Response(status=500)
        return Response(
            json.dumps(
                gen, ensure_ascii=False, sort_keys=True, indent=4),
            content_type='application/json')

    def on_groupes(self, response, groupe):
        grp = response.args.get('groupe')
        if grp:
            out = self.redis.get('issatso-timetable-{0}-{1}'.format(groupe, grp))
        else:
            out = self.redis.get('issatso-timetable-{0}'.format(groupe))
        if out:
            days = json.loads(out.decode('utf-8'))
        else:
            days = get_days(groupe, sgrp=grp)
            if grp:
                self.redis.set('issatso-timetable-{0}-{1}'.format(groupe, grp), json.dumps(days), ex=EXPIRATION_CACHE)
            else:
                self.redis.set('issatso-timetable-{0}'.format(groupe), json.dumps(days), ex=EXPIRATION_CACHE)

        return Response(
            json.dumps(
                days, ensure_ascii=False, sort_keys=True, indent=4),
            content_type='application/json')

    def dispatch_request(self, request):
        adapter = self.url_map.bind_to_environ(request.environ)
        try:
            endpoint, values = adapter.match()
            return getattr(self, 'on_' + endpoint)(request, **values)
        except NotFound as e:
            return e
        except HTTPException as e:
            return e

    def wsgi_app(self, environ, start_response):
        request = Request(environ)
        response = self.dispatch_request(request)
        return response(environ, start_response)

    def __call__(self, environ, start_response):
        return self.wsgi_app(environ, start_response)


def create_app(redis_host='localhost', redis_port=6379):
    app = TimeTable({
        'redis_host': redis_host,
        'redis_port': redis_port
    })
    return app


if __name__ == '__main__':
    from werkzeug.serving import run_simple
    application = create_app()
    run_simple('localhost', 4000, application, use_debugger=True,
               use_reloader=True)
