# -*- coding: utf-8 -*-
import json
import os

from dataset import Dataset


class DirectDownload(object):

    def __init__(self, dataset, base_url):
        self.dataset = dataset
        self.base_url = base_url
        self.url = self.get_url()

    def get_url(self):
        with open('dataset_urls.json', 'r') as f:
            data = json.loads(f.read())
            if self.dataset in data:
                return data[self.dataset]
        return None

    def exists(self):
        return self.url is not None

    def get_links(self):
        dataset = Dataset(self.dataset, self.base_url)
        links = []
        for filename in dataset.get_filenames():
            links.append('%s/%s' % (self.url, filename))
        return links
