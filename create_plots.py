
# import

import xml.etree.ElementTree as ET
import urllib.request
import csv
import requests
from bs4 import BeautifulSoup
from urllib.request import urlopen
import json
import re
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd
import matplotlib.lines as mlines
from urllib.request import urlopen
from bs4 import BeautifulSoup
import datetime
from functools import reduce
from datetime import date
from collections import OrderedDict


# define function: create plot showing a map with all catalogued stations (color of dots according to reporting status)

def plot_overview_map(json_file, reporting = True):

    """ create a plot showing a spatial map with dots for the catalogued stations (color of dots according to reporting status)

        Parameters:
        json_file (.json file): containing the required information on the stations
        (WIGOS ID, name, lat, lon, elevation, facilityType, observed Properties, dateEstablsihed,
        dateClosed & reportingStatus)
        reporting (boolean): True (default) -> color of dots according to reporting status, False -> all dots the same color
    """

    # Figure size
    fig = plt.figure(figsize=(15, 15))

    # Load map background
    m = Basemap(projection='lcc', resolution='h', lat_0=0.1, lon_0=37.5, width=1.5E6, height=1.2E6)
    m.shadedrelief()
    m.drawmapscale(lon=43, lat=-4.7, lon0=43,lat0=-4, length=200, barstyle="fancy", linecolor="black", fillcolor2="black", fontsize=12, fontcolor="black")
    m.drawcoastlines(color='grey', linewidth=1.5)
    m.drawrivers(color='grey', linewidth=1.5)
    m.drawcountries(color='black', linewidth=2)

    # load data
    f = open(json_file)
    data = json.load(f)
    df = pd.DataFrame(data["stations"])

    # color according to reporting status
    colors = {'operational':'tab:blue', 'preOperational':'tab:purple', 'unknown':'tab:grey', 'closed':'tab:red', 'nonReporting':'tab:orange'}

    # print station dots
    lat = df["lat"]
    lon = df["lon"]
    if reporting == True:
        m.scatter(lon, lat,latlon=True,c=df["reportingStatus"].map(colors),s=60,marker="*")
    else:
        m.scatter(lon, lat,latlon=True,c="blue",s=60,marker="*")

    # legend
    if reporting == True:
        stations = [mlines.Line2D([0], [0], color="w", marker='o',markersize=10,  markerfacecolor=v, label=k) for k, v in colors.items()]
        plt.legend(handles=stations, loc=3, title="Operating Status", title_fontsize="xx-large", labelcolor="black", fontsize="xx-large")

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    dir = os.getcwd()+"/Plots/"+str(date_today)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # save plot

        plt.savefig(dir+"/Map_all_stations_reportingStatus_"+str(date_today)+"_.jpeg", bbox_inches='tight')
    else:
        plt.savefig(dir+"/Map_all_stations_catalogued_"+str(date_today)+"_.jpeg", bbox_inches='tight')


# define function: create plot showing maps (one for every decade) with all catalogued stations established within that decade (color of dots according to reporting status)

