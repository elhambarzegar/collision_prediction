import pandas as pd
import geopandas as gpd
from matplotlib import pyplot as plt
import numpy as np


travel_time = pd.read_csv('./datasets/travel-time-2014.csv')
shapefile = gpd.read_file("./datasets/bluetooth-routes/bluetooth_routes_wgs84.shp")

merged = shapefile.merge(travel_time, on='resultId')
merged.dropna()
density = (merged['count']*merged['timeInSeconds'])/(merged['length_m'])
merged['density'] = density
merged['speed'] = merged['length_m']/merged['timeInSeconds']
november_weather = pd.read_csv('./datasets/november-weather-2014.csv')
november_weather.index = pd.to_datetime(november_weather['Date']+" "+november_weather['Time'])
december_weather = pd.read_csv('./datasets/december-2014.csv')
december_weather.index = pd.to_datetime(december_weather['Date']+" "+december_weather['Time'])
october_weather = pd.read_csv('./datasets/october-2014.csv')
october_weather.index = pd.to_datetime(october_weather['Date']+" "+october_weather['Time'])
weather = pd.concat([november_weather, december_weather,october_weather])
weather.loc[weather["Wind"] == "No", "Wind"] = 0

test = pd.read_csv('./datasets/KSI.csv')

coll2014 = test[test['YEAR']==2014]
merged = merged[(merged['updated']>'2014-10-01T00:00:00-05')]
merged.index = pd.to_datetime(merged['updated'].map(lambda x: x[0:-3]))

collision_locations = gpd.GeoDataFrame(coll2014, geometry = gpd.points_from_xy(coll2014['LONGITUDE'], coll2014['LATITUDE']))

for id, geometry in enumerate(shapefile.geometry):
  row = shapefile.iloc[id].resultId
  temp = merged[(merged['resultId']==row)]
    
  #aggregate temp every hour
  aggregated = temp.groupby(by=[
    temp.index.month,
    temp.index.day,
    temp.index.hour
  ]).aggregate({'density':'mean','speed':'mean','updated':'min'})
  aggregated.index = pd.to_datetime(aggregated['updated'].map(lambda x: x[0:-3]))
  
  route = geometry
  route = route.buffer(0.002)

  imp_collisions = collision_locations.within(route)

  coll_loc = coll2014[imp_collisions==True]
  coll_loc.index = pd.to_datetime(coll_loc['DATE'].astype(str)+" "+coll_loc['HOUR'].astype(str)+":00")
  coll_loc = coll_loc[(coll_loc.index>'2014-10-01 00:00:00')]
  print(coll_loc['ObjectId'].count())
  finalData = aggregated.join(weather, how='outer').join(coll_loc, how='outer', rsuffix='_right')

  data = finalData.filter(['resultId','density','speed','Temp','Weather','Wind','Visibility','VISIBILITY','LIGHT','ACCLASS','LONGITUDE','LATITUDE'])
  
  filename = 'result'+ro+'.csv'
  data.to_csv(filename)
