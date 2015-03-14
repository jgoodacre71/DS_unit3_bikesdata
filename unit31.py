
# coding: utf-8

# In[2]:

import requests
r = requests.get('http://www.citibikenyc.com/stations/json')


# In[3]:

r.text


# In[4]:

r.json()


# In[5]:

r.json().keys()


# In[6]:

r.json()['stationBeanList']


# In[7]:

key_list = [] #unique list of keys for each station listing
for station in r.json()['stationBeanList']:
    for k in station.keys():
        if k not in key_list:
            key_list.append(k)


# In[8]:

key_list


# In[9]:

from pandas.io.json import json_normalize

df = json_normalize(r.json()['stationBeanList'])


# In[10]:

import matplotlib.pyplot as plt
import pandas as pd

df['availableBikes'].hist()
plt.show()


# In[11]:

df['totalDocks'].hist()
plt.show()


# In[12]:

df['testStation'].hist()
plt.show()


# In[13]:

df['testStation']


# In[14]:

df['testStation'].count()


# In[15]:

df['testStation'].max()


# In[16]:

key_list


# In[17]:

df[df['testStation']==True].count()


# In[18]:

df[df['statusValue']=='In Service']['availableBikes'].mean()



# In[19]:

df['availableBikes'].median()


# In[20]:

((df['totalDocks']-df['availableDocks'])-df['availableBikes']).mean()


# In[83]:

import sqlite3 as lite

con = lite.connect('citi_bike1.db')
cur = con.cursor()

with con:
    cur.execute('CREATE TABLE citibike_reference (id INT PRIMARY KEY, totalDocks INT, city TEXT, altitude INT, stAddress2 TEXT, longitude NUMERIC, postalCode TEXT, testStation TEXT, stAddress1 TEXT, stationName TEXT, landMark TEXT, latitude NUMERIC, location TEXT )')


# In[84]:

#a prepared SQL statement we're going to execute over and over again
sql = "INSERT INTO citibike_reference (id, totalDocks, city, altitude, stAddress2, longitude, postalCode, testStation, stAddress1, stationName, landMark, latitude, location) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)"

#for loop to populate values in the database
with con:
    for station in r.json()['stationBeanList']:
        #id, totalDocks, city, altitude, stAddress2, longitude, postalCode, testStation, stAddress1, stationName, landMark, latitude, location)
        cur.execute(sql,(station['id'],station['totalDocks'],station['city'],station['altitude'],station['stAddress2'],station['longitude'],station['postalCode'],station['testStation'],station['stAddress1'],station['stationName'],station['landMark'],station['latitude'],station['location']))


# In[85]:

#extract the column from the DataFrame and put them into a list
station_ids = df['id'].tolist() 

#add the '_' to the station name and also add the data type for SQLite
station_ids = ['_' + str(x) + ' INT' for x in station_ids] 

#create the table
#in this case, we're concatentating the string and joining all the station ids (now with '_' and 'INT' added)
with con:
    cur.execute("CREATE TABLE available_bikes ( execution_time INT, " +  ", ".join(station_ids) + ");")


# In[21]:

# a package with datetime objects
import sqlite3 as lite
con = lite.connect('citi_bike1.db')
import time

# a package for parsing a string into a Python datetime object
from dateutil.parser import parse 

import collections


#take the string and parse it into a Python datetime object
exec_time = parse(r.json()['executionTime'])


# In[87]:

with con:
    cur.execute('INSERT INTO available_bikes (execution_time) VALUES (?)', (exec_time.strftime('%s'),))


# In[88]:

id_bikes = collections.defaultdict(int) #defaultdict to store available bikes by station

#loop through the stations in the station list
for station in r.json()['stationBeanList']:
    id_bikes[station['id']] = station['availableBikes']

#iterate through the defaultdict to update the values in the database
with con:
    for k, v in id_bikes.iteritems():
        cur.execute("UPDATE available_bikes SET _" + str(k) + " = " + str(v) + " WHERE execution_time = " + exec_time.strftime('%s') + ";")


# In[74]:




# In[77]:




# In[89]:

for i in range(60):
    r = requests.get('http://www.citibikenyc.com/stations/json')
    exec_time = parse(r.json()['executionTime'])

    cur.execute('INSERT INTO available_bikes (execution_time) VALUES (?)', (exec_time.strftime('%s'),))
    con.commit()

    id_bikes = collections.defaultdict(int)
    for station in r.json()['stationBeanList']:
        id_bikes[station['id']] = station['availableBikes']

    for k, v in id_bikes.iteritems():
        cur.execute("UPDATE available_bikes SET _" + str(k) + " = " + str(v) + " WHERE execution_time = " + exec_time.strftime('%s') + ";")
    con.commit()

    time.sleep(60)

con.close() #close the database connection when done


# In[22]:

con.close()


# In[90]:

import pandas as pd
import sqlite3 as lite

con = lite.connect('citi_bike.db')
cur = con.cursor()


# In[91]:

con.close()


# In[1]:

import requests


# In[23]:

import pandas as pd
import sqlite3 as lite

con = lite.connect('citi_bike1.db')
cur = con.cursor()


# In[24]:

df = pd.read_sql_query("SELECT * FROM available_bikes ORDER BY execution_time",con,index_col='execution_time')


# In[27]:

hour_change = collections.defaultdict(int)
for col in df.columns:
    station_vals = df[col].tolist()
    station_id = col[1:] #trim the "_"
    station_change = 0
    for k,v in enumerate(station_vals):
        if k < len(station_vals) - 1:
            station_change += abs(station_vals[k] - station_vals[k+1])
    hour_change[int(station_id)] = station_change #convert the station id back to integer
    
def keywithmaxval(d):
    # create a list of the dict's keys and values; 
    v = list(d.values())
    k = list(d.keys())

    # return the key with the max value
    return k[v.index(max(v))]

# assign the max key to max_station
max_station = keywithmaxval(hour_change)


# In[28]:

#query sqlite for reference information
cur.execute("SELECT id, stationname, latitude, longitude FROM citibike_reference WHERE id = ?", (max_station,))
data = cur.fetchone()
print "The most active station is station id %s at %s latitude: %s longitude: %s " % data
print "With " + str(hour_change[379]) + " bicycles coming and going in the hour between " + datetime.datetime.fromtimestamp(int(df.index[0])).strftime('%Y-%m-%dT%H:%M:%S') + " and " + datetime.datetime.fromtimestamp(int(df.index[-1])).strftime('%Y-%m-%dT%H:%M:%S')


# In[29]:

import matplotlib.pyplot as plt

plt.bar(hour_change.keys(), hour_change.values())
plt.show()


# In[30]:

df.head


# In[31]:

df


# In[32]:

from mpl_toolkits.basemap import Basemap
St latitude: 40.751551 longitude: -73.993934 


# In[33]:

m = Basemap(projection='npstere',boundinglat=40,lon_0=-74,resolution='l')
x, y = m(-73.993934, 40.751551)


# In[53]:

map = Basemap(projection='merc', lat_0=40.751551, lon_0=-73.993934,
    resolution = 'h', area_thresh = 0.1,
    llcrnrlon=-73.75, llcrnrlat=40.5,
    urcrnrlon=-74.25, urcrnrlat=41)
 

map.drawmapboundary(fill_color='#85A6D9')
map.drawcoastlines(color='#6D5F47', linewidth=.4)
map.drawrivers(color='#6D5F47', linewidth=.4)
map.fillcontinents(color='white',lake_color='#85A6D9')
 
map.drawmeridians(np.arange(0, 360, 30))
map.drawparallels(np.arange(-90, 90, 30))

 
plt.show()


# In[ ]:



