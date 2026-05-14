import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
from shapely.geometry import Point
import re
import ast
import folium
from folium import Choropleth
import statsmodels.api as sm
import statsmodels.formula.api as smf

# IMPORTANT! My original dataset was huge (~2 GB) and so I took a sample of 10k rows
# below is the commented-out code of what I did and produced an already-sampled dataset that's already
# filtered and on github :)

#citations = pd.read_csv("C:\\Users\\taylor\\Downloads\\parking-citations.csv.zip")
#citations.columns = citations.columns.str.lower().str.replace(" ","_")

#citations['issue_date'] = pd.to_datetime(citations['issue_date'])
#citations['issue_year'] = citations['issue_date'].dt.year

# 2019 only
#citations_2019 = citations[citations['issue_year'] == 2019]

# drop unneded columns
#citations_2019 = citations_2019.drop(['ticket_number','meter_id','rp_state_plate','plate_expiry_date','vin','make','body_style','route','color_description','body_style_description'], axis=1)

#sample_path = "C:\\Users\\taylor\\LA_Parking_Citations_Analysis\\data\\parking_citations_2019_sample.csv"
#citations_2019.sample(n=10000, random_state=42).to_csv(sample_path, index=False)

citations = pd.read_csv("C:\\Users\\taylor\\LA_Parking_Citations_Analysis\\data\\parking_citations_2019_sample.csv") # main
neighborhoods = gpd.read_file("C:\\Users\\taylor\\LA_Parking_Citations_Analysis\\data\\LA_Times_Neighborhood_Boundaries.geojson") # helper
meter_amts = pd.read_csv("C:\\Users\\taylor\\LA_Parking_Citations_Analysis\\data\\LADOT_Metered_Parking_Inventory___Policies.csv") # helper
street_types = pd.read_csv("C:\\Users\\taylor\\LA_Parking_Citations_Analysis\\data\\LA_Street_Type.csv") # helper

# DATA CLEANING!
# we will go one dataset at a time :) 


### CITATIONS ###

# CURRENT DATA SIZE - (10,000,14) originally was (105658, 22) but trimmed it down to 2019 and dropped some columns, as shown commented above
citations_2019.shape

# standardizing column names 
citations_2019.columns = citations_2019.columns.str.lower().str.replace(" ","_")

# trimming off the columns that are not needed for analysis
citations_2019 = citations_2019.drop(['ticket_number','meter_id','rp_state_plate','plate_expiry_date','vin','make','body_style','route','color_description','body_style_description'], axis=1)

# we are only looking at 2019 data
citations_2019 = citations_2019[citations_2019['issue_year'] == 2019]

# split up the issue_date by the month, year, and day of week
citations_2019['issue_date'] = pd.to_datetime(citations_2019['issue_date'])
citations_2019['issue_month'] = citations_2019['issue_date'].dt.month
citations_2019['issue_year'] = citations_2019['issue_date'].dt.year
citations_2019['issue_day_of_week'] = citations_2019['issue_date'].dt.dayofweek #0 - 6 means Monday - Sunday

# dropping marked_time since there's a lot of NAs and we care about what time the citation was issued, not when the car parked
citations_2019 = citations_2019.drop('marked_time', axis=1)



### NEIGHBORHOODS ###

# ORIGINAL DATA SIZE - (114, 3)
neighborhoods.shape
# standardize column names 
neighborhoods.columns = neighborhoods.columns.str.lower().str.replace(" ","_")
# we only care about the neighborhood name and the geometry for our analysis, so we can drop the rest of the columns
neighborhoods = neighborhoods.drop(['objectid','shape_area','shape_len','city'], axis=1)




### STREET TYPES ###

# ORIGINAL DATA SIZE - (11385, 16)
street_types.shape

# standardizing column names
street_types.columns = street_types.columns.str.lower()

# something new! we only want designation == Boulevard I, Boulevard II, Avenue I, Avenue II, Avenue III
# why? because these are Arterial (major) streets according to lacity.gov
street_types = street_types[street_types['designation'].isin(['Boulevard I', 'Boulevard II', 'Avenue I', 'Avenue II', 'Avenue III'])]   

         
                                   
### METER AMTS ###

# ORIGINAL DATA SIZE - (34269, 7)
meter_amts.shape
# making all columns lowercase, no spaces for readability
meter_amts.columns = meter_amts.columns.str.lower()
# we only need lattitude and longitude
meter_amts = meter_amts.drop(['spaceid','metertype','ratetype','raterange','meteredtimelimit'], axis=1)

