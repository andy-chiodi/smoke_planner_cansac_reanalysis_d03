# file wrf_getregridment.py
# command line usage:  python wrf_aggregate.py varlist yearlist
# where "varlist", "yearlist" are file 
#    names of files containing lists of variables/years to repeat over
# depends on ferret .jnl files: getregridmet_pr.jnl getregridmet_fm100.jnl getregridmet_1000.jnl  
#
# list of files needed:
# 
# getregridmet_pr.jnl, getregridmet_fm100.jnl, getregridmet_1000.jnl  
# variable list
# year list
# cansac.486lon.534lat.nc (the curvilinear latitude and longitudes of the CANSAC d03 domain; needed for Ferret of redridding of GridMet data to CANSAC grid)

# [START_HERE] 
# where the regridded, year-long, daily-ave, gridment netcdf files will be saved.  Note that the
# a directory with the name of the given year (e.g. ~/2018) will be appended automatically to the following path
###save_dir = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/XYt/'
save_dir = '/fire8/jonc/CANSAC_reanalysis/d03/output_data/XYt/'
#--------ferret script name
fsname = 'getregridmet_'    #complete in loop for, e.g. >> go getregridment_fm100.jnl 2018 ($save_dir) 

#----------------------------------------------------------------------------

if __name__ == '__main__':    
    import sys
    import pyferret
    import os
    import datetime

# read file containing list of variables
    vname = str(sys.argv[1])
    with open(vname) as f:
         variables = f.readlines()

# read file containing list of years
    yname = str(sys.argv[2])
    with open(yname) as f:
         years = f.readlines()

    years     = [x.strip() for x in years]
    variables = [x.strip() for x in variables]

    lfn = 'logfile.'+'gridmet'+'.txt'
    lfid = open(lfn,'w+')
    lfid.write('Python/PyFerret script logfile \n')
    lfid.write('Input files   '+vname+'   '+yname+'  '+save_dir+'\n') 
    now = datetime.datetime.now()
    lfid.write(str(now)+'\n')


# loop through days and hours and:  1. open and read gzipped source PNW wrf data  2. copy wrf data to working directory  3. run main.jnl for each hour of each day in list

    for x in years:
        year  = x.strip()
        for y in variables:
            var = y.strip()            
            ncfn = var+'_'+year+'.nc' # name of gridmet netcdf file
            oscmd = 'wget -nc -c -nd -nv http://www.northwestknowledge.net/metdata/data/'+ncfn
            os.system(oscmd)
            pyferret.start(quiet=True,verify=False,journal=False,memsize=2000)     
            fc = 'go '+ fsname + var + '.jnl  '+ year + '   '+ save_dir+str(year)
            print(fc)
            pyferret.run(fc)
    now = datetime.datetime.now()
    lfid.write(str(now)+'\n')
    lfid.close()

# command line usage:  python wrf_getregridme.py varlist yearlist
