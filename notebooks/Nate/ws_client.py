"""
:module: ws_client.py
:auth: Nathan T. Stevens
:email: ntsteven@uw.edu
:org: Pacific Northwest Seismic Network
:license: GPLv3
:purpose: A lightweight IRIS webservices client for requesting data quality metrics and data
    availability information from the MUSTANG and FDSNWS services.
"""
import logging
import requests
import pandas as pd
from collections import deque

logger = logging.getLogger('mustang_client')

class WebServiceClient(object):
    """A client baseclass for requesting metadata from 
    webservices using the `requests` python library

    :param base_url: base url to be used for all requests, defaults to 'http://service.iris.edu'
    :type base_url: str, optional
    :param cache_size: number of queries and their requests output to cache locally, defaults to 20
    :type cache_size: int-like, optional
    :param nodata: no data code, defaults to 404
    :type nodata: int, options
        Supported values: 404 and 204
    """    
    def __init__(
            self,
            base_url='http://service.iris.edu',
            service=None,
            cache_size=20,
            nodata=404):
        """Initialize a WebServiceClient object

        :param base_url: base url to be used for all requests, defaults to 'http://service.iris.edu'
        :type base_url: str, optional
        :param cache_size: number of queries and their requests output to cache locally, defaults to 20
        :type cache_size: int-like, optional
        :param nodata: no data code, defaults to 404
        :type nodata: int, options
        Supported values: 404 and 204
        """        
        self.base_url = base_url
        if isinstance(service, str):
            self.base_url += f'/{service}'
        self.cache = deque(maxlen=cache_size)
        self.queries = deque(maxlen=cache_size)
        self.nodata = nodata


    def __setattr__(self, key, value):
        if key in ['service','interface']:
            if value is None:
                value = ''
            elif isinstance(value, str):
                pass
            else:
                raise ValueError
        if key == 'cache_size':
            if value is None:
                pass
            else:
                value = int(value)
                if value < 1:
                    raise ValueError('cache_size must be positive int-like or None')
        if key == 'nodata':
            if int(value) in [204, 404]:
                pass
            else:
                raise ValueError('nodata must be 204 or 404')
        super().__setattr__(key, value)        

    def request(self, interface, version=1, method='query', **options):
        """Execute a request for (meta)data from the intended webservice
        base_url/service/version/query?{k}={v}&...&nodata=nodata

        :param service: _description_
        :type service: _type_
        :param version: _description_, defaults to 1
        :type version: int, optional
        :return: _description_
        :rtype: _type_
        """        
        url = self._form_url(
            interface=interface,
            version=version,
            method=method,
            **options)
        payload = self._webservice_request(url)
        return payload
    
    def __repr__(self):
        """String representation of this WebserviceClient object's contents"""
        rstr = f'{self.__class__.__name__} ({self.base_url})\n'
        rstr += f'{len(self.cache):d} cached querie(s) with status codes:\n'
        scodes = [_pl.status_code for _pl in self.cache]
        rstr += f'{scodes}'
        return rstr

    def _check_cache(self, query_str):
        """Check if a query is cached and either
        return the payload from that query or
        return None if not present in cache

        :param query_str: query string
        :type query_str: str
        :return: cached payload or None
        :rtype: _type_
        """        
        if query_str in self.queries:
            for _e, _q in enumerate(self.queries):
                if _q == query_str:
                    return self.cache[_e]
        else:
            return None
    
    def _document_query(self, query_str, payload):
        """Private method 

        append the query string and returned `requests.get` payload
        to the queries and cache objects, respectively

        :param query_str: query string
        :type query_str: str
        :param payload: requests payload
        :type payload: requests.models.Response
        """        
        self.cache.appendleft(payload)
        self.queries.appendleft(query_str)

    def _form_url(self, interface=None, version=1, method='query', **options):
        """Formulate a  URL for the target webservice
        with options forming the key=value pairs, delimited by &'s

        General structure:
        {base_url}/{service}/{interface}/{version}/{method}?{options}&nodata={nodata}
        
        E.g., 
        http://service.iris.edu/mustang/metrics/1/query?...

        :param service: service name
        :type service: str
        :param interface: interface name
        :type interface: str
        :param version: service interface version, defaults to 1
        :type version: int, optional
        :return: formatted query url
        :rtype: str
        """        
        if isinstance(interface, str):
            q_str = f'{self.base_url}/{interface}/{version:d}/{method}?'
        else:
            q_str = f'{self.base_url}/{version:d}/{method}?'
        for _k, _v in options.items():
            q_str += f'{_k}={_v}&'
        q_str += f'nodata={self.nodata:d}'
        return q_str
    
    def _webservice_request(self, query_str):
        """Run a request to the targeted webservice, first checking
        if the request has already been run and stored in cache

        :param query_str: query url string
        :type query_str: str
        :return: payload
        :rtype: requests.models.Response
        """        
        payload = self._check_cache(query_str)
        if payload is None:
            payload = requests.get(query_str)
            self._document_query(query_str, payload)
        return payload
    
    def _parse_payload(self, payload):
        return payload



