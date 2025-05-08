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
import warnings
import pandas as pd
from collections import deque

# MUSTANG Web Service Base URL
BASE_URL = 'http://service.iris.edu/mustang/measurements/1'
# Mustang Metrics (Including TS PROTOTYPE)
MMETS = ['amplifier_saturation','asl_coherence',
         'calibration_signal','clock_locked',
         'cross_talk','data_latency',
         'dc_offset','dead_channel_gsn',
         'dead_channel_lin','digital_filter_charging',
         'digitizer_clipping','event_begin',
         'event_end','event_in_progress',
         'feed_latency','glitches',
         'gsn_timing','max_gap',
         'max_range','max_stalta',
         'metric_error','missing_padded_data',
         'num_gaps','num_overlaps','num_spikes'
         'orientation_check','pct_above_nhnm',
         'percent_availability','polarity_check',
         'pressure_effects',
         'sample_max','sample_min',
         'sample_mean','sample_median','sample_rate_channel',
         'sample_rate_resp','sample_rms','sample_snr',
         'sample_unique','spikes','suspect_time_tag',
         'telemetry_sync_error','timing_correction','timing_quality',
         'total_latency','transfer_function',
         'ts_channel_gap_list','ts_channel_up_time',
         'ts_gap_length','ts_gap_length_total',
         'ts_max_gap','ts_max_gap_total','ts_num_gaps',
         'ts_num_gaps_total','ts_percent_availability',
         'ts_percent_availability_total']



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
        

    def get_metrics(self, metric, indexing='start', **options):
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
        df = self._parse_payload_text(payload, indexing=indexing)
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
        metric = self._validate_metric(metric)
        qstr = f'query?metric={metric}'
        for _k, _v in options.items():
            qstr += f'&{_k}={_v}'

        # Form full query string
        full_str = f'{self.base_url}/{qstr}&nodata={self._nodata}'
        return full_str

    def _validate_metric(self, metric):
        if ' ' in metric:
            raise ValueError('metric cannot include whitespaces')
        if isinstance(metric, list):
            parts = metric
        elif isinstance(metric, str):
            parts = metric.split(',')
        else:
            raise TypeError('metric must be type str or a list-like containing individual metric name strings')
        mets = set([])
        for _p in parts:
            if _p not in MMETS:
                warnings.warn(f'{_p} is not included in MUSTANG metrics - skipping')
            else:
                mets.add(_p)
        mets = list(mets)
        return ','.join(mets)


    def _parse_payload_text(self, payload, indexing=None):
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


        if indexing in _df.columns:
            if indexing in ['start','end','lddate']:
                _o = pd.DataFrame()
                for _e, (_k, _v) in enumerate(outs.items()):
                    if _e == 0:
                        _o = _v[['target',_k]]
                        _o.index = _v[indexing].values
                    else:
                        _oo = _v[_k]
                        _oo.index = _v[indexing].values
                        _o = pd.concat([_o, _oo], axis=1, ignore_index=False)
                _o.index.name = indexing
                return _o
            else:
                return outs
                
                    


if __name__ == '__main__':
    # Example query & plot
    import matplotlib.pyplot as plt
    # Run an example on UW.MBW.01
    query = {'metric':['sample_unique','num_gaps','sample_min','max_range','percent_availability'],
             'net':'UW',
             'sta':'MBW',
             'loc':'01',
             'cha':'EHZ',
             'timewindow':'2023-01-01T00:00:00,2023-12-31T00:00:00'}
    
    client = MustangClient()
    df = client.get_metrics(**query)
    fig = plt.figure()
    gs = fig.add_gridspec(nrows=len(query['metric']))
    ax0 = fig.add_subplot(gs[0])
    axes = [ax0]
    axes += [fig.add_subplot(gs[_e], sharex=ax0) for _e in range(1,len(query['metric']))]
    for _e, _m in enumerate(query['metric']):
        _df = df[_m]
        axes[_e].plot(_df.index, _df.values,'.-', alpha=0.5, label=_m)
        axes[_e].legend()
        axes[_e].set_ylabel(_m)
    plt.show()

