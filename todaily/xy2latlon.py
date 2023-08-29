# converts input lat, lon to neareast X,Y direction indices by using np.unravel_indices based on minimization

import numpy as np
from scipy.io import netcdf
from timezonefinder import TimezoneFinder
from datetime import datetime
from pytz import timezone, utc

def rll(i,j):
    f = netcdf.netcdf_file('cansac.486lon.534lat.nc','r')  # read in prepared lats and lons of CANSAC d03 grid 
    wrflon=f.variables['LON']
    wrflat=f.variables['LAT']
    lat = wrflat[j,i] 
    lon = wrflon[j,i]
    return lat,lon 

def roffset(i,j):
    tf = TimezoneFinder()
    [lat,lon] = rll(i,j)
    """
    returns a location's time zone offset from UTC in hours - presently set to use standard (non-daylight savings) time
    """
    today = datetime.now()
    sday = datetime(2000,7,1)  # a daylight savings-time date
    aday = datetime(2000,1,1)  # a standard-time date (non daylight savings)
    day = aday   # pick standard time
    tz_target = timezone(tf.certain_timezone_at(lng=lon, lat=lat)) # returns timezone, e.g. 'America/Los_Angeles' from lat,lon
    # tz_target could be None! handle error case for large domain (UW WRF i,j domain seems to return named timezones)
    day_target = tz_target.localize(day)
    day_utc = utc.localize(day)
    return (day_utc - day_target).total_seconds() / 3600, lat, lon
