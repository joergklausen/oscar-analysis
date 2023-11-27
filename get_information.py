
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

    # Get station xml Files via jOAI and save relevant information in json file
    for id in wigosIds:

        # get url
        url = "https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier=%20" + id

        # get xml from url
        document = requests.get(url)
        soup= BeautifulSoup(document.content,"xml")

        # get information from OAI
        metadata = soup.find('metadata') #check if xml file is available on jOAI
        if metadata:

            # Name
            name = soup.find("name")
            name = name.get_text()

            # Location
            location = soup.find_all('pos')
            location = re.findall(r'.*?\>(.*)\<.*',str(location))[0]
            loc = re.findall(r'-?[0-9]*\.?[0-9]*', location)
            lat = loc[0]
            lon = loc[2]
            if len((loc)) == 6: # check if elevation is given
                ele = loc[4]
            else:
                ele = "unknown"

            # facility type
            facilityType = soup.find('facilityType')
            facilityType = re.findall(r'http://codes.wmo.int/wmdr/FacilityType/(.*)\"\s.*',str(facilityType))[0]

            # observed Variables
            observedProperties = soup.find_all('observedProperty')
            observedProperties_notation = re.findall(r'\d+',str(observedProperties))

            # Date established
            dateEstablished = soup.find_all('dateEstablished')
            if dateEstablished:
                dateEstablished = re.findall(r'\d{4}-\d{2}-\d{2}',str(dateEstablished))[0]
            else:
                dateEstablished = "unknown"

            # Date closed
            dateClosed = soup.find_all('dateClosed')
            if dateClosed:
                dateClosed = re.findall(r'\d{4}-\d{2}-\d{2}',str(dateClosed))[0]
            else:
                dateClosed = "NA"

            # ReportingStatus
            reportingStatus = soup.find('reportingStatus')
            if reportingStatus:
                reportingStatus = soup.find_all('reportingStatus')
                reportingStatus = re.findall(r'http://codes.wmo.int/wmdr/ReportingStatus/(.*)\"\s.*',str(reportingStatus))[0]
            else:
                reportingStatus = "unknown"

            # save information to json File
            aDict = {"wigosId" : id, "name":name, "lat":lat, "lon":lon, "ele":ele, "facilityType":facilityType, "observedProperties" : observedProperties_notation, "dateEstablished" : dateEstablished, "dateClosed" : dateClosed, "reportingStatus" : reportingStatus}
            # print(aDict)
            write_json(aDict)

# define function: get xml files

def get_xml_info(WIGOS_ID):

    """get xml information through jOAI and save file

        Parameters:
        WIGOS_ID (str): WIGOS identifier of the station of interest
    """
    id = WIGOS_ID
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

# define function: find necessary information and create data frame

