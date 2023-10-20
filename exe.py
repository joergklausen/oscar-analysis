
# import functions
from urllib.request import urlopen
import json
from functions import get_info, plot_deployments_station


# get all ids
#### Get WIGOS IDs for all stations catalogued in a country ####

country = "KEN"

# API: all stations as json
all_stations_KEN_url = "https://oscar.wmo.int/surface/rest/api/search/station?territoryName="+country


response = urlopen(all_stations_KEN_url)
data_json = json.loads(response.read())
stations = data_json["stationSearchResults"]

wigosIds = []

for station in data_json["stationSearchResults"]:
    # print(station["wigosId"])
    wigosId = str(station["wigosId"])
    wigosIds.append(wigosId)


# make plots
for id in wigosIds:
    print("ID: ", id)
    plot_deployments_station(id)

# id = "0-454-2-AWSRUMPHI"

# plot_deployments_station(id)
