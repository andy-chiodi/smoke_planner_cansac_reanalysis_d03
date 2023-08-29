import pyferret
import datetime
from xy2latlon import roffset

#[start_here]
input_dir  = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/hourly_time_series'
output_dir = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/daily_netcdf'
start_year = '1980'
end_year   = '2022' 
# end of what you might want to change

lfn = 'wrfdaily_logfile.txt'
lfid = open(lfn,'w+')
now = datetime.datetime.now()
lfid.write(str(now)+'\n')

s = ' '
for i in range(1,487):                 # ilon 1-486(7)   Note: Python stops at 486 for range(1,487) 
    for j in range(1,535):         # jlat  1,534(5)  
       i1 = i-1;
       j1 = j-1;  # convert to Ferret index, which starts with 1, wheras python starts with 0
       [offset,lat,lon] = roffset(i1,j1)
       fc = 'go wrfdaily_tz.jnl'+s+str(i)+s+str(j) +s+ str(offset) +s+ input_dir +s+ output_dir +s+ start_year +s+ end_year ;
       print(fc)
       pyferret.start(quiet=True,verify=False,journal=False,memsize=1500)  
       pyferret.run(fc)

et = datetime.datetime.now()
lfid.write(str(et)+'\n')
lfid.close()

# usage:  python wrfdaily_tz.py    
# note that year range and ilat, jlon range are hard coded in this script.
