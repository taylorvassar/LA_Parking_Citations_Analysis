# LA_Parking_Citations_Analysis
This project examines the distribution of parking citations given throughout Los Angeles in 2019, aggregated by official neighborhood boundaries. Additionally, it attempts to predict the count of parking citations by neighborhood in the year 2020, assuming that COVID did not occur.

# Project Structure

Here's a map of the project:

**code** -> Scripts + notebook used to clean, visualize, and model the data. \
**data** -> Raw datasets. \
**visualizations** -> Static and interactive (?) visuals. \
**requirements.txt** -> Dependencies needed to reproduce project. \

# Reproducibility

To re-create this project on your device, do the following steps:

1. **Clone Repository**: Run git clone ...
- something about requirements.txt
  

# Data
My project utilizes multiple datasets, in which I've designated one as the 'main' and the others as 'helpers'. The main dataset contains the citations themselves, and the helpers provide additional information about neighborhood geographic boundaries that helped me with creating the neighborhood variable and visualize the citation count. The sources where I found each dataset is **hyperlinked**.
## Datasets tables

| Dataset Name | Description | Size | Format| Personal Use|
|----------|----------|----------|----------| ----------|
| [Starter Los Angeles Parking Citations](https://www.kaggle.com/datasets/cityofLA/los-angeles-parking-citations?select=parking-citations.csv) | Parking citations recorded in Los Angeles from pre-2015 to the present day, updated daily but with entry errors. | 2.04 GB | CSV | Main
| Row 2 Col 1 | Row 2 Col 2 | Row 2 Col 3 | Row 2 Col 4 | Helper
| [LA Street Type](https://geohub.lacity.org/datasets/la-times-neighborhood-boundaries/explore?location=34.020728%2C-118.410084%2C9) | Categorizes streets into certain groups as a part of the city'a general plan for land use. | 13.4 MB | CSV | Helper |
| LA Times Neighborhood Boundaries | Provides latitude and longitude coordinates for official neighborhood boundaries. | 968 KB | CSV (names) & GeoJSON (geography) | Helper
for this projecct, i used year = and N= . . .

# Modeling Method 
## Negative Binomial Regression
## Results
