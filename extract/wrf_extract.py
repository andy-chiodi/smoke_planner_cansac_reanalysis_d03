# file wrf_extract.py
# command line usage:  python wrf_extract.py daylist hourlist main_CANSAC.jnl
# where "daylist" and "hourlist" are file names of files containing lists of days/hours to repeat over
# depends on ferret .jnl files: recipe_CANSAC.jnl and vi_CANSAC.jnl, as well as the variable-specific
# ferret script that saves to netcdf, e.g. main_CANSAC.jnl (for mixing, trans. wind, vent. index and 10m wspd)
# also needs wrf_zaxes.nc to use Ansley's ncks method for axis modification (from WRF default to a more CF-friendly version)
# outputs the extracted wrf variables, including some calculated in the ferret scripts, with a time axis that allows aggregation (in time) in netcdf format
#
# list of other files needed:
# daylist
# hourlist
# main_CANSAC.jnl (or similar)
# recipe_CANSAC.jnl (or similar)
# vi_2.1.jnl (or similar)
# alpha.nc    (saved from a sample wrfout file; needed to adjust wind direction to Cartesian coordinates)
# wrf_zaxes.nc (created by define_axes.jnl)

# [START_HERE] source WRF repository directory location info (possibly no write permission)
source_dir  = '/storage/chiodi/CANSAC_reanalysis/d03/source_data/'
# working directory info (w/ write permission)
working_dir = '/storage/chiodi/CANSAC_reanalysis/d03/extract/'
# where the output netcdf files will be saved
save_dir = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/extract/'
# [end of directory changes]


# file naming info
pre = 'wrfout_d03_'
post1 = '_00_00'      # the ending of the archived/pre-existing files
post2 = '_00_00z.nc'   # the ending of the cp'd files that will get nckd'd

#----------------------------------------------------------------------------


if __name__ == '__main__':    
    import sys
    import pyferret
    import gzip
    import shutil
    import os
    import datetime

# read file containing list of days
    dname = str(sys.argv[1])
    with open(dname) as f:
         days = f.readlines()

# read filecontaining list of hours
    hname = str(sys.argv[2])
    with open(hname) as f:
         hours = f.readlines()

# save str name of .jnl ferret script that this shell will run
    fname = str(sys.argv[3])

    days  = [x.strip() for x in days]
    hours = [x.strip() for x in hours]

    lfn = 'logfile.'+dname+'.txt'
    lfid = open(lfn,'w+')
    lfid.write('Python/PyFerret script logfile \n')
    lfid.write('Input files   '+dname+'      '+hname+'\n') 
    now = datetime.datetime.now()
    lfid.write(str(now)+'\n')


# loop through days and hours and:  1. open and read gzipped source PNW wrf data  2. copy wrf data to working directory  3. run main.jnl for each hour of each day in list

    for x in days:
        day  = x.strip()
        for y in hours:
            hour = y.strip()
#            fn = pre+day+'-'+hour+post
#            gzd = source+day+'/'+fn
#            unc = working+fn.strip('.gz')
            f_in  = source_dir  + pre+day+'_'+hour+post1                   # source directory then filename
            f_out = working_dir + pre+day+'_'+hour+post2 
            try:
#               with gzip.open(gzd, 'rb') as f_in:       # this can be used if source file is compressed, as is the case in the AirFire UW WRF archive
#                    with open(unc, 'wb') as f_out:
               shutil.copyfile(f_in, f_out)
               # ncks run in os.system adds z axes to the wrfout netcdf to allow Ferret to read it and understand the vertical dimensions
               os1 = 'ncks -A -h -v bottom_top wrf_zaxes.nc ' + ' ' + f_out
               os2 = 'ncks -A -h -v bottom_top_stag wrf_zaxes.nc ' + ' ' + f_out
               os3 = 'ncks -A -h -v soil_layers_stag wrf_zaxes.nc ' + ' ' + f_out
               os.system(os1)
               os.system(os2)
               os.system(os3)
               pyferret.start(quiet=True,verify=False,journal=False,memsize=500)
               fc = 'go '+ fname +'  ' + ' ' + f_out + ' ' + day+'_'+hour + '  '+ save_dir
               print(fc)
               pyferret.run(fc)
               try:
                  os.remove(f_out)
                  #print('removing source file')
               except OSError:
                  lfid.write('Did not remove '+f_out+'\n')
                  pass

            except:
               lfid.write('Could not find '+f_in+'\n')
 
# note: gridmet has its own calc. path, merge comes after reshape & todaily

    et = datetime.datetime.now()
    lfid.write(str(et)+'\n')
    lfid.close()

# command line usage:  python wrf_extract.py daylist hourlist main_CANSAC.jnl
