#!/bin/bash
# auth: Nathan T Stevens
# email: ntsteven@uw.edu    
# org: Pacific Northwest Seismic Network
# license: GPLv3
# purpose: sets up a python venv for qc notebooks in this directory

python3 -m venv qc_env
source qc_env/bin/activate
python3 -m pip install --upgrade pip
pip install obspy
pip install matplotlib
pip install pyrocko[gui]
pip install obsplus
pip install ipykernel
pip install jupyter