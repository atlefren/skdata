# -*- coding: utf-8 -*-
import json

import requests

from get_geojson_url import get_geojson_url
from util import spaces_to_underscores, replace_norwegian_chars


class Dataset(object):

    def __init__(self, dataset_id, base_url):
        self.dataset_id = dataset_id
        self.base_url = base_url
        self.kms_widget = None

    def exists(self):
        kms = self._get_kms_widget()
        return kms is not None and bool(kms)

    def is_singlefile(self):
        service_name = self._get_kms_widget().get('service_name', None)
        return service_name is None

    def get_filenames(self):
        kms_widget = self._get_kms_widget()
        service_name = kms_widget.get('service_name', None)
        if service_name is None:
            return [kms_widget.get(u'selection_details', None)]

        url = get_geojson_url(service_name)
        if url is None:
            return []

        filenames = []
        r = requests.get(url)
        for feature in r.json()['features']:
            file_id = feature.get('id', None)
            name = feature['properties'].get('n', None)
            selection_details = kms_widget.get(u'selection_details')
            service_layer = kms_widget.get(u'service_layer', None)
            dataformat = kms_widget.get(u'dataformat')

            if file_id is None:
                filename = name + selection_details
            else:
                filename = '%s_%s%s' % (file_id, name, selection_details)

            ext = 'sid' if kms_widget[u'dataformat'] == 'MrSID' else 'zip'

            filename = '%s_%s_%s.%s' % (
                service_layer,
                spaces_to_underscores(filename),
                dataformat,
                ext
            )

            filename = replace_norwegian_chars(filename)
            filenames.append(unicode(filename).encode('utf8'))

        return filenames

    def _get_kms_widget(self):
        if self.kms_widget is None:
            url = '%s/download/content/%s' % (self.base_url, self.dataset_id)
            r = requests.get(url)
            r.encoding = 'iso-8859-1'
            line = next(line for line in r.text.split('\n') if
                        line.startswith('jQuery.extend(Drupal.settings'))
            self.kms_widget = json.loads(
                line.replace('jQuery.extend(Drupal.settings, ', '').replace(');', '')
            ).get('kms_widget', {})
        return self.kms_widget
