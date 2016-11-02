# -*- coding: utf-8 -*-
import re
import os
import sys
import json

import requests
from bs4 import BeautifulSoup

'''
import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True
'''
BASE_URL = 'http://data.kartverket.no'


def check_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)


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


def get_categories(session):
    url = '%s/download/' % BASE_URL
    soup = get_soup(session, url)
    div = soup.find('div', {'class': 'field-item'})
    categories = []
    for td in div.find('table').findAll('td'):
        h3 = td.find('h3')
        if h3 is not None:
            link = td.findAll('p')[-1].find('a')['href']
            id = next(l for l in link.split('?')[-1].split('&') if l.startswith(u'korttype')).split('=')[-1]
            categories.append({
                'name': unicode(h3.text).encode('iso-8859-1'),
                'id': id
            })
    return categories


def parse_subcategories_soup(soup):
    rows = []
    for row in soup.findAll('div', {'class': 'views-row'}):
        title = row.find('div', {'class': 'title'}).find('a')
        # info = row.find('div', {'class': 'info'})
        # print info.text.replace('Korttype: ', '').split(', ')
        rows.append({
            'title': unicode(title.text).encode('iso-8859-1'),
            'id': title['href'].split('/')[-1],
            # 'tags': []
        })
    return rows


def get_subcategory_page(subcategory_id, page, session):
    url = '%s/download/content/geodataprodukter?korttype=%s&page=%s' % (
        BASE_URL,
        subcategory_id,
        page
    )
    soup = get_soup(session, url)
    data = parse_subcategories_soup(r.text)
    if data is not None and len(data) > 0:
        return data, True
    return None, False


def get_subcategories(subcategory_id, session):
    has_data = True
    subcategories = []
    page = 0
    while has_data:
        data, has_data = get_subcategory_page(subcategory_id, page, session)
        page += 1
        if data is not None:
            subcategories += data
    return subcategories


def get_geojson_url(service_type):
    urls = {
        u'fylker': '/json/norge/fylker.json',
        u'fylker-utm35': '/json/norge/fylker-utm35.json',
        u'fylker-utm33': '/json/norge/fylker-utm33.json',
        u'fylker-utm32': '/json/norge/fylker-utm32.json',
        u'kommuner': '/json/norge/kommuner.json',
        u'kommuner-utm35':  '/json/norge/kommuner-utm35.json',
        u'kommuner-utm33':  '/json/norge/kommuner-utm33.json',
        u'kommuner-utm32':  '/json/norge/kommuner-utm32.json',
        u'dtm-dekning-utm32': '/json/dekning/dtm/utm32.geojson',
        u'dtm-dekning-utm33': '/json/dekning/dtm/utm33.geojson',
        u'dtm-dekning-utm33-100km':  '/json/dekning/dtm/utm33-100km.geojson',
        u'dtm-dekning-utm35':  '/json/dekning/dtm/utm35.geojson',
        u'dtm-sjo': '/json/dekning/sjo/celler/dtm50.geojson',
        u'dtm-sjo-5': '/json/dekning/sjo/celler/dtm50_5.geojson',
        u'dtm-sjo-25': '/json/dekning/sjo/celler/dtm50_25.geojson',
        u'dtm-sjo-50': '/json/dekning/sjo/celler/dtm50_50.geojson',
        u'raster-32': '/json/dekning/raster/32.geojson',
        u'raster-33': '/json/dekning/raster/33.geojson',
        u'raster-35': '/json/dekning/raster/35.geojson',
        u'raster-n50': '/json/dekning/raster/n50.geojson',
        u'raster-n250': '/json/dekning/raster/n250_ny.geojson',
        u'raster-n500': '/json/dekning/raster/n500_ny.geojson',
        u'raster-n1000': '/json/dekning/raster/n1000_ny.geojson',
        u'dybdedata_50m': '/json/norge/dybdedata_50m.geojson',
    }
    url = urls.get(service_type, None)
    if url is not None:
        return 'http://www.norgeskart.no%s' % url
    return None