class MustangClient(WebServiceClient):
    """
    A client for the IRIS Webservices MUSTANG station data quality service

    :param cache_size: maximum number of queries to cache locally, defaults to 20
    :type cache_size: int, optional
    :param nodata: nodata status code, defaults to 404
        Supported values: 204, 404
    :type nodata: int, optional
    """
    def __init__(self, cache_size=20, nodata=404):
        """
        Initialize a MustangClient object

        :param cache_size: maximum number of queries to cache locally, defaults to 20
        :type cache_size: int, optional
        :param nodata: nodata status code, defaults to 404
            Supported values: 204, 404
        :type nodata: int, optional
        """
        super().__init__(service='mustang', cache_size=cache_size, nodata=nodata)
    

    def request(self, service, version=1, **options):
        # Handle list-like options inputs
        for _k, _v in options.items():
            if isinstance(_v, list):
                options.update({_k:','.join([str(_e) for _e in _v])})
        payload = super(MustangClient, self).request(service, version=version, **options)
        return payload

    def measurements_request(self, version=1, indexing='start', **options):
        """Run a request for station data quality metadata from the MUSTANG measurements
        service and return the request formatted as a Pandas DataFrame

        :param version: service version to use, defaults to 1
        :type version: int, optional
        :param indexing: index column to use for combining multiple metrics, defaults to 'start'
        :type indexing: str, optional
        :return: parsed payload from request
        :rtype: pandas.DataFrame
        """        
        options.update({'format':'text'})
        if 'include_extra_times' in options.keys():
            iet = options.pop('include_extra_times')
        else:
            iet = False
        payload = self.request('measurements', version=version, **options)
        parsed = self._parse_measurements_payload(payload, indexing=indexing, include_extra_times=iet)
        return parsed            
    
    def _parse_measurements_payload(self, payload, indexing='start', include_extra_times=False):
        """
        TODO: Turn indexing and target into a multi-index
        """
        text = payload.text
        # Split lines on newline
        lines = text.split('\n')

        metrics = []
        hdr = []
        datas = {}
        # Iterate across each line
        for line in lines:
            # If metric is in the line, capture that metric
            if 'Metric' in line:
                metric = '_'.join(line[1:-1].split(' ')[:-1]).lower()
                metrics.append(metric)
                datas.update({metric:[]})
             #If value is in line, parse this line as the header line
            elif 'value' in line:
                # Only if this hasn't been done already
                if hdr == []:
                    hdr = [p[1:-1] for p in line.split(',')]
            # Parse all others as data line, so long as the line has content
            elif len(line) > 0:
                _ln = []
                for _e, _l in enumerate(line.split(',')):
                    _v = _l[1:-1]
                    # Parse values
                    if _e == 0:
                        # If value is entirely numeric, parse as int
                        if _v.isnumeric():
                            _v = int(_v)
                        # If value looks BOOL, parse as bool
                        elif _v.upper() in ['TRUE','FALSE']:
                            _v = bool(_v)
                        # Otherwise try to parse as float
                        else:
                            try:
                                _v = float(_v)
                            except:
                                pass
                    # Pass targets
                    elif _e == 1:
                        pass
                    # Parse timestamps
                    elif _e >= 2:
                        _v = pd.Timestamp(_v)
                    _ln.append(_v)
                datas[metric].append(_ln)

        output = pd.DataFrame()
        # Convert lists & keys into dataframes
        for _k, _v in datas.items():
            # Basic conversion to DF
            _df = pd.DataFrame(_v, columns=[_k] + hdr[1:])
            # Create multi-index
            if indexing in ['start','end','lddate']:
                midx = pd.MultiIndex.from_arrays((_df[indexing].values, _df.target.values), names=(indexing,'target'))
            else:
                midx = pd.MultiIndex.from_arrays((_df.index.values, _df.target.values), names=('index','target'))
            keep_cols = []
            for _c in _df.columns:
                if _c in midx.names:
                    pass
                elif _c in output.columns:
                    pass
                else:
                    keep_cols.append(_c)
            _df = _df[keep_cols]
            _df.index = midx
            output = pd.concat([output, _df], axis=1, ignore_index=False)
        outsortcol = []
        timecols = []
        for _c in output.columns:
            if _c in ['start','end','lddate']:
                timecols.append(_c)
            else:
                outsortcol.append(_c)
        if include_extra_times:
            outsortcol += timecols
        output = output[outsortcol]
        return output



