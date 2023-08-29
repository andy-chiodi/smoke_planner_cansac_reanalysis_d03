# file wrf_reshape.py
#
# list of files needed
# reshape_gridmet_var_yr_ijrange_sub.jnl
# reshape_vars_yr_ijrange.jnl 
# reshape_var_yr_ijrange_sub.jnl
#
# note: i,j range hard coded below. edit this file to change i,j range if needed
#
# usage example: python wrf_reshape.py 2018

# [start here]
# names of directories to read from/write to
read_from_root = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/XYt'
write_to_root  = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/hourly_time_series/' # adds year
# asign i,j range.  CANSAC max is i:1-486,  j:1-534.  Use Ferret numbering.
i1 = str(1)      # 1
i2 = str(486)    # 486
j1 = str(1)      # 1
j2 = str(534)    # 534
# end of what you might want to change



if __name__ == '__main__':

  import pyferret
  import sys
  import datetime
  import os


# get year to process from command line
  yr = str(sys.argv[1])
  lfn = 'logfile.reshape.txt'
  lfid = open(lfn,'w+')
  lfid.write('Python/PyFerret reshape script logfile \n')
  now = datetime.datetime.now()
  lfid.write(str(now)+'\n')

# create ~/yr directories if they do not already exist

  try:
    os.mkdir(write_to_root+yr)
    a = "made directory"
  except OSError:
    a = "save_to directory already exists"
    
  lfid.write(a+'\n')

# create ferret command

  sp = '  '
  fc = 'go reshape_vars_yr_ijrange.jnl ' + yr + ' ' + i1 +sp+ i2 +sp+ j1 +sp+ j2 +sp+ read_from_root +sp+ write_to_root
  print(fc)

# start and run ferret
  pyferret.start(quiet=True,verify=False,journal=False,memsize=1500)
  pyferret.run(fc)
  pyferret.stop()

# add ending time to logfile
  et = datetime.datetime.now()
  lfid.write(str(et)+'\n')
  lfid.close()

# usage example: python wrf_reshape.py 2018
