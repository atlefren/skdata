# -*- coding: utf-8 -*-
import re

from util import (get_form_params, get_soup)


def stringify_files(files):
    return '[%s]' % ', '.join(['"%s"' % file for file in files])


def make_chunk(files, max_len):
    '''
        Split the files into "chunks" that, when stringified with
        stringify_files is no longer than max_len
    '''
    file_chunk = []
    chunk_length = 0
    cont = True
    while cont and len(files) > 0:
        file = files.pop()
        length = len(file) + 4  # length of filename + quotes + ,
        chunk_length += length
        if chunk_length > max_len:
            files.append(file)  # re-add the file so it's not forgotten
            cont = False
        else:
            file_chunk.append(file)
    return file_chunk


def make_chunks(files, max_len):
    chunks = []
    while len(files) > 0:
        chunks.append(make_chunk(files, max_len))
    return chunks


class Cart(object):

    def __init__(self, session, base_url, order_id=None):
        self.session = session
        self.base_url = base_url
        self.order_id = None
        if order_id is not None:
            self.order_id = str(order_id)

    def _add_files(self, url, form_params, files, is_singlefile):
        if is_singlefile:
            num = '1 samlet fil'
        else:
            num = '%s filer' % len(files)
        files = stringify_files(files)
        data = {
            'product_id': ('', form_params['product_id']),
            'form_build_id': ('', form_params['form_build_id']),
            'form_token': ('', form_params['form_token']),
            'form_id': ('', form_params['form_id']),
            'line_item_fields[field_selection][und][0][value]': ('', files),
            'line_item_fields[field_selection_text][und][0][value]': ('', num),
            'quantity': ('', '1'),
            'op': ('', 'Legg i kurv')
        }

        r = self.session.post(url, files=data)

        return r.status_code == 200

    def add_dataset(self, dataset):
        url = '%s/download/content/%s' % (self.base_url, dataset.dataset_id)
        form_params = get_form_params(
            self.session,
            url,
            ['form_build_id', 'form_id', 'form_token', 'product_id']
        )

        files = dataset.get_filenames()

        if dataset.is_singlefile():
            return self._add_files(url, form_params, files, True)

        MAX_LEN = 2550

        if len(stringify_files(files)) > MAX_LEN:
            chunks = make_chunks(files, MAX_LEN)
        else:
            chunks = [files]

        for chunk in chunks:
            self._add_files(url, form_params, chunk, False)

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