def plot_maps_establishment_decade(json_file, reporting = True):

    """ create plot showing maps (one for every decade) with all catalogued stations established within that decade

        Parameters:
        json_file (.json file): containing the required information on the stations
        (WIGOS ID, name, lat, lon, elevation, facilityType, observed Properties, dateEstablsihed,
        dateClosed & reportingStatus)
        reporting (boolean): True -> color of dots according to reporting status, False -> all dots the same color
    """

    # create plot
    plt.style.use('default')
    fig, axes = plt.subplots(2,4, figsize=(16,9.7))
    axes = axes.ravel()

    # load data
    f = open(json_file)
    data = json.load(f)

    # years
    years = [1961, 1961, 1971, 1981, 1991, 2001, 2011, 2021, 2031]

    # loop over decades; for every decade one map showing the stations established within
    for i, decade in enumerate(["before 1961", "1961 - 1970", "1971 - 1980", "1981 - 1990", "1991 - 2000", "2001 - 2010", "2011 - 2020", "since 2021"]):

        # map background
        m = Basemap(projection='lcc', resolution='l', lat_0=0.1, lon_0=37.5, width=1.5E6, height=1.2E6,  ax = axes[i])
        m.drawcoastlines(color='grey', linewidth=0.8)
        m.drawcountries(color='black', linewidth=2)

        # find stations established within decade
        df = pd.DataFrame(data["stations"])
        if i == 0:
            df = df[(pd.to_datetime(df["dateEstablished"]) < pd.to_datetime(datetime.datetime(1961, 1,1)))]
        else:
            df = df[(pd.to_datetime(df["dateEstablished"]) >= pd.to_datetime(datetime.datetime(years[i], 1,1))) & (pd.to_datetime(df["dateEstablished"]) < pd.to_datetime(datetime.datetime(years[i+1], 1,1)))]

        # plot dots for established stations
        if not df.empty:
            lat = df["lat"]
            lon = df["lon"]
            if reporting == True:
                colors = {'operational':'tab:blue', 'preOperational':'tab:purple', 'unknown':'tab:grey', 'closed':'tab:red', 'nonReporting':'tab:orange'}
                m.scatter(lon, lat, latlon=True, c=df["reportingStatus"].map(colors),s=60,marker="*")
            else:
                m.scatter(lon, lat, latlon=True, c="blue",s=30,marker="*")

        # small title over every map
        axes[i].set_title(decade)

    # large title
    plt.suptitle('Establishment of stations', fontsize=20, fontweight="bold")

    # handles, labels = axes.get_legend_handles_labels()
    if reporting == True:
        stations = [mlines.Line2D([0], [0], color="w", marker='*',markersize=20,  markerfacecolor=v, label=k) for k, v in colors.items()]
        fig.legend(handles=stations, loc='lower center', ncol=len(stations), title="Today's reporting status", title_fontproperties={'weight':'bold'})
    plt.tight_layout(pad=1)

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    dir = os.getcwd()+"/Plots/"+str(date_today)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # save plot
    if reporting == True:
        plt.savefig(dir+"/Map_establishment_decade_reporting_"+str(date_today)+"_.jpeg", bbox_inches='tight')
    else:
        plt.savefig(dir+"/Map_all_stations_reportingStatus_"+str(date_today)+"_.jpeg", bbox_inches='tight')


# define function: Barplot over the decades showing the station establishment & today's reporting status

def barplot_establishment_decade(json_file, reporting = True):

    """ Barplot showing the number of stations established within a decade (and how many of them are operational today)

        Parameters:
        json_file (.json file): containing the required information on the stations
        (WIGOS ID, name, lat, lon, elevation, facilityType, observed Properties, dateEstablsihed,
        dateClosed & reportingStatus)
        reporting (boolean): True -> how many stations are operational today, False -> without today's reporting status
    """

    # load data
    f = open(json_file)
    data = json.load(f)

    # prepare
    stations_n = []
    stations_operational = []

    # years
    years = [1961, 1961, 1971, 1981, 1991, 2001, 2011, 2021, 2031]
    decades = ["before 1961", "1961 - 1970", "1971 - 1980", "1981 - 1990", "1991 - 2000", "2001 - 2010", "2011 - 2020", "since 2021"]

    for i, decade in enumerate(decades):

        df = pd.DataFrame(data["stations"])

        if i == 0:
            df = df[(pd.to_datetime(df["dateEstablished"]) < pd.to_datetime(datetime.datetime(years[i], 1,1)))]
            stations_n.append(len(df))
            stations_operational.append(len(df[(df["reportingStatus"]=="operational")]))
        else:
            df = df[(pd.to_datetime(df["dateEstablished"]) >= pd.to_datetime(datetime.datetime(years[i], 1,1))) & (pd.to_datetime(df["dateEstablished"]) < pd.to_datetime(datetime.datetime(years[i+1], 1,1)))]
            stations_n.append(len(df))
            stations_operational.append(len(df[(df["reportingStatus"]=="operational")]))

    plt.style.use('default')
    fig, axes = plt.subplots(1,1, figsize=(8,5))

    n = len(decades)
    r = np.arange(n)
    width = 0.4
    if reporting == True:
        plt.bar(r, stations_n, width=width, label= "total", color="purple")
        plt.bar(r + width, stations_operational, width=width, label="currently operational", color="blue")
    else:
        plt.bar(decades, stations_n, width=0.4)

    # labels, legend, title
    plt.xlabel("Period", fontsize=12, fontweight="bold")
    plt.xticks(r + width/2,decades, rotation=25)
    plt.ylabel("Number of stations established", fontsize=12, fontweight="bold")
    plt.title("Establishment of stations", fontsize=16, fontweight="bold")
    plt.legend()

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    dir = os.getcwd()+"/Plots/"+str(date_today)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # save plot
    if reporting == True:
        plt.savefig(dir+"/Barplot_station_establishment_"+str(date_today)+"_reporting.jpeg", bbox_inches='tight')
    else:
        plt.savefig(dir+"/Barplot_station_establishment_"+str(date_today)+"_.jpeg", bbox_inches='tight')



