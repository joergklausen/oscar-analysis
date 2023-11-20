
# import functions
from urllib.request import urlopen
import json
from functions import plot_deployments_station


# get all ids
#### Get WIGOS IDs for all stations catalogued in a country ####

country = "KEN"

# API: all stations as json
all_stations_KEN_url = f"https://oscar.wmo.int/surface/rest/api/search/station?territoryName={country}"


response = urlopen(all_stations_KEN_url)
data_json = json.loads(response.read())
stations = data_json["stationSearchResults"]

wigosIds = []

for station in data_json["stationSearchResults"]:
    wigosId = str(station["wigosId"])
    wigosIds.append(wigosId)


# make plots
for id in wigosIds:
    print("ID: ", id)
    plot_deployments_station(id)

# id = "0-20000-0-63709"
# plot_deployments_station(id)
