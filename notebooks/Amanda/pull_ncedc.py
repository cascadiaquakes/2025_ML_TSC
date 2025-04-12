import obspy
import boto3
from datetime import datetime
from botocore import UNSIGNED
from botocore.config import Config
import pandas as pd
import numpy as np
from obspy.clients.fdsn import Client

# Pull NCEDC data from S3
s3=boto3.resource('s3',config=Config(signature_version=UNSIGNED))

# Set up NCEDC S3 bucket
BUCKET_NAME = 'ncedc-pds'

# Load station data
stas=pd.read_csv("../data/station2.txt", 
                delim_whitespace=True, 
                header=None, 
                usecols=[0, 1, 2], 
                names=["name", "lat", "lon"])

# Set client
client = Client("IRIS")

# Set dates
starttime = obspy.UTCDateTime("2022-12-20")
endtime = obspy.UTCDateTime("2022-12-27")

#metadata=pd.read_csv("../data/station2.meta.txt",
#                     delimiter='|')

date = datetime(2022, 12, 20)  # You can use datetime.today() if desired
year = date.strftime("%Y")
jday = date.strftime("%j")  # Julian day as 3-digit number
for station in stas['name']:
    #df=metadata[metadata['sta']==station]
    try:
        inventory = client.get_stations(network="*", 
                        station=station,
                        starttime=starttime,
                        endtime=endtime,
                        level="channel")
    except:
        print('No data for station: '+station)
    else:
        # print(inventory)
        for network in inventory:
            for station in network:
                for channel in station:
                    if channel.code[:2] == 'EH' or channel.code[:2] == 'HH' or channel.code[:2] == 'H':
                        net = network.code
                        sta = station.code
                        cha = channel.code
                        loc = channel.location_code or "00"  # Use "00" if location code is blank
                        fname = f"{sta}.{net}.{cha}.{loc}.D.{year}.{jday}"
                        print(fname)
                        KEY='continuous_waveforms/'+net+'/2022/2022.'+jday+'/'+fname
                        s3.Bucket(BUCKET_NAME).download_file(KEY,fname)