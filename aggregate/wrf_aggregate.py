# file wrf_aggregate.py
# command line usage:  python wrf_aggregate.py varlist yearlist monthlist
# where "varlist", "yearlist" and "monthlist" are file 
#    names of files containing lists of variables/years/months to repeat over
# depends on ferret .jnl files: agg.vn.yr.mn.dir.jnl
#
# list of files needed:
# agg.nv.yr.mn.dir.jnl
# variable list
# year list
# month list

import sys
import pyferret
import os
import datetime


# [START_HERE] 
# directory containing output of wrf_extract.py # note: no '/' at end because Ferret will not accept
source_dir = '/fire8/jonc/CANSAC_reanalysis/d03/output_data/extract'
# where the output aggregated netcdf files are saved, leaving off year, which will be added automatically below
save_dir = '/fire8/jonc/CANSAC_reanalysis/d03/output_data/XYt'
# [end directory changes]


#---ferret script name-----------
fsname = 'agg.vn.yr.mn.dir.jnl'

#----------------------------------------------------------------------------


if __name__ == '__main__':    

# read file containing list of variables
    vname = str(sys.argv[1])
    with open(vname) as f:
         variables = f.readlines()

# read file containing list of years
    yname = str(sys.argv[2])
    with open(yname) as f:
         years = f.readlines()

# read filecontaining list of months
    mname = str(sys.argv[3])
    with open(mname) as f:
         months = f.readlines()

    years  = [x.strip() for x in years]
    months = [x.strip() for x in months]

    lfn = 'logfile.'+'agg'+'.txt'
    lfid = open(lfn,'w+')
    lfid.write('Python/PyFerret script logfile \n')
    lfid.write('Input files   '+vname+'   '+yname+'  '+mname+'  '+source_dir+'  '+save_dir+'\n') 
    now = datetime.datetime.now()
    lfid.write(str(now)+'\n')


# loop through days and hours and:  1. open and read gzipped source PNW wrf data  2. copy wrf data to working directory  3. run main.jnl for each hour of each day in list

    for x in years:
        year  = x.strip()
        # create directory save_dir/YEAR if it does not already exist
        try:
          os.mkdir(save_dir+'/'+str(year))
          a = "made directory "+str(year)
        except OSError:
          a = "save_to directory already exists"
        lfid.write(a+'\n')
        for y in months:
            month = y.strip()
            for z in variables:
                var = z.strip()            
                pyferret.start(quiet=True,verify=False,journal=False,memsize=4000)
                fc = 'go '+ fsname +'  ' + var + ' ' + year+' '+month + ' '+ source_dir + '  '+ save_dir+'/'+str(year)
                print(fc)
                pyferret.run(fc)

    now = datetime.datetime.now()
    lfid.write(str(now)+'\n')
    lfid.close()

# command line usage:  python wrf_aggregate.py varlist yearlist monthlist