# make the lat/long into a geometry column for geospatial analysis
meter_amts['geometry'] = meter_amts['latlng'].apply(lambda row: Point(meter_amts['latlon']))
meter_amts = gpd.GeoDataFrame(meter_amts, geometry='geometry')


# creating 3 new variables for dataset

# variable 1: neighborhood
# Use lat/lon to find which neighborhood each citation occurred in
geometry = [Point(xy) for xy in zip(citations_2019['latitude'], citations_2019['longitude'])]
citations_gdf = gpd.GeoDataFrame(citations_2019, geometry=geometry, crs='EPSG:2229')
neighborhoods_projected = neighborhoods.to_crs('EPSG:4326')

# reproject citations to match neighborhoods CRS
citations_gdf = citations_gdf.to_crs('EPSG:4326')

# spatial join - figuring out which neighborhood each citation is in
citations_with_neighborhood = gpd.sjoin(citations_gdf, neighborhoods_projected[['geometry', 'name']], 
                                         how='left', predicate='within')
citations_2019.loc[citations_with_neighborhood.index, 'neighborhood'] = citations_with_neighborhood['name']

# variable 2: major (arterial) street
# get street name (remove numbers) and check if it matches street_types
def extract_street_name(street):
    """Extract the street name, excluding numbers."""
    if pd.isna(street):
        return None
    street_name = re.sub(r'\d+', '', str(street)).strip()
    return street_name

citations_2019['street_name'] = citations_2019['location'].apply(extract_street_name)

street_names_set = set(street_types['stname'].str.strip().unique())

citations_2019['major_street'] = citations_2019['street_name'].apply(
    lambda x: 1 if x in street_names_set else 0
)

# variable 3: amount of meters per neighborhood 
meter_amts['latitude'] = meter_amts['latlng'].apply(lambda x: ast.literal_eval(x)[0])
meter_amts['longitude'] = meter_amts['latlng'].apply(lambda x: ast.literal_eval(x)[1])

# make it a geodataframe
meter_amts_geo = gpd.GeoDataFrame(
    meter_amts,
    geometry=[Point(xy) for xy in zip(meter_amts['longitude'], meter_amts['latitude'])],
    crs='EPSG:4326'
)

# another spatial join - which meters are in which neighborhoods?
meter_amts_with_neighborhood = gpd.sjoin(meter_amts_geo, neighborhoods_projected[['geometry', 'name']], 
                                          how='left', predicate='within')

# count of meters per neighborhood
meters_per_neighborhood = meter_amts_with_neighborhood.groupby('name').size().reset_index(name='amt_of_meters')

if 'amt_of_meters' in citations_2019.columns:
    citations_2019 = citations_2019.drop('amt_of_meters', axis=1)

# merge meter count with citations_2019
citations_2019 = citations_2019.merge(meters_per_neighborhood, 
                                       left_on='neighborhood', 
                                       right_on='name', 
                                       how='left')


if 'name' in citations_2019.columns and 'name' != 'neighborhood':
    citations_2019 = citations_2019.drop('name', axis=1)

# NaN values are now 0
citations_2019['amt_of_meters'] = citations_2019['amt_of_meters'].fillna(0).astype(int)


print(f"\nCitations 2019 shape: {citations_2019.shape}")
print(f"\nNew columns:\n{citations_2019[['neighborhood', 'major_street', 'amt_of_meters']].head()}")


# dropping unneded columns again!
#citations_2019 = citations_2019.drop(['issue_date', 'amt_of_meters_x','amt_of_meters_y'], axis=1)

# turning some variables into categorical and numeric types for modeling
citations_2019['month'] = citations_2019['issue_month'].astype('category')
citations_2019['day_of_week'] = citations_2019['issue_day_of_week'].astype('category')
citations_2019['neighborhood'] = citations_2019['neighborhood'].astype('category')
citations_2019['major_street'] = citations_2019['major_street'].astype('int')
citations_2019['violation_code'] = citations_2019['violation_code'].astype('category')
citations_2019['agency'] = citations_2019['agency'].astype('category')
citations_2019['color'] = citations_2019['color'].astype('category')
citations_2019['fine_amount'] = citations_2019['fine_amount'].astype('float')
citations_2019['amt_of_meters'] = citations_2019['amt_of_meters'].astype('int')
citations_2019['issue_time'] = pd.to_numeric(citations_2019['issue_time'], errors='coerce').astype('Int64')

# full dataset has been made :) - let's see 
citations_2019.head()

# that's all for the cleaning! :)