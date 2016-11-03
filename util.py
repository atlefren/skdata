# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup


def get_soup(session, url):
    r = session.get(url)
    r.encoding = 'iso-8859-1'
    return BeautifulSoup(r.text, 'html.parser')


def get_form_params(session, url, params):
    soup = get_soup(session, url)
    data = {}
    for param in params:
        input = soup.find('input', {'name': param})
        if input is not None:
            data[param] = input.get('value', None)
    return data


def spaces_to_underscores(string):
    return '_'.join(string.split(' '))

REPLACES = {
    u'æ': 'e',
    u'Æ': 'E',
    u'ø': 'o',
    u'Ø': 'O',
    u'å': 'a',
    u'Å': 'A',
}


def replace_norwegian_chars(string):
    for key, value in REPLACES.iteritems():
        string = string.replace(key, value)
    return string
