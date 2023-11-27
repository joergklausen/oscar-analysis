# import libraries

import json
import os
import pandas as pd
from datetime import date
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import pandas as pd
import matplotlib.lines as mlines
from IPython import display
import matplotlib.animation as animation
import datetime
from functools import reduce


# define function: Animation of stations establishment

def animation_establishment(json_file, background = True):

    """ Animation of station establishment

        Parameters:
        json_file (.json file): containing the required information on the stations
        (WIGOS ID, name, lat, lon, elevation, facilityType, observed Properties, dateEstablsihed,
        dateClosed & reportingStatus)

        background (boolean): True (default) -> relief as background, False -> white background
    """

    # load data
    f = open(json_file)
    data = json.load(f)
    df_animation = pd.DataFrame(data["stations"])

    # for legend
    def legend_without_duplicate_labels(figure):
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        figure.legend(by_label.values(), by_label.keys(), loc='lower right')

    # figure
    plt.style.use('default')
    fig = plt.figure()

    # Load map background
    m = Basemap(projection='lcc', resolution='h', lat_0=0.1, lon_0=37.5, width=1.5E6, height=1.2E6)
    if background == True:
        m.shadedrelief()
    m.drawcountries(color='black', linewidth=2)
    m.drawcoastlines(color='grey', linewidth=0.8)
    # m.drawrivers(color='grey', linewidth=1.5)

    point = m.plot([], [], c="blue", marker="*")[0]
    props = dict(boxstyle='round', facecolor='wheat', alpha=1)

    # define animation
    def animate(year):
        df = df_animation[(pd.DatetimeIndex(df_animation["dateEstablished"]).year == year)]
        m.scatter(df["lon"], df["lat"], latlon=True, c="blue",s=30,marker="*", label = "established")

        # station closed:
        for i in range(0,len(df["dateClosed"])):
            if not df.iloc[i]["dateClosed"] == "NA":
                m.scatter(df.iloc[i]["lon"], df.iloc[i]["lat"], latlon=True, c="red",s=30,marker="*", label = "closed")

        # legend & year
        legend_without_duplicate_labels(plt)
        plt.text(0.1, 0.1, year, color='black', size=17, weight=800, bbox=props,  horizontalalignment='left', verticalalignment='bottom')
        return m,

    # create animation
    ani = animation.FuncAnimation(fig, animate, frames=range(1908,2023), interval=10)

    # To save the animation using Pillow as a gif
    plt.tight_layout()
    writer = animation.PillowWriter(fps=5, bitrate=1800)

    # save plot to folder with today's date
    date_today = date.today()
    date_today.strftime("%m_%d_%Y")

    # check if directory exists, otherwise create
    dir = os.getcwd()+"/Plots/"+str(date_today)
    if not os.path.exists(dir):
        os.makedirs(dir)
    if background == True:
        ani.save(dir+"/Animation_station_establishment_Kenya_"+str(date_today)+"_relief.gif", writer=writer)
    else:
        ani.save(dir+"/Animation_station_establishment_Kenya_"+str(date_today)+"_.gif", writer=writer)

    plt.show()
