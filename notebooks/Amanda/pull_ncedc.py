import obspy
import boto3
from datetime import datetime
from botocore import UNSIGNED
from botocore.config import Config
import pandas as pd
import numpy as np
from obspy.clients.fdsn import Client

S3=False

# Set client
client = Client("NCEDC")

# Set dates
starttime = obspy.UTCDateTime("2022-12-20")
endtime = obspy.UTCDateTime("2022-12-21")
nogo=[]

# Load station data
stas = pd.read_csv("../data/station_file.txt", header=None, names=["Station", "Latitude", "Longitude", "Elevation"])
#stas = stas[stas['Station'].str.endswith('.BK')]

 # Pull NCEDC data from S3
s3=boto3.resource('s3',config=Config(signature_version=UNSIGNED))

 # Set up NCEDC S3 bucket
BUCKET_NAME = 'ncedc-pds'

# Channel priority
channel_priority = ['EH', 'HH', 'BH', 'HN', 'NP']  # Highest to lowest priority

# Set time range
for sta in stas['Station']:
    print("Trying "+sta)
    station=sta[:-3]
    network=sta[-2:]
    try:
        inventory = client.get_stations(network=network, 
                        station=station,
                        starttime=starttime,
                        endtime=endtime,
                        level="channel")
    except:
        print('No XML data for station: '+station)
        nogo.append(station)
    else:
        # print(inventory)
        for network in inventory:
            for station in network:
                # Get available channel types for this station
                channel_types = set(chan.code[:2] for chan in station if chan.code[:2] in channel_priority)

                # Find the highest priority channel type available
                selected_prefix = next((ch for ch in channel_priority if ch in channel_types), None)
                if not selected_prefix:
                    continue  # Skip this station if no desired channel type is available

                for channel in station:
                    if channel.code[:2] != selected_prefix:
                        continue  # Skip channels that aren't the selected type

                    net = network.code
                    sta = station.code
                    cha = channel.code
                    loc = channel.location_code or "00"

                    for day in np.arange(20, 21):
                        date = datetime(2022, 12, day)
                        year = date.strftime("%Y")
                        jday = date.strftime("%j")
                        fname = f"{sta}.{net}.{cha}.{loc}.D.{year}.{jday}"
                        print(fname)

                        if os.path.exists(fname):
                            print(f"{fname} already exists. Skipping.")
                            continue

                        if S3:
                            KEY = f'continuous_waveforms/{net}/2022/2022.{jday}/{fname}'
                            try:
                                s3.Bucket(BUCKET_NAME).download_file(KEY, fname)
                            except:
                                print('No S3 data for ' + fname)
                        else:
                            try:
                                st = client.get_waveforms(
                                    network=net,
                                    station=sta,
                                    location="*",
                                    channel=cha,
                                    starttime=starttime,
                                    endtime=endtime,
                                )
                            except:
                                print('No Client data for ' + net + " " + sta)
                            else:
                                st.merge(method=1, interpolation_samples=0)
                                for tr in st:
                                    if np.ma.isMaskedArray(tr.data):
                                        tr.data = tr.data.filled(fill_value=0)  # or np.nan if you prefer
                                st.write(fname, format='MSEED')