class AvailabilityClient(WebServiceClient):
    def __init__(self, service='fdsnws',cache_size=20, nodata=404):
        super().__init__(service=service, cache_size=cache_size, nodata=nodata)
    
    def request(self, version=1, method='query',**options):
        for _k, _v in options.items():
            if isinstance(_v, list):
                options.update({_k:','.join([str(_e) for _e in _v])})
        options.update({'format':'geocsv'})
        payload = super(AvailabilityClient, self).request(interface='availability',version=version,method=method, **options)
        return payload
    
    def availability_request(self, method='query', **options):
        payload = self.request(method=method, **options)
        parsed = self._parse_availability_geocsv(payload)
        return parsed

    
    def _parse_availability_geocsv(self, payload):
        lines = payload.text.split('\n')
        cols = []
        body = []
        for _l in lines:
            if '#' in _l:
                isheader = True
            else:
                isheader = False
            if isheader:
                continue
            
            if 'Network|' in _l:
                cols = _l.split('|')
            elif len(_l) == 0:
                continue
            else:
                parts = _l.split('|')
                _o = parts[:5]
                _o.append(float(parts[5]))
                _o.append(pd.Timestamp(parts[6]))
                _o.append(pd.Timestamp(parts[7]))
                body.append(_o)
        parsed = pd.DataFrame(body, columns=cols)
        return parsed
            



### GRAVEYARD ###
# Nate Stevens 9 MAY 2025
# An earlier version of the MustangClient that still needs to be scavenged for 
# parts like checking against MMETS and providing logging information

# # MUSTANG Web Service Base URL
# BASE_URL = 'http://service.iris.edu/mustang/'
# MMURL = f'{BASE_URL}measurements/1'
# # Mustang Metrics (Including TS PROTOTYPE)
# MMETS = ['amplifier_saturation','asl_coherence',
#          'calibration_signal','clock_locked',
#          'cross_talk','data_latency',
#          'dc_offset','dead_channel_gsn',
#          'dead_channel_lin','digital_filter_charging',
#          'digitizer_clipping','event_begin',
#          'event_end','event_in_progress',
#          'feed_latency','glitches',
#          'gsn_timing','max_gap',
#          'max_range','max_stalta',
#          'metric_error','missing_padded_data',
#          'num_gaps','num_overlaps','num_spikes'
#          'orientation_check','pct_above_nhnm',
#          'percent_availability','polarity_check',
#          'pressure_effects',
#          'sample_max','sample_min',
#          'sample_mean','sample_median','sample_rate_channel',
#          'sample_rate_resp','sample_rms','sample_snr',
#          'sample_unique','spikes','suspect_time_tag',
#          'telemetry_sync_error','timing_correction','timing_quality',
#          'total_latency','transfer_function',
#          'ts_channel_gap_list','ts_channel_up_time',
#          'ts_gap_length','ts_gap_length_total',
#          'ts_max_gap','ts_max_gap_total','ts_num_gaps',
#          'ts_num_gaps_total','ts_percent_availability',
#          'ts_percent_availability_total']



