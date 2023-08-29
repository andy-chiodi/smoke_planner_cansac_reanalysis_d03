# defines modules to return lat,lon and landmask info based on pre-defined/prepared WRF grid netcdf file "CANSAC_i486_j534_landmask.nc"

import numpy as np
from scipy.io import netcdf

def rlatlon(i,j):
    f = netcdf.netcdf_file('CANSAC_i486_j534_landmask.nc','r')  # read in prepared lats and lons of CANSAC d03 WRF grid
    wrflon=f.variables['LON']
    wrflat=f.variables['LAT']
    # subtract 1 to return answer in FERRET index convention (first index=1), rather than python (first index value = 0)
    j = j-1
    i = i-1
    lat = round(wrflat[j,i],4)
    lon = round(wrflon[j,i],4)
    return lat,lon 
    f.close()

def rland(i,j):
    f = netcdf.netcdf_file('CANSAC_i486_j534_landmask.nc','r')  # read in landmask from wrfout
    wrfland=f.variables['LAND']
    # subtract 1 to return answer in FERRET index convention (first index=1), rather than python (first index value = 0)
    j = j-1
    i = i-1
    land = wrfland[j,i]
    return land
    f.close()

