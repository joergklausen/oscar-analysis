
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
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.lines as mlines
from urllib.request import urlopen
from bs4 import BeautifulSoup
from functools import reduce
from collections import OrderedDict
from datetime import date
from datetime import datetime


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


# define function: save basic information to json file

def save_basic_info_to_json(country):

    """create json file with information on WIGOS ID, Name, latitude, longitude, elevation, facility Type, observed Properties,
       date Established, date Closed & reportingStatus of all stations within selected country

        Parameters:
        country (str): country code - e.g. "KEN" for Kenya
    """

    # create empty json file to add station data from xml files to
    j_data = '{"stations":[]}'
    file = open("stations.json", "w")
    file.write(j_data)
    file.close()

    # get list of WIGOS identifiers of country of interest
    wigosIds = get_WIGOS_ID_country(country)

    # name spaces
    ns = {
        "gml": "http://www.opengis.net/gml/3.2",
        "xlink": "http://www.w3.org/1999/xlink",
        "wmdr": "http://def.wmo.int/wmdr/2017",
        "gco": "http://www.isotc211.org/2005/gco",
        "gmd": "http://www.isotc211.org/2005/gmd",
        "ns6": "http://def.wmo.int/opm/2013",
        "ns7": "http://def.wmo.int/metce/2013",
        "om": "http://www.opengis.net/om/2.0",
        "ns9": "http://www.isotc211.org/2005/gts",
        "sam": "http://www.opengis.net/sampling/2.0",
        "sams": "http://www.opengis.net/samplingSpatial/2.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"
    }

    # Get station xml Files via jOAI and save relevant information in json file
    for id in wigosIds:

        ## set wmdr xml file location
        record_file = os.getcwd()+"/Files/file.xml"
        # open xml
        url = "https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier=%20" + id
        response = requests.get(url)
        soup= BeautifulSoup(response.content,"xml")
        with open(record_file, 'w') as f:
            f.write(soup.prettify())

        tree = ET.parse(record_file)
        root = tree.getroot()


        # get information from OAI
        metadata = root.find('.//wmdr:WIGOSMetadataRecord',ns) #check if xml file is available on jOAI
        if metadata:
            # Name
            name = root.find(".//wmdr:facility/wmdr:ObservingFacility/gml:name", ns).text
            name = name.strip()

            # Location
            location = root.find(".//wmdr:facility/wmdr:ObservingFacility/wmdr:geospatialLocation/wmdr:GeospatialLocation/wmdr:geoLocation/gml:Point/gml:pos", ns).text
            split_values = location.split()
            numbers = [float(value) for value in split_values]
            lat = numbers[0]
            lon = numbers[1]
            if len(numbers) == 3:
                ele = numbers[2]
            else:
                ele = "unknown"

            # facility type
            facilityType = root.find(".//wmdr:facility/wmdr:ObservingFacility/wmdr:facilityType", ns).attrib["{http://www.w3.org/1999/xlink}href"]
            facilityType = facilityType.split('/')[-1]

            # observed Variables
            variables = list()
            capabilities = root.findall(".//wmdr:ObservingCapability", ns)
            for capability in capabilities:
                observations = capability.findall(".//wmdr:observation", ns)
                for observation in observations:
                    # find observed property
                    observedProperty = observation.find(".//om:OM_Observation/om:observedProperty", ns).attrib["{http://www.w3.org/1999/xlink}href"]
                    # get notation of observed property
                    variables.append(int(observedProperty.split('/')[-1]))

            # Date established
            dateEstablished = root.find(".//wmdr:facility/wmdr:ObservingFacility/wmdr:dateEstablished", ns).text
            if dateEstablished:
                 dateEstablished = dateEstablished.strip()
            else:
                dateEstablished = np.nan

            # Date closed
            dateClosed = root.findall(".//wmdr:facility/wmdr:ObservingFacility/wmdr:dateClosed", ns)
            if dateClosed:
                dateClosed = dateClosed[0].text.strip()
            else:
                dateClosed = np.nan

            # ReportingStatus
            reportingStatus = root.findall(".//wmdr:facility/wmdr:ObservingFacility/wmdr:programAffiliation/wmdr:ProgramAffiliation/wmdr:reportingStatus/wmdr:ReportingStatus/wmdr:reportingStatus", ns)
            if reportingStatus:
                reportingStatus = reportingStatus[0].attrib["{http://www.w3.org/1999/xlink}href"]
                reportingStatus = reportingStatus.split('/')[-1]
            else:
                reportingStatus = "unknown"

            # save information to json File
            aDict = {"wigosId" : id, "name":name, "lat":lat, "lon":lon, "ele":ele, "facilityType":facilityType, "observedProperties" : variables, "dateEstablished" : dateEstablished, "dateClosed" : dateClosed, "reportingStatus" : reportingStatus}
            # print(aDict)
            write_json(aDict)


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


