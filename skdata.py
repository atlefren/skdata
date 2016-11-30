# -*- coding: utf-8 -*-

import os

import requests
from bs4 import BeautifulSoup
import click

from util import (get_soup, get_form_params)
from download import download_files, check_dir
from dataset import Dataset
from cart import Cart
from direct_download import DirectDownload


BASE_URL = 'http://data.kartverket.no'


def get_categories():
    '''
        Get all top-level categories
    '''
    url = '%s/download/' % BASE_URL
    soup = get_soup(requests, url)
    div = soup.find('div', {'class': 'field-item'})
    categories = []
    for td in div.find('table').findAll('td'):
        h3 = td.find('h3')
        if h3 is not None:
            link = td.findAll('p')[-1].find('a')['href']
            category_id = next(l for l in link.split('?')[-1].split('&')
                               if l.startswith(u'korttype')).split('=')[-1]
            categories.append({
                'name': unicode(h3.text).encode('iso-8859-1'),
                'id': int(category_id)
            })
    return categories


def parse_dataset_list(soup):
    datasets = []
    for row in soup.findAll('div', {'class': 'views-row'}):
        title = row.find('div', {'class': 'title'}).find('a')
        datasets.append({
            'name': unicode(title.text).encode('iso-8859-1'),
            'id': title['href'].split('/')[-1]
        })
    return datasets


def get_dataset_page(category_id, page, session):
    url = '%s/download/content/geodataprodukter?korttype=%s&page=%s' % (
        BASE_URL,
        category_id,
        page
    )
    soup = get_soup(session, url)
    data = parse_dataset_list(soup)
    if data is not None and len(data) > 0:
        return data, True
    return None, False


def get_datasets(category_id):
    '''
        Get a list of all datasets in a category
    '''
    has_data = True
    datasets = []
    page = 0
    while has_data:
        data, has_data = get_dataset_page(category_id, page, requests)
        page += 1
        if data is not None:
            datasets += data
    return datasets


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

    soup = BeautifulSoup(r.text, 'html.parser')

    if soup.find('div', {'class': 'messages error'}):
        raise Exception('could not log in')

    return session


def download_dataset(dataset_id, session, directory=None):

    # create a dataset
    dataset = Dataset(dataset_id, BASE_URL)
    if not dataset.exists():
        raise IndexError('Unknown dataset {dataset_id}'.format(dataset_id=dataset_id))

    # create a cart
    cart = Cart(session, BASE_URL)

    click.echo('Add dataset to cart')
    # add the dataset to the cart
    cart.add_dataset(dataset)

    click.echo('place order')
    # place the order
    cart.place_order()
    click.echo('order with id={order_id} placed'.format(order_id=cart.order_id))

    order_id = cart.order_id
    if order_id is None:
        order_id = 'unknown'
    if directory is None:
        directory = os.path.join('dl', order_id)
    else:
        check_dir(directory)

    dd = DirectDownload(dataset_id, BASE_URL)
    if dd.exists():
        links = dd.get_links()
    else:
        links = cart.get_download_links()
    click.echo('Downloading {len} files'.format(len=len(links)))
    # actually download the files
    download_files(links, directory, session)


def download_impl(dataset_id, session, directory=None):
    click.echo('Download data from {dataset_id}'.format(dataset_id=dataset_id))
    download_dataset(dataset_id, session, directory=directory)


@click.group()
def cli():
    pass


@click.command(help='List categories')
def categories():
    click.echo('Categories:')
    for category in get_categories():
        click.echo('{id}: {name}'.format(**category))


@click.command(help='Show datasets in category')
@click.argument('category_id')
def datasets(category_id):
    for dataset in get_datasets(category_id):
        click.echo('{id}: {name}'.format(**dataset))




@click.command(help='Download all files in specified dataset')
@click.argument('dataset_id')
@click.argument('username')
@click.argument('password')
@click.option('--directory', help='directory to place result in')
def download(dataset_id, username, password, directory):
    session = login(username, password)
    download_impl(dataset_id, session, directory=directory)


@click.command(help='Download all files on the server')
@click.argument('username')
@click.argument('password')
@click.option('--directory', help='directory to place result in')
def getall(username, password, directory='dl'):
    session = login(username, password)
    for category in get_categories():
        for dataset in get_datasets(category['id']):
            d = os.path.join(directory, dataset['id'])
            print dataset['id']
            download_impl(dataset['id'], session, directory=directory)


cli.add_command(categories)
cli.add_command(datasets)
cli.add_command(download)
cli.add_command(getall)

if __name__ == '__main__':
    cli()
