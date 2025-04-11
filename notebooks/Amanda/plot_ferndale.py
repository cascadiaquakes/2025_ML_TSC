#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug 10 08:45:15 2022

Plot the Ferndale earthquake

@author: amt
"""

import pygmt
import pandas as pd
%matplotlib notebook

# Load station data
df = pd.read_csv("../data/station2.txt", delim_whitespace=True, header=None, usecols=[0, 1, 2], names=["name", "lat", "lon"])

# Ferndale earthquake info (USGS event ID: nc73798970)
eq_lat = 40.31
eq_lon = -124.57
eq_depth = 17  # km
eq_mag = 6.4

# Double-couple focal mechanism (strike, dip, rake)
# Approximate for this event (strike-slip): 150, 90, 0
focal_mech  = {"strike": 252, "dip": 89, "rake": 7, "magnitude": 6.4}

# Initialize map
fig = pygmt.Figure()

# Region around northern CA (adjust as needed)
region = [-124.75, -122.75, 39.25, 41.25]

# Base map
fig.basemap(region=region, 
            projection="M10i", 
            frame=["a", "+t2022 Ferndale Earthquake"]
            )
fig.coast(shorelines="1/0.5p,black", 
          water="lightblue", 
          land="gray95", 
          borders="a", 
          resolution="f")

# Plot stations
fig.plot(x=df["lon"], 
         y=df["lat"], 
         style="t0.5c", 
         fill="blue", 
         pen="black", 
         label="Stations")

# Add station names
for _, row in df.iterrows():
    fig.text(x=row["lon"], 
             y=row["lat"], 
             text=row["name"], 
             font="14p,Helvetica,black", 
             offset="0.3c/0.6c")

# Plot earthquake location
fig.plot(x=[eq_lon], 
         y=[eq_lat], 
         style="a1.0c", 
         fill="red", 
         pen="black", 
         label="Event")

# Plot focal mechanism
fig.meca(spec=focal_mech, 
         scale="2c", 
         longitude=eq_lon, 
         latitude=eq_lat, 
         depth=0, 
         plot_longitude=eq_lon+0.1, 
         plot_latitude=eq_lat-0.20,
         offset="+p1p,darkorange+s0.25c",
         compressionfill="lightorange")

# Plot Faults
fig.plot(data="../data/gem_active_faults.gmt", pen="1p,darkred", label="Faults")

# Add legend
pygmt.config(FONT_ANNOT_PRIMARY="30p,Helvetica,black")
fig.legend(position="JTR+o-4c", box=True)

# Show figure
fig.show()