# define function: find necessary information and create data frame

def get_deployments_station(WIGOS_ID):

    """ create data frame with the required information (station, establishment date and deployment dates) of a specific station

        Parameters:
        WIGOS_ID (str): WIGOS identifier of the station of interest

        Returns:
        df_station (data frame): data frame with the required information (start and end dates of deployments, establishment date, etc.)
    """

    ## set wmdr xml file location
    record_file = os.getcwd()+"/Files/file.xml"
    url = "https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier=%20" + WIGOS_ID

    response = requests.get(url)
    soup= BeautifulSoup(response.content,"xml")

    with open(record_file, 'w') as f:
        f.write(soup.prettify())

    tree = ET.parse(record_file)
    root = tree.getroot()

    # namespaces
    ns = {
        "gml": "http://www.opengis.net/gml/3.2",
        "xlink": "http://www.w3.org/1999/xlink",
        "wmdr": "http://def.wmo.int/wmdr/2017",
        "gco": "http://www.isotc211.org/2005/gco",
        "gmd": "http://www.isotc211.org/2005/gmd",
        "ns6": "http://def.wmo.int/opm/2013",
        "ns7": "http://def.wmo.int/metce/2013",
        "om": "http://www.opengis.net/om/2.0",
        "ns9": "http://www.isotc211.org/2005/gts",
        "sam": "http://www.opengis.net/sampling/2.0",
        "sams": "http://www.opengis.net/samplingSpatial/2.0",
        "xsi": "http://www.w3.org/2001/XMLSchema-instance"
    }

    # date of establishment
    dateEstablished = root.find(".//wmdr:facility/wmdr:ObservingFacility/wmdr:dateEstablished", ns).text
    if dateEstablished:
        dateEstablished = datetime.strptime(dateEstablished.strip(), '%Y-%m-%dZ')
    else:
        dateEstablished = "unknown"

    # find observing capabilities in xml file
    results = list()
    capabilities = root.findall(".//wmdr:ObservingCapability", ns)
    for capability in capabilities:
        observations = capability.findall(".//wmdr:observation", ns)
        for observation in observations:
            # find observed property
            observedProperty = observation.find(".//om:OM_Observation/om:observedProperty", ns).attrib["{http://www.w3.org/1999/xlink}href"]
            # get notation of observed property
            observedProperty_notation = int(observedProperty.split('/')[-1])


            beginPosition_element = observation.find(".//om:OM_Observation/om:procedure/wmdr:Process/wmdr:deployment/wmdr:Deployment/wmdr:validPeriod/gml:TimePeriod/gml:beginPosition", ns)
            if beginPosition_element is not None:
                try:
                    beginPosition_text = beginPosition_element.text
                    # Convert to Pandas datetime
                    beginPosition = pd.to_datetime(beginPosition_text.strip(), format='%Y-%m-%dT%H:%M:%SZ')
                except Exception as e:
                    # print("Error converting beginPosition:", e)
                    beginPosition = np.nan
            else:
                beginPosition = np.nan

            # find potential ending of deployment
            endPosition_element = observation.find(".//om:OM_Observation/om:procedure/wmdr:Process/wmdr:deployment/wmdr:Deployment/wmdr:validPeriod/gml:TimePeriod/gml:endPosition", ns)
            if endPosition_element is not None:
                try:
                    endPosition_text = endPosition_element.text
                    endPosition = pd.to_datetime(endPosition_text.strip(), format='%Y-%m-%dT%H:%M:%SZ')
                except Exception as e:
                    endPosition = pd.Timestamp.today().strftime("%Y-%m-%d")
            else: # if no ending: today
                endPosition = pd.Timestamp.today().strftime("%Y-%m-%d")

            results.append({
                "variable": observedProperty_notation,
                "beginPosition": beginPosition,
                "endPosition": endPosition
            })

    # create data frame
    df_station = pd.DataFrame(results)

    # get names of variables through dictionary
    with open(os.getcwd()+'/WMDR_dictionaries/T_GO_VARIABLE_REF_dictionary.json') as f:
        dictionary = json.loads(f.read())
        variables = df_station["variable"]
        df_station["variables_names"] = [(list(dictionary.keys())[list(dictionary.values()).index(str(vari))]) for vari in variables]

    df_station["station"] = WIGOS_ID
    df_station["dateEstablished"] = dateEstablished

    variables_u = df_station["variable"].unique().tolist()


    return df_station, variables_u


