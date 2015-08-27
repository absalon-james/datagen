import json
import requests


class Datapoint(dict):
    """
    Models a datapoint to be ingested into blueflood.

    """
    def __init__(self, name, value, collection_time=None,
                 ttl_seconds=None, unit=None):
        """
        Inits the datapoint

        @param name - String name of the metric
        @param value - Value of the metric
        @param collection_time - Time of collection
        @param ttl_seconds - Number of seconds for datapoint to live
        @param unit - String unit of the metric

        """
        self['metricValue'] = value
        self['metricName'] = name

        # Set collection time
        if collection_time:
            collection_time = int(max(collection_time, 0) * 1000)
            self['collectionTime'] = collection_time

        # Set ttl
        if not ttl_seconds:
            ttl_seconds = 60 * 60 * 24 * 180
        ttl_seconds = max(ttl_seconds, 0)
        self['ttlInSeconds'] = ttl_seconds

        # Set units
        if unit:
            self['unit'] = unit


class BluefloodClient(object):
    """
    Simple client for interacting with blueflood.

    """
    # Options available for selection on some GET requests
    selectables = [
        'average',
        'min',
        'max',
        'numPoints',
        'variance'
    ]

    def __init__(self, tenant_id, location, write_port=19000, read_port=20000):
        """
        Inits the client.

        @param tenant_id - String id of tenant
        @param location - Location of blueflood
        @param write_port - Integer port to write to
        @param read_port - Integer port to read from

        """
        self.tenant_id = tenant_id
        self.location = location
        self.write_port = write_port
        self.read_port = read_port
        url_template = 'http://%s:%s/v2.0/%s'
        self.write_url = url_template % (
            self.location,
            self.write_port,
            self.tenant_id
        )
        self.read_url = url_template % (
            self.location,
            self.read_port,
            self.tenant_id
        )

    def selects(self, **kwargs):
        """
        @param **kwargs - Dictionary containing selectables.

        @return - String - comma separated list of selectables

        """
        return ','.join([s for s in self.selectables
                         if s in kwargs and kwargs.get(s)])

    def read_params(self, start, stop, points, resolution):
        """
        Sets up a dictionary with basic read parameters.

        @param start - Float time in seconds
        @param stop - Float time in seconds
        @param points - Integer number of points
        @return - Dictionary

        """
        start = self.prep_time(start)
        stop = self.prep_time(stop)
        params = {
            'from': start,
            'to': stop,
        }
        if resolution:
            params['resolution'] = resolution
        elif points:
            params['points'] = points
        return params

    def prep_time(self, value):
        """
        Ensures timestamp is at least 0 and converts from seconds to
        milliseconds.

        @param value - Float time in seconds
        @return inter - Integer time in milliseconds.

        """
        return int(max(value, 0) * 1000)

    def metric_list(self, query='*'):
        """
        Search for all metrics matching the query

        @param query - String query
        @return - List

        """
        url = "%s/metrics/search" % self.read_url
        r = requests.get(url, params={'query': query})
        r.raise_for_status()
        return r.json()

    def get_metric(self, start, stop, metric,
                   points=None, resolution=None, **kwargs):
        """
        Returns a single metric.

        @param start - Integer start time
        @param stop - Integer stop time
        @param metric - String name of metric
        @param points - Integer number of points
        @param resolution - One of FULL|MIN5|MIN20|MIN60|MIN240|MIN1440
        @param kwargs - Remaining keyword arguments should be selectables.
        @return - Dictionary

        """
        url = '%s/views/%s' % (self.read_url, metric)
        params = self.read_params(start, stop, points, resolution)
        selects = self.selects(**kwargs) if kwargs else None
        if selects:
            params['select'] = selects
        params['resolution'] = 'FULL'
        r = requests.get(url, params=params)
        r.raise_for_status()
        return r.json()

    def get_metrics(self, start, stop, metrics,
                    points=None, resolution=None, **kwargs):
        """
        Returns multiple metrics

        @param start - Integer time in seconds
        @param stop - Integer time in seconds
        @param metrics - String list of metric names
        @param points - Integer number of points
        @param resolution - One of FULL|MIN5|MIN20|MIN60|MIN240|MIN1440
        @param kwargs - Remaining keyword arguments should be selectables.
        @return - Dictionary

        """
        url = '%s/views' % self.read_url
        params = self.read_params(start, stop, points)
        selects = self.selects(**kwargs) if kwargs else None
        if selects:
            params['select'] = selects
        r = requests.post(url, data=json.dumps(metrics), params=params)
        r.raise_for_status()
        return r.json()

    def ingest(self, points):
        """
        Expects a list of dictionaries representing metric points.

        @param points - List of point dictionaries.

        """
        url = '%s/ingest' % self.write_url
        r = requests.post(url, data=json.dumps(points))
        r.raise_for_status()
