# LA_Parking_Citations_Analysis
This project examines the distribution of parking citations given throughout Los Angeles in 2019, aggregated by official neighborhood boundaries. Additionally, it attempts to predict the count of parking citations by neighborhood in the year 2020, assuming that COVID did not occur.

# Project Structure

Here's a map of the project:

**code** -> Scripts + notebook used to clean, visualize, and model the data. \
**data** -> Raw datasets. \
**visualizations** -> Static and interactive (?) visuals. \
**requirements.txt** -> Dependencies needed to reproduce project. 

# Reproducibility

To re-create this project on your device, do the following steps:

1. **Clone Repository**: Run git clone ...
- something about requirements.txt
  

# Data
My project utilizes multiple datasets, in which I've designated one as the 'main' and the others as 'helpers'. The main dataset contains the citations themselves, and the helpers provide additional information about neighborhood geographic boundaries that helped me with creating the neighborhood variable and visualize the citation count. The sources where I found each dataset is **hyperlinked**.
## Datasets 

| Dataset Name | Description | Size | Format| Personal Use|
|----------|----------|----------|----------| ----------|
| [Starter Los Angeles Parking Citations](https://www.kaggle.com/datasets/cityofLA/los-angeles-parking-citations?select=parking-citations.csv) | Parking citations recorded in Los Angeles from pre-2015 to the present day, updated daily but with entry errors. | 2.04 GB | CSV | Main
| [LA DOT Parking Meter Inventories](https://data.lacity.org/Transportation/LADOT-Metered-Parking-Inventory-Policies/s49e-q6j2/about_data) | Current inventory of all LA Parking meters, used to hepl create the amt_of_parking_meters variable. | 2.58 MB | CSV | Helper
| [LA Street Type](https://geohub.lacity.org/datasets/efa5d05db5cd4fe8a8492a13ff1f4a15_17/about) | Categorizes streets into certain groups as a part of the city'a general plan for land use. | 13.4 MB | CSV | Helper |
| [LA Times Neighborhood Boundaries](https://geohub.lacity.org/datasets/la-times-neighborhood-boundaries/explore?location=34.020728%2C-118.410084%2C9) | Provides latitude and longitude coordinates for official neighborhood boundaries. | 968 KB | CSV (names) & GeoJSON (geography) | Helper

For my analysis, N = # observations from the year 2019 as the 'training' information to predict the outcome of citation counts in 2020. 

# Modeling Method 
## Negative Binomial Regression
## Results
