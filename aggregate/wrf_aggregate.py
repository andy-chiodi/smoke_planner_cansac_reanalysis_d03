# file wrf_aggregate.py
# command line usage:  python wrf_aggregate.py year varlist monthlist
# where "varlist" and "monthlist" are file 
#    names of files containing lists of variables/months to repeat over
# depends on ferret .jnl files: agg.vn.yr.mn.dir.jnl
#
# list of files needed:
# agg.nv.yr.mn.dir.jnl
# variable list
# month list

import sys
import pyferret
import os
import datetime

# Jon's additions
import logging
import time

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

    # Start the timer
    start_time = time.perf_counter()

    # Get command line arguments
    year = sys.argv[1]

    # read file containing list of variables
    vname = str(sys.argv[2])
    with open(vname) as f:
         variables = f.readlines()

    # read filecontaining list of months
    mname = str(sys.argv[3])
    with open(mname) as f:
         months = f.readlines()

    months = [x.strip() for x in months]

    #lfn = 'logfile.'+'agg'+'.txt'
    #lfid = open(lfn,'w+')
    #lfid.write('Python/PyFerret script logfile \n')
    #lfid.write('Input files   '+vname+'   '+yname+'  '+mname+'  '+source_dir+'  '+save_dir+'\n') 
    #now = datetime.datetime.now()
    #lfid.write(str(now)+'\n')

    # Logging         
    log_file = "wrf_aggregate_" + year + ".log"
                
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


# loop through days and hours and:  1. open and read gzipped source PNW wrf data  2. copy wrf data to working directory  3. run main.jnl for each hour of each day in list

    # create directory save_dir/YEAR if it does not already exist
    try:
        os.mkdir(save_dir+'/'+ year)
        a = "made directory "+ year
    except OSError:
        a = "save_to directory already exists"
    #lfid.write(a+'\n')
    for y in months:
        month = y.strip()
        logging.debug("Working on %s-%s ...", year, month)
        for z in variables:
            var = z.strip()            
            pyferret.start(quiet=True,verify=False,journal=False,memsize=4000)
            fc = 'go '+ fsname +'  ' + var + ' ' + year +' '+month + ' '+ source_dir + '  '+ save_dir+'/'+ year 
            #print(fc)
            pyferret.run(fc)

    #now = datetime.datetime.now()
    #lfid.write(str(now)+'\n')
    #lfid.close()

    elapsed = time.perf_counter() - start
    logging.info("Completed in %.1f hours", elapsed / 3600)
    

# command line usage:  python wrf_aggregate.py varlist yearlist monthlist