# class MustangClient(object):
#     """A simple client for querying MUSTANG quality assessment time series
#     data from IRIS webservices using the python `requests` library

#     :param cache_size: maximum number of queries to store in local cache, defaults to 20
#     :type cache_size: int-like, optional
#     :param base_url: base query url, defaults to 'http://service.iris.edu/mustang/measurements/1
#     :type base_url: str, optional
#     :param nodata: nodata code, defaults to 404
#     :type nodata: int, optional
#     """    
#     def __init__(self, cache_size=20, base_url=BASE_URL, nodata=404):
#         """Initialize a MustangClient object

#         :param cache_size: maximum number of queries to store in local cache, defaults to 20
#         :type cache_size: int-like, optional
#         :param base_url: base query url, defaults to 'http://service.iris.edu/mustang/measurements/1
#         :type base_url: str, optional
#         :param nodata: nodata code, defaults to 404
#         :type nodata: int, optional
#         """        
#         self.cache = deque(maxlen=cache_size)
#         self.queries = deque(maxlen=cache_size)
#         self.base_url = base_url
#         self._nodata = nodata
#         self.logger = logging.getLogger(self.__class__.__name__)
        

#     def get_metrics(self, metric, indexing='start', **options):
#         """
#         Compose and execute a mustang metric query using key-word arguments and strings
#         as defined in the MUSTANG documentation:
#         https://service.iris.edu/mustang/measurements/1/

#         :param metric: metric(s) to query. Accepts lists of metrics with comma delimiters
#         :type metric: str
#         :param options: key-word argument collector for all other optional query inputs

#         NOTE: the 'format'
#         """
#         met_list = self._validate_metric(metric=metric)
#         if indexing in ['start','end','lddate']:
#             out = pd.DataFrame()
#         else:
#             out = {}
#         for met in met_list:
#             self.logger.info(f'getting "{met}"')
#             full_str = self._compose_query(met, **options)
#             payload = self._cache_query(full_str)
#             df = self._parse_payload_text(payload, indexing=indexing)
#             if indexing in ['start','end','lddate']:
#                 if 'target' not in out.columns:
#                     _df = df[['target',met]]
#                 else:
#                     _df = df[met]
#                 out = pd.concat([out, _df], axis=1,ignore_index=False)
#             else:
#                 out.update({met: df})
#         if isinstance(out, pd.DataFrame):
#             out = out.sort_index()
#         return out
    

#     def _cache_query(self, full_str):
#         """Check if the composed query string has already been run
#         if so, fetch the payload from that query saved in cache
#         if not, fetch a payload from the web and save the query and payload
#         to cache and query

#         :param full_str: _description_
#         :type full_str: _type_
#         :return: _description_
#         :rtype: _type_
#         """        
#         # Check if query is already cached
#         if full_str in self.queries:
#             self.logger.info(f'fetching from cache')
#             for _e, _c in enumerate(self.cache):
#                 if self.queries[_e] == full_str:
#                     payload = _c
#         else:
#             self.logger.info(f'requesting from MUSTANG')
#             payload = requests.get(full_str)
#             self.cache.appendleft(payload)
#             self.queries.appendleft(full_str)

#         return payload

        
#     def _compose_query(self, metric, **options):
#         """Compose a query string for MUSTANG

#         :param metric: _description_
#         :type metric: _type_
#         :return: _description_
#         :rtype: _type_
#         """        
#         options.update({'format':'text'})
#         # metric = self._validate_metric(metric)
#         qstr = f'query?metric={metric}'
#         for _k, _v in options.items():
#             qstr += f'&{_k}={_v}'

#         # Form full query string
#         full_str = f'{self.base_url}measurements/1/{qstr}&nodata={self._nodata}'
#         return full_str

#     def _validate_metric(self, metric):
#         if ' ' in metric:
#             raise ValueError('metric cannot include whitespaces')
#         if isinstance(metric, list):
#             parts = metric
#         elif isinstance(metric, str):
#             parts = metric.split(',')
#         else:
#             raise TypeError('metric must be type str or a list-like containing individual metric name strings')
#         mets = set([])
#         for _p in parts:
#             if _p not in MMETS:
#                 warnings.warn(f'{_p} is not included in MUSTANG metrics - skipping')
#             else:
#                 mets.add(_p)
#         mets = list(mets)
#         return mets
#         # return ','.join(mets)

