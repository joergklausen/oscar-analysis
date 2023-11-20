# About
Analysis of the [OSCAR/Surface](https://oscar.wmo.int/surface/#/) station catalogue using Kenya as an example. The general concept:
* get station identifiers through [OSCAR API](https://oscar.wmo.int/surface/rest/api/search/station?territoryName=KEN)
* analyse xml files from [jOAI](https://oscar.wmo.int/oai/) based on the WIGOS station identifiers 
* used python version 3.10.6

## Analysis of a specific station

### History of deployments at a station
* Example of the Mount Kenya station:
![Deployments at Mount Kenya](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/Deployments_0-20008-0-MKN.jpeg)
* The plot shows the registered deployments on OSCAR/Surface for the selected station. The y-axis shows the different variables measured, whereas the x-axis shows the time.
* The first point is the start of the deployment. The second point indicates the end point. The blue dashed line in between indicates the duration of the deplyoment. -> e.g. MKN: Global solar radiation (downwelling)
* When there is no end date, the second point lies at today. -> e.g. MKN: Air temperature (at specified distance from reference surface)
* If there are more than two points and / or the line is solid, there are multiple deployments for a variable. -> e.g. MKN: CO
* In rare cases, there is no start date for a deployment (then only one point is visible). -> e.g. MKN: Light absorptino coefficient, total aerosol
* Other plots in [this folder](https://github.com/sdanioth/OSCAR_analysis/tree/main/Plots)

## Analysis over all stations of a country

### Piechart: reporting status
* E.g. Kenya:
![Pie chart](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/Station_ReportingStatus_piechart.jpeg)

### Barplot: station establishment over decades
* E.g. Kenya:
![Barplot](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/Station_establishment_barplot.jpeg)

### Overview of the measured variables
* E.g. Kenya:
![Variables](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/MeasuredVariables_Overview.jpeg)

### One specific variable in a country
* E.g. Air temperature in Kenya:
![Variable 224](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/Variable_224_KEN.jpeg)

## Map
### Overview: all stations in the country
* E.g. Kenya;
![Kenyan overview](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/all_stations_reportingStatus.jpeg)

### Establishment over the decades
* E.g. Kenya:
![including reporting status](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/Station_establishment_decade_reporting.jpeg)

## Animation: evolution over time
![Evolution of stations over time](https://github.com/sdanioth/OSCAR_analysis/blob/main/station_establishment_Kenya.gif)

## Analyses of ambiguities in the station catalogue

### History of deployments including establishment date
* Example of the Lamu station:
![Deployments and establishment date at Lamu](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/Deployments_0-20000-0-63772_withEstablishmentDate.jpeg)
* The plot is the same as [Deployments at Mount Kenya](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/Deployments_0-20008-0-MKN.jpeg) with the establishment date added as a vertical red line.
* E.g. Lamu was established in 1908. The first deployment registered starts in 2016. There is a huge gap in between.

### Establishment date vs. date of first deployment
![Overview over all Kenyan stations](https://github.com/sdanioth/OSCAR_analysis/blob/main/Plots/EstablshmentDate_vs_FirstDeployment.jpeg)
* The plot shows the establishment dates of the stations versus the dates of the first registered deployments of the stations. The y-axis shows the stations, whereas the x-axis shows the time.
* The red triangles indicate the establishment date. The blue dots indicate the date of the first deployment. The black dashed lines show if there is a difference.