def get_deployments_station(WIGOS_ID):

    """ create data frame with the required information (station, establishment date and deployment dates) of a specific station

        Parameters:
        WIGOS_ID (str): WIGOS identifier of the station of interest

        Returns:
        df_station (data frame): data frame with the required information (start and end dates of deployments, establishment date, etc.)
    """

    id = WIGOS_ID
    # print(id)

    # get xml for the station
    get_xml_info(id)

    # get variables at a station
    url = "https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier=%20" + str(id)
    url = url.replace(" ", "%20")
    xml = urlopen(url).read()
    soup = BeautifulSoup(xml, 'xml')

    # Establishment date of station
    dateEstablished = soup.find_all('dateEstablished')
    if dateEstablished:
        dateEstablished = re.findall(r'\d{4}-\d{2}-\d{2}',str(dateEstablished))[0]
    else:
        dateEstablished = "unknown"

    # find observed properties
    observedProperties = []
    with open(os.getcwd()+'/Files/File_'+id+'.txt') as myFile:
        observedProperties_line = soup.find_all('observedProperty')
        observedProperties_notation = re.findall(r'\d+',str(observedProperties_line))
        observedProperties.append(observedProperties_notation)

    # list of unique observed properties
    def unique(list1):
        ans = reduce(lambda re, x: re+[x] if x not in re else re, list1, [])
        return(ans)
    variables_u = unique(observedProperties[0])

    # open file
    f=open(os.getcwd()+'/Files/File_'+id+'.txt')
    lines=f.readlines()
    all_dates = []

    # prepare data frame
    df_station = pd.DataFrame(np.nan, index=[0],columns=["beginPosition", "endPosition", "station", "dateEstablished", "variable"])

    # go through every observed variable
    for var in variables_u:

        # find line numbers containing the WMDR notation of the observed property
        numbers = []

        with open(os.getcwd()+'/Files/File_'+id+'.txt') as myFile:
            for num, line in enumerate(myFile, 1):
                if var in line:
                    numbers.append(num)

        # find the line numbers with <om:observedProperty
        obs = "observedProperty"
        numbers_obs = []

        for n in numbers:
            if obs in lines[n-1]:
                number = re.findall(r'\d+',lines[n-1])
                if number[0]==str(var):
                    numbers_obs.append(n)

        # read 50 lines before "observedProperty" line to get "beginPosition" (& "endPosition")
        for n in numbers_obs:
            start = "beginPosition"
            end = "endPosition"
            line_numbers = range(n-50,n)

            f=open(os.getcwd()+'/Files/File_'+id+'.txt')
            lines=f.readlines()
            positions = []

            for n in line_numbers:
                if start in lines[n]:
                    beginning = re.findall(r'\d{4}-\d{2}-\d{2}',lines[n])
                    if beginning:
                        pd.to_datetime(beginning, format='%Y-%m-%d')
                        positions.append(beginning[0])
                    else:
                        positions.append(np.nan)

                elif end in lines[n]:
                    ending = re.findall(r'\d{4}-\d{2}-\d{2}',lines[n])
                    if ending:
                        pd.to_datetime(ending, format='%Y-%m-%d')
                        positions.append(ending[0])
                    else: # if no ending: today
                        positions.append(pd.Timestamp.today().strftime("%Y-%m-%d"))

            beginPosition  = positions[0]
            endPosition = positions[1]
            # fill new row to data frame
            new_row = {"beginPosition":beginPosition,"endPosition":endPosition,"station":id, "dateEstablished":dateEstablished, "variable":var}
            df_station.loc[len(df_station)] = new_row

    # delete row zero from data frame
    df_station.drop([0], axis=0, inplace=True)

    # get names of variables through dictionary
    with open(os.getcwd()+'/WMDR_dictionaries/'+'T_GO_VARIABLE_REF_dictionary.json') as f:
        dictionary = json.loads(f.read())
    variables = df_station["variable"]
    df_station["variables_names"] = [(list(dictionary.keys())[list(dictionary.values()).index(str(vari))]) for vari in variables]

    # print data frame
    # print(df_station)
    return df_station, variables_u





# define function: find necessary information and create data frame

def get_information_date_verification(country):

    """ create data frame with the required information (station, establishment date and start of first deployment) from the underlying xml files

    Parameters:
        country (str): country code - e.g. KEN for Kenya

    Returns:
        df_dates (data frame): ata frame with the required information (station, establishment date and start of first deployment)
    """

    # prepare data frame
    df_dates = pd.DataFrame(np.nan, index=[0],columns=["station", "dateEstablished", "firstDeploymentStart"])

    # get WIGOS IDs
    wigosIds = get_WIGOS_ID_country(country)

    # go through each station xml and append the information to the data frame
    for id in wigosIds:
        # print(id)
        get_xml_info(id)

        # open xml
        observedProperties = []
        url = "https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier=%20" + str(id)
        xml = urlopen(url).read()
        soup = BeautifulSoup(xml, 'xml')


        # find establishment date of station
        dateEstablished = soup.find_all('dateEstablished')
        if dateEstablished:
            dateEstablished = re.findall(r'\d{4}-\d{2}-\d{2}',str(dateEstablished))[0]
        else:
            dateEstablished = "unknown"

        # find observed properties
        with open(os.getcwd()+"/Files/File_"+id+".txt") as myFile:
            observedProperties_line = soup.find_all('observedProperty')
            observedProperties_notation = re.findall(r'\d+',str(observedProperties_line))
            observedProperties.append(observedProperties_notation)

        #  list of unique observed properties
        def unique(list1):
            ans = reduce(lambda re, x: re+[x] if x not in re else re, list1, [])
            return(ans)
        variables_u = unique(observedProperties[0])

        f=open(os.getcwd()+'/Files/File_'+id+'.txt')
        lines=f.readlines()

        # find deployment start for every measured variable
        positions = []
        for var in variables_u:
            variable = var

            # find line numbers containing the WMDR notation of the observed property
            numbers = []

            with open(os.getcwd()+'/Files/File_'+id+'.txt') as myFile:
                for num, line in enumerate(myFile, 1):
                    if variable in line:
                        numbers.append(num)

            # find the line numbers with <om:observedProperty
            obs = "observedProperty"
            numbers_obs = []

            for n in numbers:
                if obs in lines[n-1]:
                    number = re.findall(r'\d+',lines[n-1])
                    if number[0]==str(var):
                        numbers_obs.append(n)

            # read 30 lines before "observedProperty" line to get "beginPosition"
            for n in numbers_obs:
                start = "beginPosition"
                line_numbers = range(n-30,n)
                for n in line_numbers:
                    if start in lines[n]:
                        beginning = re.findall(r'\d{4}-\d{2}-\d{2}',lines[n])
                        if beginning:
                            pd.to_datetime(beginning, format='%Y-%m-%d')
                            positions.append(beginning[0])
                        else:
                            positions.append(np.nan)

        # find first date
        pos = pd.to_datetime(positions, format='%Y-%m-%d')
        firstDeploymentStart = pd.Series(pos).min()

        # write data in data frame
        new_row = {"station":id,"dateEstablished":dateEstablished,"firstDeploymentStart":firstDeploymentStart}
        df_dates.loc[len(df_dates)] = new_row

    df_dates.drop([0], axis=0, inplace=True)

    return df_dates


