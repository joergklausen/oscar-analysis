
# import

import xml.etree.ElementTree as ET
import urllib.request
import csv
import requests
from urllib.request import urlopen
import json
import re
import os
import pandas as pd
import datetime as dt
# %matplotlib inline
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.lines as mlines
from urllib.request import urlopen
from bs4 import BeautifulSoup
from functools import reduce
from collections import OrderedDict
from datetime import date

# define function: get all WIGOS identifier

def get_WIGOS_ID_country(country):

    """ use the OSCAR API to find all stations registered within one country

    Parameters:
        country (str): country code - e.g. KEN for Kenya

    Returns:
        wigosIds (list): list of all WIGOS IDs of registered stations in selected country
    """

    # open API
    all_stations_KEN_url = "https://oscar.wmo.int/surface/rest/api/search/station?territoryName=" + country
    response = urlopen(all_stations_KEN_url)
    data_json = json.loads(response.read())

    # find WIGOS IDs and save in list
    wigosIds = []
    for station in data_json["stationSearchResults"]:
        wigosId = str(station["wigosId"])
        wigosIds.append(wigosId)

    return wigosIds


# define function: get xml files

def get_xml_info(WIGOS_ID):

    """get xml information through jOAI and save file

        Parameters:
        WIGOS_ID (str): WIGOS identifier of the station of interest
    """

    # open xml file through jOAI
    url = "https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier=%20" + str(id)
    xml = urlopen(url).read()
    soup = BeautifulSoup(xml, 'xml')
    content = soup('OAI-PMH')

    # save file
    with open(os.getcwd()+"/Files/File_"+id+".txt", 'w') as f:
        f.write(str(content))


# define function: append information to json file

def write_json(new_data, filename='stations.json'):

    """ create a json file and add information on stations to it

    Parameters:
        new_data (dictionary): dictionary including {"wigosId" : id, "name":name, "lat":lat,
        "lon":lon, "ele":ele, "facilityType":facilityType, "observedProperties" : observedProperties_notation,
        "dateEstablished" : dateEstablished, "dateClosed" : dateClosed, "reportingStatus" : reportingStatus}
        filename (str): name of json file

    """

    with open(filename,'r+') as file:
        # First we load existing data into a dict.
        file_data = json.load(file)
        # Join new_data with file_data inside emp_details
        file_data["stations"].append(new_data)
        # Sets file's current position at offset.
        file.seek(0)
        # convert back to json.
        json.dump(file_data, file, indent = 4)