#     def _get_metric_explainer(self, metric=None):
#         full_str = f'{self.base_url}metrics/1/query'
#         if metric is None:
#             pass
#         else:
#             full_str = f'{full_str}?metric={metric}'

#         payload = requests.get(full_str)
#         return payload



#     def _parse_payload_text(self, payload, indexing=None):
#         """Parse a single or multi-metric text output from a payload into
#         a dictionary of pandas DataFrames for each metric. Dictionary is
#         keyed by metric name as formatted for the MUSTANG query

#         E.g., num_gaps -> 'num_gaps', not 'Num Gaps Metric"

#         """        
#         if payload.status_code == self._nodata:
#             return None
        
#         text = payload.text
#         # Split lines on newline
#         lines = text.split('\n')

#         metrics = []
#         hdr = []
#         datas = {}
#         for line in lines:
#             if 'Metric' in line:
#                 metric = '_'.join(line[1:-1].split(' ')[:-1]).lower()
#                 metrics.append(metric)
#                 datas.update({metric:[]})
#             elif 'value' in line:
#                 if hdr == []:
#                     hdr = [p[1:-1] for p in line.split(',')]
#             elif len(line) > 0:
#                 _ln = []
#                 for _e, _l in enumerate(line.split(',')):
#                     _v = _l[1:-1]
#                     if _e == 0:
#                         if _v.isnumeric():
#                             _v = int(_v)
#                         elif _v.upper() in ['TRUE','FALSE']:
#                             _v = bool(_v)
#                         else:
#                             try:
#                                 _v = float(_v)
#                             except:
#                                 pass
#                     elif _e == 1:
#                         pass
#                     elif _e >= 2:
#                         _v = pd.Timestamp(_v)
#                     _ln.append(_v)
#                 datas[metric].append(_ln)

#         outs = {}  
#         for _k, _v in datas.items():
#             _df = pd.DataFrame(_v, columns=[_k] + hdr[1:])
#             outs.update({_k:_df})


#         if indexing in _df.columns:
#             if indexing in ['start','end','lddate']:
#                 _o = pd.DataFrame()
#                 for _e, (_k, _v) in enumerate(outs.items()):
#                     if _e == 0:
#                         _o = _v[['target',_k]]
#                         _o.index = _v[indexing].values
#                     else:
#                         _oo = _v[_k]
#                         _oo.index = _v[indexing].values
#                         _o = pd.concat([_o, _oo], axis=1, ignore_index=False)
#                 _o.index.name = indexing
#                 return _o
#             else:
#                 return outs
#
#
# if __name__ == '__main__':
#     # Example query & plot
#     import matplotlib.pyplot as plt
#     # Run an example on UW.MBW.01
#     query = {'metric':['sample_unique','num_gaps','sample_min','max_range','percent_availability'],
#              'net':'UW',
#              'sta':'MBW',
#              'loc':'01',
#              'cha':'EHZ',
#              'timewindow':'2023-01-01T00:00:00,2023-12-31T00:00:00'}
    
#     logger = logging.getLogger()
#     logger.setLevel(level=logging.INFO)
#     ch = logging.StreamHandler()
#     ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
#     logger.addHandler(ch)


#     client = MustangClient()
#     df = client.measurements_request(**query)
#     breakpoint()
#     fig = plt.figure()
#     gs = fig.add_gridspec(nrows=len(query['metric']))
#     ax0 = fig.add_subplot(gs[0])
#     axes = [ax0]
#     axes += [fig.add_subplot(gs[_e], sharex=ax0) for _e in range(1,len(query['metric']))]
#     for _e, _m in enumerate(query['metric']):
#         _df = df[_m]
#         axes[_e].plot(_df.index, _df.values,'.-', alpha=0.5, label=_m)
#         axes[_e].legend()
#         axes[_e].set_ylabel(_m)
#     plt.show()