# define function: find necessary information and create data frame

def get_information_date_verification(country):

    """ create data frame with the required information (station, establishment date and start of first deployment) from the underlying xml files

        Parameters:
        country (str): country code - e.g. KEN for Kenya

        Returns:
        df_dates (data frame): data frame with the required information (station, establishment date and start of first deployment)
    """

    # prepare data frame
    df_dates = pd.DataFrame(np.nan, index=[0],columns=["station", "dateEstablished", "firstDeploymentStart"])

    # get WIGOS IDs
    wigosIds = get_WIGOS_ID_country(country)

    # go through each station xml and append the information to the data frame
    for id in wigosIds:

        # set wmdr xml file location
        record_file = os.getcwd()+"/Files/file.xml"
        url = "https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier=%20" + id

        response = requests.get(url)
        soup= BeautifulSoup(response.content,"xml")

        with open(record_file, 'w') as f:
            f.write(soup.prettify())

        tree = ET.parse(record_file)
        root = tree.getroot()

        # namespaces
        ns = {
            "gml": "http://www.opengis.net/gml/3.2",
            "xlink": "http://www.w3.org/1999/xlink",
            "wmdr": "http://def.wmo.int/wmdr/2017",
            "gco": "http://www.isotc211.org/2005/gco",
            "gmd": "http://www.isotc211.org/2005/gmd",
            "ns6": "http://def.wmo.int/opm/2013",
            "ns7": "http://def.wmo.int/metce/2013",
            "om": "http://www.opengis.net/om/2.0",
            "ns9": "http://www.isotc211.org/2005/gts",
            "sam": "http://www.opengis.net/sampling/2.0",
            "sams": "http://www.opengis.net/samplingSpatial/2.0",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }

        # date of establishment
        dateEstablished = root.find(".//wmdr:facility/wmdr:ObservingFacility/wmdr:dateEstablished", ns).text
        if dateEstablished:
            dateEstablished = datetime.strptime(dateEstablished.strip(), '%Y-%m-%dZ')
        else:
            dateEstablished = "unknown"

        # find observing capabilities in xml file
        results = list()
        capabilities = root.findall(".//wmdr:ObservingCapability", ns)
        for capability in capabilities:
            observations = capability.findall(".//wmdr:observation", ns)
            for observation in observations:
                # find observed property
                observedProperty = observation.find(".//om:OM_Observation/om:observedProperty", ns).attrib["{http://www.w3.org/1999/xlink}href"]
                # get notation of observed property
                observedProperty_notation = int(observedProperty.split('/')[-1])


                beginPosition_element = observation.find(".//om:OM_Observation/om:procedure/wmdr:Process/wmdr:deployment/wmdr:Deployment/wmdr:validPeriod/gml:TimePeriod/gml:beginPosition", ns)
                if beginPosition_element is not None:
                    try:
                        beginPosition_text = beginPosition_element.text
                        # Convert to Pandas datetime
                        beginPosition = pd.to_datetime(beginPosition_text.strip(), format='%Y-%m-%dT%H:%M:%SZ')
                    except Exception as e:
                        beginPosition = np.nan
                else:
                    beginPosition = np.nan

                results.append({
                    "variable": observedProperty_notation,
                    "beginPosition": beginPosition,
                })

        # create data frame
        df_station = pd.DataFrame(results)
        # find first date
        pos = pd.to_datetime(df_station["beginPosition"], format='%Y-%m-%d')
        firstDeploymentStart = pd.Series(pos).min()

        # write data in data frame
        new_row = {"station":id,"dateEstablished":dateEstablished,"firstDeploymentStart":firstDeploymentStart}
        df_dates.loc[len(df_dates)] = new_row

    df_dates.drop([0], axis=0, inplace=True)

    return df_dates

# define function: find necessary information and create data frame