# define function: Pie chart the number of stations

def piechart_reporting(json_file):

    """ Pie chart showing the number of stations registered with each reporting status

        Parameters:
        json_file (.json file): containing the required information on the stations
        (WIGOS ID, name, lat, lon, elevation, facilityType, observed Properties, dateEstablsihed,
        dateClosed & reportingStatus)
    """

    # load data
    f = open(json_file)
    data = json.load(f)
    df = pd.DataFrame(data["stations"])

    # find number of stations for each reporting status
    status = ['operational', 'preOperational', 'unknown', 'closed', 'nonReporting']
    status_n = []
    for stat in status:
        status_n.append(len(df[df["reportingStatus"]==stat]))

    # set colors
    colors = ['blue', 'purple', 'grey', 'red', 'orange']
    # make piechart
    plt.style.use('default')
    fig, ax = plt.subplots()
    ax.pie(status_n, labels=status, colors=colors,  autopct='%1.1f%%')
    # set total number of stations as title
    plt.title("n = " + str(len(df)))

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    dir = os.getcwd()+"/Plots/"+str(date_today)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # save plot
    plt.savefig(dir+"/Piechart_reportingStatus_"+str(date_today)+"_.jpeg", bbox_inches='tight')


# define function: Barplot observed propertiess

def barplot_observedProperties_overview(json_file):

    """ Barplot: overview of the observed properties within a country

        Parameters:
        json_file (.json file): containing the required information on the stations
        (WIGOS ID, name, lat, lon, elevation, facilityType, observed Properties, dateEstablsihed,
        dateClosed & reportingStatus)
    """

    # load data
    f = open(json_file)
    data = json.load(f)
    df = pd.DataFrame(data["stations"])
    # create column for number of unique observed properties
    df["observedProperties_unique"] = range(0,len(df))
    pd.options.mode.chained_assignment = None

    # find unique values within list
    def unique(list1):
        ans = reduce(lambda re, x: re+[x] if x not in re else re, list1, [])
        return(ans)

    # find the unique observed poperties at each station
    for i in range(0,len(df)):
        unique_codes = unique(df["observedProperties"][i])
        df["observedProperties_unique"][i] = unique_codes

    # count the observed properties over all stations
    df_count = pd.Series(sum([item for item in df.observedProperties_unique], [])).value_counts()
    df_count = pd.DataFrame(df_count)
    df_count.index.name = 'variables'
    df_count.reset_index(inplace=True)

    # use dictionary to find variable names from notations
    with open(os.getcwd()+"/WMDR_dictionaries/T_GO_VARIABLE_REF_dictionary.json") as f:
        dictionary = json.loads(f.read())

    variables = df_count["variables"]
    df_count["variables_names"] = [(list(dictionary.keys())[list(dictionary.values()).index(var)]) for var in variables]

    # create plot
    plt.style.use('default')
    fig, axes = plt.subplots(1,1, figsize=(14,5))
    # plot numbers
    plt.bar(df_count["variables_names"], df_count["count"], width=0.4, color="purple", label="Number of stations at which the\nvariable was measured at least once")
    # horizontal line at total number of stations
    plt.hlines(y = len(df), xmin=0, xmax=46, colors="k", ls="--")
    t = plt.text(42, 150, "Total stations", fontsize=10)
    t.set_bbox(dict(facecolor='white', alpha=1, edgecolor='white'))
    # labels, legend, title
    plt.xticks(rotation=90)
    plt.legend(loc="center right", fontsize=10, scatterpoints=10)
    plt.ylabel("Number of stations", fontsize=12, fontweight="bold")
    plt.title("Variables measured", fontsize=16, fontweight="bold")

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    dir = os.getcwd()+"/Plots/"+str(date_today)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # save plot
    plt.savefig(dir+"/Barplot_ObservedVariables_"+str(date_today)+"_.jpeg", bbox_inches='tight')



# define function: Barplot observed propertiess

