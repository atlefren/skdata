# -*- coding: utf-8 -*-

URLS = {
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


def get_geojson_url(service_type):
    url = URLS.get(service_type, None)
    if url is not None:
        return 'http://www.norgeskart.no%s' % url
    return None
