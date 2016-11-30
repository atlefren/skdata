# -*- coding: utf-8 -*-
import re

from util import (get_form_params, get_soup)


class Cart(object):

    def __init__(self, session, base_url, order_id=None):
        self.session = session
        self.base_url = base_url
        self.order_id = None
        if order_id is not None:
            self.order_id = str(order_id)

    def add_dataset(self, dataset):
        url = '%s/download/content/%s' % (self.base_url, dataset.dataset_id)
        data = get_form_params(
            self.session,
            url,
            ['form_build_id', 'form_id', 'form_token', 'product_id']
        )

        files = dataset.get_filenames()

        if dataset.is_singlefile():
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

        r = self.session.post(url, files=data)
        return r.status_code == 200

    def place_order(self):
        if self.order_id is not None:
            return

        url = '%s/download/cart' % self.base_url
        data = get_form_params(
            self.session,
            url,
            ['form_build_id', 'form_id', 'form_token']
        )
        data['op'] = 'Bestill'
        response = self.session.post(url, data=data)
        url2 = response.url

        m = re.search(
            'http://data\.kartverket\.no/download/checkout/(\d*)/checkout',
            url2
        )
        if m is not None:
            self.order_id = m.group(1)
        else:
            self.order_id = None

        data2 = get_form_params(
            self.session,
            url2,
            ['form_build_id', 'form_id', 'form_token']
        )
        data2['op'] = 'Fortsett'

        self.session.post(url2, data=data2)

    def get_download_links(self):
        url = '%s/download/mine/downloads' % self.base_url
        soup = get_soup(self.session, url)

        links = []
        for table in soup.findAll('table', {'class': 'views-table'}):
            order_id = table\
                .find('caption').text\
                .split(' |')[0]\
                .replace('Ordrenummer: ', '')
            if order_id == self.order_id:
                for tr in table.find('tbody').findAll('tr'):
                    links.append(tr.find('a')['href'])
        return links