def parse_filenames_files(kms_widget):
    service_name = kms_widget[u'service_name']
    if service_name is None:
        return [kms_widget[u'selection_details']], True

    url = get_geojson_url(service_name)
    res = []
    if url is not None:
        r = requests.get(url)
        for feature in r.json()['features']:
            res.append({
                'id': feature.get('id', None),
                'name': feature['properties']['n'],
                'feature': feature
            })

    replaces = {
        u'æ': 'e',
        u'Æ': 'E',
        u'ø': 'o',
        u'Ø': 'O',
        u'å': 'a',
        u'Å': 'A',
    }

    filenames = []
    for data in res:
        id = data.get('id', None)
        selection_details = kms_widget[u'selection_details']
        if id is None:
            filename = data['name'] + selection_details
        else:
            filename = '%s_%s%s' % (id, data['name'], selection_details)
        ext = 'zip'
        if kms_widget[u'dataformat'] == 'MrSID':
            ext = 'sid'

        filename = '%s_%s_%s.%s' % (kms_widget[u'service_layer'], '_'.join(filename.split(' ')), kms_widget[u'dataformat'], ext)

        for key, value in replaces.iteritems():
            filename = filename.replace(key, value)

        filenames.append(unicode(filename).encode('utf8'))
    return filenames, False


def get_data_select(id, session):
    url = '%s/download/content/%s' % (BASE_URL, id)
    r = session.get(url)
    r.encoding = 'iso-8859-1'
    line = next(line for line in r.text.split('\n') if
                line.startswith('jQuery.extend(Drupal.settings'))
    kms_widget = json.loads(
        line.replace('jQuery.extend(Drupal.settings, ', '').replace(');', '')
    ).get('kms_widget', {})
    return parse_filenames_files(kms_widget)


def login(username, password):
    session = requests.Session()
    url = 'http://data.kartverket.no/download/'
    params = get_form_params(session, url, ['form_build_id', 'form_id'])
    data = {
        'form_build_id': params['form_build_id'],
        'form_id': params['form_id'],
        'name': username,
        'op': 'Logg inn',
        'pass': password
    }
    r = session.post(url, data=data)

    return session


def add_to_cart(content_id, files, session, single_file=False):
    url = '%s/download/content/%s' % (BASE_URL, content_id)
    data = get_form_params(
        session,
        url,
        ['form_build_id', 'form_id', 'form_token', 'product_id']
    )

    if single_file:
        num = '1 samlet fil'
    else:
        num = '%s filer' % len(files)

    files = '[%s]' % ', '.join(['"%s"' % file for file in files])
    data = {
        'product_id': ('', data['product_id']),
        'form_build_id': ('', data['form_build_id']),
        'form_token': ('', data['form_token']),
        'form_id': ('', data['form_id']),
        'line_item_fields[field_selection][und][0][value]': ('', files),
        'line_item_fields[field_selection_text][und][0][value]': ('', num),
        'quantity': ('', '1'),
        'op': ('', 'Legg i kurv')
    }

    r = session.post(url, files=data)
    return r.status_code == 200


def place_order(session):

    url = '%s/download/cart' % BASE_URL
    data = get_form_params(
        session,
        url,
        ['form_build_id', 'form_id', 'form_token']
    )
    data['op'] = 'Bestill'
    response = session.post(url, data=data)
    url2 = response.url

    m = re.search('http://data\.kartverket\.no/download/checkout/(\d*)/checkout', url2)
    order_id = m.group(1)

    data2 = get_form_params(
        session,
        url2,
        ['form_build_id', 'form_id', 'form_token']
    )
    data2['op'] = 'Fortsett'

    response2 = session.post(url2, data=data2)
    return order_id


def get_download_links(order_id, session):
    url = '%s/download/mine/downloads' % BASE_URL
    soup = get_soup(session, url)

    files = []
    for table in soup.findAll('table', {'class': 'views-table'}):
        order_id_for_table = table\
            .find('caption').text\
            .split(' |')[0]\
            .replace('Ordrenummer: ', '')
        if order_id_for_table == order_id:
            for tr in table.find('tbody').findAll('tr'):
                files.append(tr.find('a')['href'])
    return files


def download_file(url, save_to, session):
    # NOTE the stream=True parameter
    r = session.get(url, stream=True)
    with open(save_to, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)
                # f.flush() commented by recommendation from J.F.Sebastian


def download_files(files, directory, session):
    check_dir(directory)
    for file in files:
        filename = file.split('/')[-1]
        path = os.path.join(directory, filename)
        download_file(file, path, session)

if __name__ == '__main__':
    product_id = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]

    # log the user in, get session
    session = login(username, password)

    # get the filenames for this product
    filenames, single_file = get_data_select(product_id, session)

    # add all files to the cart
    add_to_cart(
        product_id,
        filenames,
        session,
        single_file=single_file
    )

    # place an order
    order_id = place_order(session)

    files = get_download_links(order_id, session)

    directory = os.path.join('dl', order_id)
    download_files(files, directory, session)