def barplot_observedProperties_overview_stationProgram(json_file):

    """ Barplot: overview of the observed properties within a country; different colors for station program (GAW vs. non-GAW)

        Parameters:
        json_file (.json file): containing the required information on the stations
        (WIGOS ID, name, lat, lon, elevation, facilityType, observed Properties, dateEstablsihed,
        dateClosed & reportingStatus)
    """

    # load data
    f = open(json_file)
    data = json.load(f)
    df = pd.DataFrame(data["stations"])

    # create column for number of unique observed properties
    df["observedProperties_unique"] = range(0,len(df))
    pd.options.mode.chained_assignment = None

    # drop GAW stations
    df = df.drop(df[df['wigosId'] == '0-20008-0-MKN'].index)
    df = df.drop(df[df['wigosId'] == '0-20008-0-NRB'].index)
    df = df.drop(df[df['wigosId'] == '0-20008-0-MLD'].index)

    # set index
    df.reset_index(drop=True, inplace=True)

    # find unique values within list
    def unique(list1):
        ans = reduce(lambda re, x: re+[x] if x not in re else re, list1, [])
        return(ans)

    # find the unique observed poperties at each station
    for i in range(0,len(df)):
        unique_codes = unique(df["observedProperties"][i])
        df["observedProperties_unique"][i] = unique_codes

    # count the observed properties over all stations
    df_count = pd.Series(sum([item for item in df.observedProperties_unique], [])).value_counts()
    df_count = pd.DataFrame(df_count)
    df_count.index.name = 'variables'
    df_count.reset_index(inplace=True)

    # use dictionary to find variable names from notations
    with open(os.getcwd()+"/WMDR_dictionaries/T_GO_VARIABLE_REF_dictionary.json") as f:
        dictionary = json.loads(f.read())

    variables = df_count["variables"]
    df_count["variables_names"] = [(list(dictionary.keys())[list(dictionary.values()).index(var)]) for var in variables]
    df_count["stationProgram"] = "misc"

    # GAW
    df = pd.DataFrame(data["stations"])
    df_GAW = df[(df['wigosId'].isin(['0-20008-0-MKN', '0-20008-0-NRB', '0-20008-0-MLD']))]
    df_GAW.reset_index(drop=True, inplace=True)

    df_GAW["observedProperties_unique"] = range(0,len(df_GAW))
    pd.options.mode.chained_assignment = None
    for i in range(0,len(df_GAW)):
        unique_codes = unique(df_GAW["observedProperties"][i])
        df_GAW["observedProperties_unique"][i] = unique_codes

    # count the observed properties over all stations
    df_GAW = pd.Series(sum([item for item in df_GAW.observedProperties_unique], [])).value_counts()
    df_GAW = pd.DataFrame(df_GAW)
    df_GAW.index.name = 'variables'
    df_GAW.reset_index(inplace=True)
    variables = df_GAW["variables"]
    df_GAW["variables_names"] = [(list(dictionary.keys())[list(dictionary.values()).index(var)]) for var in variables]
    df_GAW["stationProgram"] = "GAW"

    # GAW stations
    for i in range(0,len(df_GAW)):
        if not (df_count["variables_names"].eq(df_GAW["variables_names"].iloc[i])).any():
            new_row = {"variables":df_GAW["variables"].iloc[i],"count":0,"variables_names":df_GAW["variables_names"].iloc[i], "stationProgram":"misc"}
            df_count.loc[len(df_count)] = new_row

    # all station programs
    for i in range(0,len(df_count)):
        if not (df_GAW["variables_names"].eq(df_count["variables_names"].iloc[i])).any():
            new_row = {"variables":df_count["variables"].iloc[i],"count":0,"variables_names":df_count["variables_names"].iloc[i], "stationProgram":"GAW"}
            df_GAW.loc[len(df_GAW)] = new_row

    # sort data frame
    df_count= df_count.sort_values("variables_names")
    df_count.reset_index(inplace=True)
    df_GAW= df_GAW.sort_values("variables_names")
    df_GAW.reset_index(inplace=True)
    df_count["count_GAW"] = df_GAW["count"]
    df_count = df_count.sort_values('count', ascending=False)

    # plot
    fig, ax = plt.subplots(1,1, figsize=(14,5))
    # plot
    ax.bar(df_count["variables_names"], df_count["count"])
    # GAW
    ax.bar(df_count["variables_names"], df_count["count_GAW"], label="GAW", bottom=df_count["count"])
    # horizontal line at total number of stations
    plt.hlines(y = len(df), xmin=0, xmax=46, colors="k", ls="--")
    t = plt.text(42, 150, "Total stations", fontsize=10)
    t.set_bbox(dict(facecolor='white', alpha=1, edgecolor='white'))
    # labels, legend, title
    plt.xticks(rotation=90)
    plt.legend(loc="center right", fontsize=10, scatterpoints=10)
    plt.ylabel("Number of stations", fontsize=12, fontweight="bold")

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    dir = os.getcwd()+"/Plots/"+str(date_today)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # save plot
    plt.savefig(dir+"/Barplot_ObservedVariables_stationProgram_"+str(date_today)+"_.jpeg", bbox_inches='tight')




