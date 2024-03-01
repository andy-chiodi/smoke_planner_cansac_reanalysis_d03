# file wrf_extract.py
# command line usage:  python wrf_extract.py year main_CANSAC.jnl
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

# NOTE:  CANSAC files are in different directories
# [jonc@fire extract]$ ls /fire2/cansac_reanalysis/
# 2001  2002  2003  2004  2005  2006  2007  2008  2009  2010  2011
# [jonc@fire extract]$ ls /fire3/cansac_reanalysis/
# 2012  2013  2014  2015  2016  2017  2018  2019  2020  2021
# [jonc@fire extract]$ ls /fire4/cansac_reanalysis/
# 1988  1989  1990  1991  1992  1993  1994  1995  1996  1997  1998  1999  2000
# [jonc@fire extract]$ ls /fire5/cansac_reanalysis/
# 1980  1981  1982  1983  1984  1985  1986  1987

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

    # Jon's additions
    import glob
    import logging
    import time

    # Start the timer
    start_time = time.perf_counter()

    # Get command line arguments
    year = sys.argv[1]

    # Logging
    log_file = "wrf_extract_" + year + ".log"

    if (os.path.exists(log_file)):
        os.remove(log_file)

    # Configure logging
    logging.basicConfig(
      filename=log_file, 
      format='%(asctime)s %(levelname)-8s %(message)s',
      level=logging.INFO,
      datefmt='%Y-%m-%d %H:%M:%S'
    )

    logging.info("sys.argv = " + " ".join(sys.argv))

    # Determine directory with source files
    if ( int(year) in [1980, 1981, 1982, 1983, 1984, 1985, 1986, 1987] ):
        source_dir_base = '/fire5/cansac_reanalysis/' + year + '/'
    elif ( int(year) in [1988, 1989, 1990, 1991, 1992, 1993, 1994, 1995, 1996, 1997, 1998, 1999, 2000] ):
        source_dir_base = '/fire4/cansac_reanalysis/' + year + '/'
    elif ( int(year) in [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021] ):
        source_dir_base = '/fire3/cansac_reanalysis/' + year + '/'
    elif ( int(year) in [2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010, 2011] ):
        source_dir_base = '/fire2/cansac_reanalysis/' + year + '/'
    else:
        logging.error("Year " + year + " is not recognized")
        sys.exit("Year " + year + " is not recognized")

    # [START_HERE] source WRF repository directory location info (possibly no write permission)
    ###source_dir_base = '/fire5/cansac_reanalysis/1981/'
    # working directory info (w/ write permission)
    working_dir = '/fire8/jonc/Projects/smoke_planner_cansac_reanalysis_d03/extract/'
    # where the output netcdf files will be saved
    save_dir = '/fire8/jonc/CANSAC_reanalysis/d03/output_data/extract/'
    # [end of directory changes]

    # Create a list of hours (see jons_python_snippets.md)
    hours = [str(hour).zfill(2) for hour in range(24)]

    # Create an array of daylist files
    ###pattern = str(sys.argv[1]) + '*'
    pattern = 'daylist_' + year + '*'
    directory = os.getcwd()
    daylist_files = glob.glob(directory + "/" + pattern)

    for daylist_file in daylist_files:

        logging.info("daylist_file = " + daylist_file)
        dname = os.path.basename(daylist_file)
        logging.info("dname = " + dname)

        # Use a list comprehension to extract parts of this name
        name, year, run_dir = [s for s in dname.split("_")]

        # read file containing list of days
        with open(dname) as f:
             days = f.readlines()

        # read run subdirectory
        source_dir = source_dir_base + run_dir + "/"
        logging.info("source_dir = " + source_dir)

        # save str name of .jnl ferret script that this shell will run
        fname = str(sys.argv[2])
        logging.info("fname = " + fname)

        days  = [x.strip() for x in days]
        hours = [x.strip() for x in hours]

        #lfn = 'logfile.'+dname+'.txt'
        #lfid = open(lfn,'w+')
        #lfid.write('Python/PyFerret script logfile \n')
        #lfid.write('Input files   '+dname+'\n') 
        #now = datetime.datetime.now()
        #lfid.write(str(now)+'\n')


        # loop through days and hours and:  1. open and read gzipped source PNW wrf data  2. copy wrf data to working directory  3. run main.jnl for each hour of each day in list

        for x in days:
            day  = x.strip()
            logging.info("Working on %s", day)
            for y in hours:
                hour = y.strip()
                logging.debug("Working on %s %d:00", day, hour)
                f_in  = source_dir  + pre+day+'_'+hour+post1                   # source directory then filename
                f_out = working_dir + pre+day+'_'+hour+post2 
                try:
                   shutil.copyfile(f_in, f_out)
                   # ncks run in os.system adds z axes to the wrfout netcdf to allow Ferret to read it and understand the vertical dimensions
                   os1 = 'ncks -A -h -v bottom_top wrf_zaxes.nc ' + ' ' + f_out
                   os2 = 'ncks -A -h -v bottom_top_stag wrf_zaxes.nc ' + ' ' + f_out
                   os3 = 'ncks -A -h -v soil_layers_stag wrf_zaxes.nc ' + ' ' + f_out
                   os.system(os1)
                   os.system(os2)
                   os.system(os3)
                   pyferret.start(quiet=True,verify=False,journal=False,memsize=500)
                   fc = 'go '+ fname +'  ' + ' ' + f_out + ' ' + day + '_' + hour + '  '+ save_dir
                   print(fc)
                   pyferret.run(fc)
                   try:
                      os.remove(f_out)
                      #print('removing source file')
                   except OSError:
                      logging.error("Did not remove " + f_out)
                      #lfid.write('Did not remove '+f_out+'\n')
                      pass
    
                except:
                   logging.error("Could not find " + f_in )
                   #lfid.write('Could not find '+f_in+'\n')
 
# note: gridmet has its own calc. path, merge comes after reshape & todaily

    #et = datetime.datetime.now()
    #lfid.write(str(et)+'\n')
    #lfid.close()

    elapsed = time.perf_counter() - start
    logging.info("Completed in %.1f hours", elapsed / 3600)

# command line usage:  python wrf_extract.py year main_CANSAC.jnl

