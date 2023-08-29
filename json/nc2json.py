import json
import sys
import re
import xarray
import numpy
import os
import datetime
from ij2latlon import rlatlon
from ij2latlon import rland

## requires python 3.6+  for xarray.  Check line 54: point['start'] = '1-jan-1980' that date matches source data

def main():
  # this makes the json and cp's it to the aws s3 bucket
  #[start here]
  # directory where the daily netcdf file resides
  input_dir = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/daily_netcdf/'   
  # dir where json will reside
  output_dir = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/json/'
  i1 = int(1)
  i2 = int(487)  # 487
  j1 = int(1)
  j2 = int(535)  # 535
  #[end of directory and range changes]
  # first crate a log file to measure time taken
  lfn = 'logfile.json.txt'
  lfid = open(lfn,'w+')
  lfid.write('Python/PyFerret json script logfile \n')
  now = datetime.datetime.now()
  lfid.write(str(now)+'\n')

  for x in range(i1,i2):             #  1,487 for full domain
      for y in range(j1,j2):         #  1,535 for full domain 
          nc2json(x,y,input_dir,output_dir)

  now = datetime.datetime.now()
  lfid.write(str(now)+'\n')

def nc2json(ii,jj,ddir,odir):
  ii = str(ii)
  jj = str(jj)
  # root file name
  rn = 'i'+ii+'_j'+jj 
  # name of daily-statitics netcdf file generated from wrfdaily_tz.py; 
  fd = ddir+'wrf.daily.i'+ii+'.j'+jj+'.nc'
  # file containing variable names, (e.g. MH_MAX)  listed in the order they appear in the ascii data file.
  fl = 'var_list.txt'
  # get lat lon
  [lat,lon] = rlatlon(int(ii),int(jj))
  # open the netcdf file
  nc = xarray.open_dataset(fd)
  # create dictionary that will be dumped to json
  point = {}
  # some metadata
  point['start'] = '1-jan-1980'       # important that this matches input file!
  point['lat'] = lat
  point['lon'] = lon
  point['missing'] = None
  point['grid'] = 'CANSAC Reanalysis d03'
  point['land'] = str(rland(int(ii),int(jj)))
  # now assign keys and vals in the 'data' dictionary.  the key names are read from var_list.txt  
  point['data'] = {}
  l = open(fl,'r')
  var = l.readlines()

  for v in var:    # cycles through variables listed in ascii file fl = var_list.txt
    nm = v.strip()
    mydict = nc[nm].to_dict()
    mylist = mydict['data']
    flat_list = list(numpy.concatenate(mylist).flat)            # next two lines flatten the dict from the netcdf file
    mylist_none = [None if x != x else round(x,3) for x in flat_list]
    point['data'][nm] = mylist_none
  l.close()

  # dump to json, fo is the json file name
  fo = rn+'.json'
  dfo = odir+fo
  json.dump(point, open(dfo,'w'), sort_keys=False, indent = 2)
  # aws cp json file  
  cmd = '/home/chiodi/bin/aws/aws s3 cp '+dfo+' '+'s3://airfire-data-exports/smoke-planner/cansac-reanalysis-d03/'+fo
  os.system(cmd)
   
#-----------------------------

if __name__ == '__main__':
  main()

# usage example:  python nc2json.py