# define function: create plot showing all deployments registered for a specific station

def plot_deployments_station(WIGOS_ID, include_establishmentDate = False):

    """ create plot showing all deployments registered for a specific station

        Parameters:
        WIGOS_ID (str): WIGOS identifier of the station of interest
        include_establishmentDate (boolean): if True - vertical red line indicates establishment date
    """

    id = WIGOS_ID
    from get_information import get_deployments_station
    df_station,variables_u = get_deployments_station(id)

    # plot
    plt.style.use('default')
    fig, axes = plt.subplots(1,1, figsize=(14,8))
    variables = variables_u
    # plot every deployment
    for var in range(0,len(variables)):
        df_var = df_station[df_station["variable"]==str(variables[var])]
        x_values = [pd.to_datetime(df_var["beginPosition"]), pd.to_datetime(df_var["endPosition"])]
        plt.plot(x_values, [var,var], 'bo', linestyle="--")

    # line for establishment date
    if include_establishmentDate == True:
        est_date = [pd.to_datetime(df_station["dateEstablished"].iloc[0])]
        plt.axvline(x=est_date, c="red", linewidth=5, label= "Establishment Date")
        # legend
        plt.legend(loc="upper left", fontsize=10, scatterpoints=25, bbox_to_anchor=(-0.2, 1.06))

    # plot ployment names
    names = []
    for var in range(0,len(variables)):
        variable_df = df_station[df_station["variable"]==str(variables[var])]
        name = variable_df.iloc[0]["variables_names"]
        names.append(name)
    n = range(0,len(names))
    plt.yticks(n,names)

    # title
    plt.title("WIGOS Station Identifier: " + id, fontsize=16, fontweight="bold")

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    # save figure
    if include_establishmentDate == True:
        dir = os.getcwd()+"/Plots/"+str(date_today)+"/individual_stations/incl_establishmentDate/"
        if not os.path.exists(dir):
            os.makedirs(dir)
        fig.savefig(dir + "/Deployments_"+id+"_"+str(date_today)+"_establishmentDate.jpeg", bbox_inches='tight')
    else:
        dir = os.getcwd()+"/Plots/"+str(date_today)+"/individual_stations/"
        if not os.path.exists(dir):
            os.makedirs(dir)
        fig.savefig(dir + "/Deployments_"+id+"_"+str(date_today)+"_.jpeg", bbox_inches='tight')

    plt.close()


# define function: create date verification plot