def get_deployments_variable_country(country, variable):

    """ find all deployments of a variable of interest in a country

        Parameters:
        country (str): country of interest, e.g. "KEN"
        variable (int): notation of variable according to WMDR (e.g. 224 for Air temperature)

        Returns:
        df_variable: data frame including all deployments of all stations measuring the variable in the country
    """

    # prepare data frame
    df_variable = pd.DataFrame()

    # get WIGOS IDs
    wigosIds = get_WIGOS_ID_country(country)

    for id in wigosIds:

        # prepare data frame
        df_station = pd.DataFrame(np.nan, index=[0],columns=["station", "beginPosition", "endPosition", "variable"])

        # set wmdr xml file location
        record_file = os.getcwd()+"/Files/file.xml"
        url = "https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier=%20" + id

        response = requests.get(url)
        soup= BeautifulSoup(response.content,"xml")

        with open(record_file, 'w') as f:
            f.write(soup.prettify())

        tree = ET.parse(record_file)
        root = tree.getroot()

        # namespaces
        ns = {
            "gml": "http://www.opengis.net/gml/3.2",
            "xlink": "http://www.w3.org/1999/xlink",
            "wmdr": "http://def.wmo.int/wmdr/2017",
            "gco": "http://www.isotc211.org/2005/gco",
            "gmd": "http://www.isotc211.org/2005/gmd",
            "ns6": "http://def.wmo.int/opm/2013",
            "ns7": "http://def.wmo.int/metce/2013",
            "om": "http://www.opengis.net/om/2.0",
            "ns9": "http://www.isotc211.org/2005/gts",
            "sam": "http://www.opengis.net/sampling/2.0",
            "sams": "http://www.opengis.net/samplingSpatial/2.0",
            "xsi": "http://www.w3.org/2001/XMLSchema-instance"
        }

        results = list()

        # find observing capabilities in xml file
        capabilities = root.findall(".//wmdr:ObservingCapability", ns)
        for capability in capabilities:
            observations = capability.findall(".//wmdr:observation", ns)
            for observation in observations:
                # find observed property
                observedProperty = observation.find(".//om:OM_Observation/om:observedProperty", ns).attrib["{http://www.w3.org/1999/xlink}href"]
                # get notation of observed property
                observedProperty_notation = int(observedProperty.split('/')[-1])


                beginPosition_element = observation.find(".//om:OM_Observation/om:procedure/wmdr:Process/wmdr:deployment/wmdr:Deployment/wmdr:validPeriod/gml:TimePeriod/gml:beginPosition", ns)
                if beginPosition_element is not None:
                    try:
                        beginPosition_text = beginPosition_element.text
                        # Convert to Pandas datetime
                        beginPosition = pd.to_datetime(beginPosition_text.strip(), format='%Y-%m-%dT%H:%M:%SZ')
                    except Exception as e:
                        # print("Error converting beginPosition:", e)
                        beginPosition = np.nan
                else:
                    beginPosition = np.nan

                # find potential ending of deployment
                endPosition_element = observation.find(".//om:OM_Observation/om:procedure/wmdr:Process/wmdr:deployment/wmdr:Deployment/wmdr:validPeriod/gml:TimePeriod/gml:endPosition", ns)
                if endPosition_element is not None:
                    try:
                        endPosition_text = endPosition_element.text
                        endPosition = pd.to_datetime(endPosition_text.strip(), format='%Y-%m-%dT%H:%M:%SZ')
                    except Exception as e:
                        endPosition = pd.Timestamp.today().strftime("%Y-%m-%d")
                else: # if no ending: today
                    endPosition = pd.Timestamp.today().strftime("%Y-%m-%d")

                results.append({
                    "station": id,
                    "beginPosition": beginPosition,
                    "endPosition": endPosition,
                    "variable": observedProperty_notation
                })

        # create data frame
        df_station = pd.DataFrame(results)
        subset_df = df_station.loc[df_station["variable"] == variable]
        df_variable = pd.concat([df_variable, subset_df], ignore_index=True)

        # get name of variable
        with open(os.getcwd()+"/WMDR_dictionaries/T_GO_VARIABLE_REF_dictionary.json") as f:
            dictionary = json.loads(f.read())
        variables = df_variable["variable"]
        df_variable["variables_names"] = [(list(dictionary.keys())[list(dictionary.values()).index(str(vari))]) for vari in variables]

    return df_variable, wigosIds
