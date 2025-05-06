"""
:module: mustang_client.py
:auth: Nathan T. Stevens
:email: ntsteven@uw.edu
:org: Pacific Northwest Seismic Network
:license: GPLv3
:purpose: A lightweight MUSTANG query client that returns formatted pandas DataFrames
    of queried time-series.

"""


import requests
import pandas as pd
from collections import deque

BASE_URL = 'http://service.iris.edu/mustang/measurements/1'

class MustangClient(object):
    """A simple client for querying MUSTANG quality assessment time series
    data from IRIS webservices using the python `requests` library

    :param cache_size: maximum number of queries to store in local cache, defaults to 20
    :type cache_size: int-like, optional
    :param base_url: base query url, defaults to 'http://service.iris.edu/mustang/measurements/1
    :type base_url: str, optional
    :param nodata: nodata code, defaults to 404
    :type nodata: int, optional
    """    
    def __init__(self, cache_size=20, base_url=BASE_URL, nodata=404):
        """Initialize a MustangClient object

        :param cache_size: maximum number of queries to store in local cache, defaults to 20
        :type cache_size: int-like, optional
        :param base_url: base query url, defaults to 'http://service.iris.edu/mustang/measurements/1
        :type base_url: str, optional
        :param nodata: nodata code, defaults to 404
        :type nodata: int, optional
        """        
        self.cache = deque(maxlen=cache_size)
        self.queries = deque(maxlen=cache_size)
        self.base_url = base_url
        self._nodata = nodata
        

    def query_mustang(self, metric, **options):
        """
        Compose and execute a mustang metric query using key-word arguments and strings
        as defined in the MUSTANG documentation:
        https://service.iris.edu/mustang/measurements/1/

        :param metric: metric(s) to query. Accepts lists of metrics with comma delimiters
        :type metric: str
        :param options: key-word argument collector for all other optional query inputs

        NOTE: the 'format'
        """
        full_str = self._compose_query(metric, **options)
        payload = self._cache_query(full_str)
        df = self._parse_payload_text(payload)
        return df
    

    def _cache_query(self, full_str):
        """Check if the composed query string has already been run
        if so, fetch the payload from that query saved in cache
        if not, fetch a payload from the web and save the query and payload
        to cache and query

        :param full_str: _description_
        :type full_str: _type_
        :return: _description_
        :rtype: _type_
        """        
        # Check if query is already cached
        if full_str in self.queries:
            for _e, _c in enumerate(self.cache):
                if self.queries[_e] == full_str:
                    payload = _c
        else:
            payload = requests.get(full_str)
            self.cache.appendleft(payload)
            self.queries.appendleft(full_str)

        return payload

        
    def _compose_query(self, metric, **options):
        """Compose a query string for MUSTANG

        :param metric: _description_
        :type metric: _type_
        :return: _description_
        :rtype: _type_
        """        
        options.update({'format':'text'})

        qstr = f'query?metric={metric}'
        for _k, _v in options.items():
            qstr += f'&{_k}={_v}'

        # Form full query string
        full_str = f'{self.base_url}/{qstr}&nodata={self._nodata}'
        return full_str

    def _parse_payload_text(self, payload):
        """Parse a single or multi-metric text output from a payload into
        a dictionary of pandas DataFrames for each metric. Dictionary is
        keyed by metric name as formatted for the MUSTANG query

        E.g., num_gaps -> 'num_gaps', not 'Num Gaps Metric"

        """        
        if payload.status_code == self._nodata:
            return None
        
        text = payload.text
        # Split lines on newline
        lines = text.split('\n')

        metrics = []
        hdr = []
        datas = {}
        for line in lines:
            if 'Metric' in line:
                metric = '_'.join(line[1:-1].split(' ')[:-1]).lower()
                metrics.append(metric)
                datas.update({metric:[]})
            elif 'value' in line:
                if hdr == []:
                    hdr = [p[1:-1] for p in line.split(',')]
            elif len(line) > 0:
                _ln = []
                for _e, _l in enumerate(line.split(',')):
                    _v = _l[1:-1]
                    if _e == 0:
                        if _v.isnumeric():
                            _v = int(_v)
                        elif _v.upper() in ['TRUE','FALSE']:
                            _v = bool(_v)
                        else:
                            try:
                                _v = float(_v)
                            except:
                                pass
                    elif _e == 1:
                        pass
                    elif _e >= 2:
                        _v = pd.Timestamp(_v)
                    _ln.append(_v)
                datas[metric].append(_ln)

        outs = {}  
        for _k, _v in datas.items():
            _df = pd.DataFrame(_v, columns=[_k] + hdr[1:])
            outs.update({_k:_df})
        return outs
                
                    


if __name__ == '__main__':
    import matplotlib.pyplot as plt
    # Run an example on UW.MBW.01
    query = {'metric':'sample_unique,num_gaps,sample_min',
             'net':'UW',
             'sta':'MBW',
             'loc':'01',
             'cha':'EHZ',
             'timewindow':'2022-05-01T00:00:00,2023-12-31T00:00:00'}
    
    client = MustangClient()
    outs = client.query_mustang(**query)
    fig = plt.figure()
    gs = fig.add_gridspec(nrows=3)
    ax0 = fig.add_subplot(gs[0])
    axes = [ax0]
    axes += [fig.add_subplot(gs[_e], sharex=ax0) for _e in range(1,3)]
    for _e, (_k, _v) in enumerate(outs.items()):
        axes[_e].plot(_v.start, _v[_k],'.', alpha=0.5, label=_k)
        axes[_e].legend()
        axes[_e].set_ylabel(_k)
    plt.show()