def plot_date_verification(country):

    """ create plot showing the establishment date and the date of the beginning of the first deployment for each station within a country

        Parameters:
        country (str): country code - e.g. "KEN" for Kenya
    """

    # get stations
    from get_information import get_WIGOS_ID_country
    wigosIds = get_WIGOS_ID_country(country)

    # get establishment date and date of the beginning of the first deployment for each station
    from get_information import get_information_date_verification
    df_dates = get_information_date_verification(country)

    # define plot
    plt.style.use('default')
    fig, axes = plt.subplots(1,1, figsize=(14,30))

    # set names and color them according to issues
    names = []
    # If the establishment date is after the date of the first deployment, the station label appears in red
    warnings_red = []
    # If the establishment date is before the date of the first deployment but does not correspond to it, the station label appears in orange
    warnings_orange = []
    # If the start date of the deployment is missing, the station label appears in yellow
    warnings_yellow = []

    for id in range(0,len(wigosIds)):
        # information to station
        df_var = df_dates[df_dates["station"]==str(wigosIds[id])]
        # background lines for better overview
        plt.hlines(y=id, xmin=min(pd.to_datetime(df_dates["dateEstablished"])), xmax=pd.Timestamp.today(), linewidth=0.1, color="black")
        # line between establishment date and date of beginning of the first deployment
        # x_values = [pd.to_datetime(df_var["dateEstablished"]), pd.to_datetime(df_var["firstDeploymentStart"])]
        # plt.plot(x_values, [id,id], linestyle="--", color="black", label="difference")
        # triangle indicating establishment date
        plt.plot([pd.to_datetime(df_var["dateEstablished"])], [id], marker=">", linestyle='None', color="red", label="establishment")
        # dot indicating date of beginning of the first deployment
        plt.plot([pd.to_datetime(df_var["firstDeploymentStart"])], [id], marker="o",linestyle='None', color="blue", label = "first deployment")
        # station name
        name = str(df_var.iloc[0]["station"])
        names.append(name)
        # color station name according to existing issues
        # red
        if ((pd.to_datetime(df_var.iloc[0]["dateEstablished"])) > (pd.to_datetime(df_var.iloc[0]["firstDeploymentStart"]))):
            warnings_red.append(id)
        # yellow
        elif pd.isnull(pd.to_datetime(df_var.iloc[0]["firstDeploymentStart"])):
            warnings_yellow.append(id)
        # orange
        elif ((pd.to_datetime(df_var.iloc[0]["dateEstablished"])) != (pd.to_datetime(df_var.iloc[0]["firstDeploymentStart"]))):
            warnings_orange.append(id)

    # xlim
    plt.xlim(min(pd.to_datetime(df_dates["dateEstablished"])), xmax=pd.Timestamp.today())

    # set yticklabels
    n = range(0,len(names))
    plt.yticks(n,names)

    # color of yticklabels
    for i in warnings_red:
        plt.gca().get_yticklabels()[i].set_color("red")
    for i in warnings_orange:
        plt.gca().get_yticklabels()[i].set_color("orangered")
    for i in warnings_yellow:
        plt.gca().get_yticklabels()[i].set_color("gold")

    # legend
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = OrderedDict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc="upper left")

    # set title
    plt.title("Establishment date vs. first deployment"+ ' (status on ' + pd.Timestamp.today().strftime("%Y-%m-%d") + ')', fontsize=16, fontweight="bold")

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    dir = os.getcwd()+"/Plots/"+str(date_today)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # save figure
    fig.savefig(dir + "/EstablishmentDate_vs_FirstDeployment_"+str(date_today)+"_.jpeg", bbox_inches='tight')


# define function: create plot with overview of all deployments of a variable of interest within a country

def plot_deployments_variable_country(country, variable):

    """ create plot with overview of all deployments of a variable of interest within a country

        Parameters:
        country (str): country of interest, e.g. "KEN"
        variable (str): notation of variable according to WMDR (e.g. 224 for Air temperature)

    """
    # plot
    plt.style.use('default')
    fig, axes = plt.subplots(1,1, figsize=(14,30))

    # get data frame with information to plot
    from get_information import get_deployments_variable_country
    df_variable, wigosIds = get_deployments_variable_country(country, variable)

    # plot deployment for every station
    for id in range(0,len(wigosIds)):
        df_var = df_variable[df_variable["station"]==str(wigosIds[id])]
        plt.hlines(y=id, xmin=pd.Series(pd.to_datetime(df_variable["beginPosition"])).min(), xmax=pd.Timestamp.today(), linewidth=0.1, color="black")
        x_values = [pd.to_datetime(df_var["beginPosition"]), pd.to_datetime(df_var["endPosition"])]
        plt.plot(x_values, [id,id], 'bo', linestyle="--")

    # add station names
    names = []
    for var in range(0,len(wigosIds)):
        variable_df = df_variable[df_variable["station"]==str(wigosIds[var])]
        if not variable_df.empty:
            name = str(variable_df.iloc[0]["station"])
            names.append(name)

    plt.xlim(xmin= pd.Series((pd.to_datetime(df_variable["beginPosition"]))).min(), xmax=pd.Timestamp.today())
    n = range(0,len(names))
    plt.yticks(n,names)

    # title
    plt.title("Variable: " + variable, fontsize=16, fontweight="bold")

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    dir = os.getcwd()+"/Plots/"+str(date_today)
    if not os.path.exists(dir):
        os.makedirs(dir)

    # save figure
    fig.savefig(dir+"/Deployments_"+variable+"_"+country+"_"+str(date_today)+"_.jpeg", bbox_inches='tight')