def get_deployments_variable_country(country, variable):

    """ find all deployments of a variable of interest in a country

        Parameters:
        country (str): country of interest, e.g. "KEN"
        variable (str): notation of variable according to WMDR (e.g. 224 for Air temperature)

        Returns:
        df_variable: data frame including all deployments of all stations measuring the variable in the country
    """

    # prepare data frame
    df_variable = pd.DataFrame(np.nan, index=[0],columns=["beginPosition", "endPosition", "station", "variable"])

    # get WIGOS IDs
    wigosIds = get_WIGOS_ID_country(country)

    for id in wigosIds:
        # print(id)

        # open xml
        observedProperties = []
        url = "https://oscar.wmo.int/oai/provider?verb=GetRecord&metadataPrefix=wmdr&identifier=%20" + id
        xml = urlopen(url).read()
        soup = BeautifulSoup(xml, 'xml')

        # find observed properties
        with open(os.getcwd()+"/Files/File_"+id+".txt") as myFile:
            observedProperties_line = soup.find_all('observedProperty')
            observedProperties_notation = re.findall(r'\d+',str(observedProperties_line))
            observedProperties.append(observedProperties_notation)

        # check if variable of interest is measured at the station
        if str(variable) in observedProperties[0]:
            station = id
            # find line numbers containing the WMDR number of the observed property
            numbers = []

            with open('/home/sdanioth/Documents/git/OSCAR_analysis/Files/File_'+id+'.txt') as myFile:
                for num, line in enumerate(myFile, 1):
                    if variable in line:
                        numbers.append(num)

            # find the line numbers with <om:observedProperty
            obs = "observedProperty"
            numbers_obs = []
            # get line numbers containing variable
            f=open(os.getcwd()+"/Files/File_"+id+".txt")
            lines=f.readlines()
            for n in numbers:
                if obs in lines[n-1]:
                    number = re.findall(r'\d+',lines[n-1])
                    if number[0]==str(variable):
                        numbers_obs.append(n)

            # read 20 lines before "observedProperty" line to get "beginPosition" (& "endPosition")
            for n in numbers_obs:
                start = "beginPosition"
                end = "endPosition"
                line_numbers = range(n-50,n)

                f=open('/home/sdanioth/Documents/git/OSCAR_analysis/Files/File_'+id+'.txt')
                lines=f.readlines()
                positions = []

                for n in line_numbers:
                    if start in lines[n]:
                        beginning = re.findall(r'\d{4}-\d{2}-\d{2}',lines[n])
                        if beginning:
                            pd.to_datetime(beginning, format='%Y-%m-%d')
                            positions.append(beginning[0])
                        else:
                            positions.append(np.nan)

                    elif end in lines[n]:
                        ending = re.findall(r'\d{4}-\d{2}-\d{2}',lines[n])
                        if ending:
                            pd.to_datetime(ending, format='%Y-%m-%d')
                            positions.append(ending[0])
                        else:
                            positions.append(pd.Timestamp.today().strftime("%Y-%m-%d"))

                beginPosition  = positions[0]
                endPosition = positions[1]
                # write information to data frame
                new_row = {"beginPosition":beginPosition,"endPosition":endPosition,"station":station,"variable":variable}
                df_variable.loc[len(df_variable)] = new_row

        # if variable not measured at station
        else:
            station = id
            new_row = {"beginPosition":np.nan,"endPosition":np.nan,"station":station,"variable":variable}
            df_variable.loc[len(df_variable)] = new_row


    df_variable.drop([0], axis=0, inplace=True)


    # get name of variable
    with open(os.getcwd()+'/WMDR_dictionaries/'+'T_GO_VARIABLE_REF_dictionary.json') as f:
        dictionary = json.loads(f.read())
    variables = df_variable["variable"]
    df_variable["variables_names"] = [(list(dictionary.keys())[list(dictionary.values()).index(str(vari))]) for vari in variables]


    return df_variable, wigosIds
