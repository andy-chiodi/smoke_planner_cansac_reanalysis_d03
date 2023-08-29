import json
from ij2latlon import rlatlon
from ij2latlon import rland
from ij2latlon import rhgt
import pyferret
import os
import datetime


def main():
  #[start here]
  rdir = '/storage/chiodi/CANSAC_reanalysis/d03/stats/'                          # working directory where this script resides. 
  wdir = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/stats_json/'         # where output json files will be saved locally                   
  source_dir = '/storage/chiodi/CANSAC_reanalysis/d03/output_data/daily_netcdf'  # where source netcdf daily files reside
  # end of directory definitions
  # I,J range
  i1 = int(1)     # 1 for full domain
  i2 = int(487)   # 487 for full domain
  j1 = int(1)     # 1 for full domain
  j2 = int(535)   # 535 for full domain
  # end of fungibles
  # start a log file
  lfn = 'stats_logfile.txt'
  lfid = open(lfn,'w+')
  now = datetime.datetime.now()
  lfid.write(str(now)+'\n')
  #
  # create the stats json files and cp to S3
  for ilon in range(i1,i2):            # ilon  1,487  
      lfid.write('ilon :'+str(ilon)+'\n')
      for jlat in range(j1,j2):          # jlat   1,535             
       calcstatsferret(ilon,jlat,source_dir)
       calcstatsferret_vector(ilon,jlat,source_dir)
       statsjson(ilon,jlat,rdir,wdir)
  # time stamp and close the logfile
  et = datetime.datetime.now()
  lfid.write(str(et)+'\n')
  lfid.close()

def calcstatsferret(ii,jj,sdir):
  #uses ferret to calculate percentile values. depends on make_percentiles[_month].jnl
  # presently reading daily time series from use /storage/spark/chiodi/PNW_4km_test_bed/ 
  ii = str(ii)
  jj = str(jj)
  # file containing variable names (e.g. MH_MAX)
  fl = 'var_list.dat'
  l = open(fl,'r')
  var = l.readlines()
  pyferret.start(quiet=True,verify=False,journal=False,memsize=500)
  # base case loop
  for v in var:    # cycles through variables listed in ascii file fl = var_list.txt
    nm = v.strip()
    fc = 'go calcstats.jnl'+' '+ii+' '+jj+' '+nm+' '+sdir    
    pyferret.run(fc)
  # subdaily loop
  #for v in subvar:    # cycles through variables listed in ascii file fl = var_list.txt
  #  nm = v.strip()
  #  fc = 'go calcstats_subd.jnl'+' '+ii+' '+jj+' '+nm+' '+subdir
  #  pyferret.run(fc)
  pyferret.stop()

def calcstatsferret_vector(ii,jj,sdir):
  # uses ferret to calculate wind rose stat values. depends on make_windrose[_month].jnl
  # sdir is directory where source daily netcdf files are located
  ii = str(ii)
  jj = str(jj)
  # file containing variable names (w10 or tw)
  fl = 'wind_vector_list.dat'
  l = open(fl,'r')
  var = l.readlines()
  # source nertcdf dir
  #sdir='/storage/spark/chiodi/UW_4km_WRF_smoke_planner_met/daily_netcdf/subdaily'   # soure netcdf daily files
  #print('calc vec :',sdir)
  pyferret.start(quiet=True,verify=False,journal=False,memsize=500)
  for v in var:    # cycles through variables listed in ascii file fl = wind_vector_list.dat
    nm = v.strip()
    fc = 'go calcstats_vector.jnl'+' '+ii+' '+jj+' '+nm+' '+sdir
    #print(fc)
    pyferret.run(fc)    
  pyferret.stop()
 
def statsjson(ii,jj,ddir,odir):
  ii = str(ii)
  jj = str(jj)
  # file containing variable names (e.g. MH_MAX)
  fl = 'var_list.dat'  # concatenation of var_list and subvar_list
  flv = 'wind_vector_list.dat'
  # root file name
  rn = 'i'+ii+'_j'+jj
  # dir where the ascii climatological statistics file will be written to
  #ddir = '/home/chiodi/UW_4km_WRF/stats/data/'
  #print(ddir)
  # dir where the final stats json will reside
  #odir = '/home/chiodi/UW_4km_WRF/stats/data/' 
  # get lat lon;  ixlon jylat
  [lat,lon] = rlatlon(int(ii),int(jj))
  elev = rhgt(int(ii),int(jj))
  l = open(fl,'r')
  vl = open(flv,'r')
  var = l.readlines()
  vec = vl.readlines()

  point = {}
  point['base_period'] = '1980-01-01 to 2022-12-31'
  point['lat'] = lat
  point['lon'] = lon
  point['missing'] = None
  point['grid'] = 'UW WRF 4km'
  point['land'] = str(rland(int(ii),int(jj)))
  point['grid_cell_elevation_in_meters'] = elev
  point['percentiles'] = {}
  point['windroses'] = {}
  out = odir+'i'+ii+'_j'+jj+'_stats.json'
  jf  = 'i'+ii+'_j'+jj+'_stats.json'

  for v in var:    # cycles through variables listed in ascii file fl = var_list.txt
    nm = v.strip()
    # name of climo-statitics file generated from (py)ferret scripts; e.g. w10_daytime_ave.i220.j36.txt
    csf = ddir+nm+'.i'+ii+'.j'+jj+'.txt'
    #print(csf)
    # open the pre-calculated stats file (ascii)
    with open(csf) as f:
    # set Ferret to write "-999.90" to .txt files where data is missing. next line takes -999.90 -> None (python) -> Null (dump to json)     
      X = [[None if x == "-999.90" else float(x) for x in line.split()] for line in f]     
    point['percentiles'][nm] = {}
    period = 'annual'
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[0][0])] = X[0][1]
    point['percentiles'][nm][period][str(X[1][0])] = X[1][1]
    point['percentiles'][nm][period][str(X[2][0])] = X[2][1]
    point['percentiles'][nm][period][str(X[3][0])] = X[3][1]
    point['percentiles'][nm][period][str(X[4][0])] = X[4][1]
    point['percentiles'][nm][period][str(X[5][0])] = X[5][1]
    point['percentiles'][nm][period][str(X[6][0])] = X[6][1]
    point['percentiles'][nm][period][str(X[7][0])] = X[7][1]
    point['percentiles'][nm][period][str(X[8][0])] = X[8][1]
    point['percentiles'][nm][period][str(X[9][0])] = X[9][1]
    point['percentiles'][nm][period][str(X[10][0])] = X[10][1]

    period = 'jan'
    pos = 1
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'feb'
    pos = 2
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'mar'
    pos = 3
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'apr'
    pos = 4
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'may'
    pos = 5
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'jun'
    pos = 6
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'jul'
    pos = 7
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'aug'
    pos = 8
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'sep'
    pos = 9
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'oct'
    pos = 10
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'nov'
    pos = 11
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]

    period = 'dec'
    pos = 12
    st = int(pos*11)
    point['percentiles'][nm][period] = {}
    point['percentiles'][nm][period][str(X[st][0])] = X[st][1]
    point['percentiles'][nm][period][str(X[st+1][0])] = X[st+1][1]
    point['percentiles'][nm][period][str(X[st+2][0])] = X[st+2][1]
    point['percentiles'][nm][period][str(X[st+3][0])] = X[st+3][1]
    point['percentiles'][nm][period][str(X[st+4][0])] = X[st+4][1]
    point['percentiles'][nm][period][str(X[st+5][0])] = X[st+5][1]
    point['percentiles'][nm][period][str(X[st+6][0])] = X[st+6][1]
    point['percentiles'][nm][period][str(X[st+7][0])] = X[st+7][1]
    point['percentiles'][nm][period][str(X[st+8][0])] = X[st+8][1]
    point['percentiles'][nm][period][str(X[st+9][0])] = X[st+9][1]
    point['percentiles'][nm][period][str(X[st+10][0])] = X[st+10][1]
  l.close()
  vec_periods = ['daytime','nighttime','lst_0500_0900','lst_1000_1500','lst_1600_2000']
  for v in vec: # now do w10 and tw
    nm1 = v.strip()
    for p in vec_periods:
      # csf if name of climo-statitics file generated from (py)ferret scripts; e.g. w10_daytime_ave.i220.j36.txt
      nm2  = p.strip()
      nm = nm1+'_direction_'+nm2
      csf = ddir+nm+'.i'+ii+'.j'+jj+'.txt'
      print(csf)
      # open the pre-calculated stats file (ascii)
      point['windroses'][nm] = {}
      point['windroses'][nm]['annual'] = {} 
      point['windroses'][nm]['annual']['allDirection'] = {}
      point['windroses'][nm]['annual']['N'] = {}
      point['windroses'][nm]['annual']['NNE'] = {}
      point['windroses'][nm]['annual']['NE'] = {}
      point['windroses'][nm]['annual']['ENE'] = {}
      point['windroses'][nm]['annual']['E'] = {}
      point['windroses'][nm]['annual']['ESE'] = {}
      point['windroses'][nm]['annual']['SE'] = {}
      point['windroses'][nm]['annual']['SSE'] = {}
      point['windroses'][nm]['annual']['S'] = {}
      point['windroses'][nm]['annual']['SSW'] = {}
      point['windroses'][nm]['annual']['SW'] = {}
      point['windroses'][nm]['annual']['WSW'] = {}
      point['windroses'][nm]['annual']['W'] = {}
      point['windroses'][nm]['annual']['WNW'] = {}
      point['windroses'][nm]['annual']['NW'] = {}
      point['windroses'][nm]['annual']['NNW'] = {}

      point['windroses'][nm]['jan'] = {}
      point['windroses'][nm]['jan']['allDirection'] = {}
      point['windroses'][nm]['jan']['N'] = {}
      point['windroses'][nm]['jan']['NNE'] = {}
      point['windroses'][nm]['jan']['NE'] = {}
      point['windroses'][nm]['jan']['ENE'] = {}
      point['windroses'][nm]['jan']['E'] = {}
      point['windroses'][nm]['jan']['ESE'] = {}
      point['windroses'][nm]['jan']['SE'] = {}
      point['windroses'][nm]['jan']['SSE'] = {}
      point['windroses'][nm]['jan']['S'] = {}
      point['windroses'][nm]['jan']['SSW'] = {}
      point['windroses'][nm]['jan']['SW'] = {}
      point['windroses'][nm]['jan']['WSW'] = {}
      point['windroses'][nm]['jan']['W'] = {}
      point['windroses'][nm]['jan']['WNW'] = {}
      point['windroses'][nm]['jan']['NW'] = {}
      point['windroses'][nm]['jan']['NNW'] = {}

      point['windroses'][nm]['feb'] = {}
      point['windroses'][nm]['feb']['allDirection'] = {}
      point['windroses'][nm]['feb']['N'] = {}
      point['windroses'][nm]['feb']['NNE'] = {}
      point['windroses'][nm]['feb']['NE'] = {}
      point['windroses'][nm]['feb']['ENE'] = {}
      point['windroses'][nm]['feb']['E'] = {}
      point['windroses'][nm]['feb']['ESE'] = {}
      point['windroses'][nm]['feb']['SE'] = {}
      point['windroses'][nm]['feb']['SSE'] = {}
      point['windroses'][nm]['feb']['S'] = {}
      point['windroses'][nm]['feb']['SSW'] = {}
      point['windroses'][nm]['feb']['SW'] = {}
      point['windroses'][nm]['feb']['WSW'] = {}
      point['windroses'][nm]['feb']['W'] = {}
      point['windroses'][nm]['feb']['WNW'] = {}
      point['windroses'][nm]['feb']['NW'] = {}
      point['windroses'][nm]['feb']['NNW'] = {}
      
      point['windroses'][nm]['mar'] = {}
      point['windroses'][nm]['mar']['allDirection'] = {}
      point['windroses'][nm]['mar']['N'] = {} 
      point['windroses'][nm]['mar']['NNE'] = {} 
      point['windroses'][nm]['mar']['NE'] = {} 
      point['windroses'][nm]['mar']['ENE'] = {} 
      point['windroses'][nm]['mar']['E'] = {} 
      point['windroses'][nm]['mar']['ESE'] = {} 
      point['windroses'][nm]['mar']['SE'] = {} 
      point['windroses'][nm]['mar']['SSE'] = {} 
      point['windroses'][nm]['mar']['S'] = {} 
      point['windroses'][nm]['mar']['SSW'] = {} 
      point['windroses'][nm]['mar']['SW'] = {} 
      point['windroses'][nm]['mar']['WSW'] = {} 
      point['windroses'][nm]['mar']['W'] = {} 
      point['windroses'][nm]['mar']['WNW'] = {} 
      point['windroses'][nm]['mar']['NW'] = {} 
      point['windroses'][nm]['mar']['NNW'] = {} 
      
      point['windroses'][nm]['apr'] = {}
      point['windroses'][nm]['apr']['allDirection'] = {}
      point['windroses'][nm]['apr']['N'] = {} 
      point['windroses'][nm]['apr']['NNE'] = {} 
      point['windroses'][nm]['apr']['NE'] = {} 
      point['windroses'][nm]['apr']['ENE'] = {} 
      point['windroses'][nm]['apr']['E'] = {} 
      point['windroses'][nm]['apr']['ESE'] = {} 
      point['windroses'][nm]['apr']['SE'] = {} 
      point['windroses'][nm]['apr']['SSE'] = {} 
      point['windroses'][nm]['apr']['S'] = {} 
      point['windroses'][nm]['apr']['SSW'] = {} 
      point['windroses'][nm]['apr']['SW'] = {} 
      point['windroses'][nm]['apr']['WSW'] = {} 
      point['windroses'][nm]['apr']['W'] = {} 
      point['windroses'][nm]['apr']['WNW'] = {} 
      point['windroses'][nm]['apr']['NW'] = {} 
      point['windroses'][nm]['apr']['NNW'] = {} 
      
      point['windroses'][nm]['may'] = {}
      point['windroses'][nm]['may']['allDirection'] = {}
      point['windroses'][nm]['may']['N'] = {} 
      point['windroses'][nm]['may']['NNE'] = {} 
      point['windroses'][nm]['may']['NE'] = {} 
      point['windroses'][nm]['may']['ENE'] = {} 
      point['windroses'][nm]['may']['E'] = {} 
      point['windroses'][nm]['may']['ESE'] = {} 
      point['windroses'][nm]['may']['SE'] = {} 
      point['windroses'][nm]['may']['SSE'] = {} 
      point['windroses'][nm]['may']['S'] = {} 
      point['windroses'][nm]['may']['SSW'] = {} 
      point['windroses'][nm]['may']['SW'] = {} 
      point['windroses'][nm]['may']['WSW'] = {} 
      point['windroses'][nm]['may']['W'] = {} 
      point['windroses'][nm]['may']['WNW'] = {} 
      point['windroses'][nm]['may']['NW'] = {} 
      point['windroses'][nm]['may']['NNW'] = {} 
      
      point['windroses'][nm]['jun'] = {}
      point['windroses'][nm]['jun']['allDirection'] = {}
      point['windroses'][nm]['jun']['N'] = {} 
      point['windroses'][nm]['jun']['NNE'] = {} 
      point['windroses'][nm]['jun']['NE'] = {} 
      point['windroses'][nm]['jun']['ENE'] = {} 
      point['windroses'][nm]['jun']['E'] = {} 
      point['windroses'][nm]['jun']['ESE'] = {} 
      point['windroses'][nm]['jun']['SE'] = {} 
      point['windroses'][nm]['jun']['SSE'] = {} 
      point['windroses'][nm]['jun']['S'] = {} 
      point['windroses'][nm]['jun']['SSW'] = {} 
      point['windroses'][nm]['jun']['SW'] = {} 
      point['windroses'][nm]['jun']['WSW'] = {} 
      point['windroses'][nm]['jun']['W'] = {} 
      point['windroses'][nm]['jun']['WNW'] = {} 
      point['windroses'][nm]['jun']['NW'] = {} 
      point['windroses'][nm]['jun']['NNW'] = {} 
      
      point['windroses'][nm]['jul'] = {}
      point['windroses'][nm]['jul']['allDirection'] = {}
      point['windroses'][nm]['jul']['N'] = {} 
      point['windroses'][nm]['jul']['NNE'] = {} 
      point['windroses'][nm]['jul']['NE'] = {} 
      point['windroses'][nm]['jul']['ENE'] = {} 
      point['windroses'][nm]['jul']['E'] = {} 
      point['windroses'][nm]['jul']['ESE'] = {} 
      point['windroses'][nm]['jul']['SE'] = {} 
      point['windroses'][nm]['jul']['SSE'] = {} 
      point['windroses'][nm]['jul']['S'] = {} 
      point['windroses'][nm]['jul']['SSW'] = {} 
      point['windroses'][nm]['jul']['SW'] = {} 
      point['windroses'][nm]['jul']['WSW'] = {} 
      point['windroses'][nm]['jul']['W'] = {} 
      point['windroses'][nm]['jul']['WNW'] = {} 
      point['windroses'][nm]['jul']['NW'] = {} 
      point['windroses'][nm]['jul']['NNW'] = {} 

      point['windroses'][nm]['aug'] = {}
      point['windroses'][nm]['aug']['allDirection'] = {}
      point['windroses'][nm]['aug']['N'] = {} 
      point['windroses'][nm]['aug']['NNE'] = {} 
      point['windroses'][nm]['aug']['NE'] = {} 
      point['windroses'][nm]['aug']['ENE'] = {} 
      point['windroses'][nm]['aug']['E'] = {} 
      point['windroses'][nm]['aug']['ESE'] = {} 
      point['windroses'][nm]['aug']['SE'] = {} 
      point['windroses'][nm]['aug']['SSE'] = {} 
      point['windroses'][nm]['aug']['S'] = {} 
      point['windroses'][nm]['aug']['SSW'] = {} 
      point['windroses'][nm]['aug']['SW'] = {} 
      point['windroses'][nm]['aug']['WSW'] = {} 
      point['windroses'][nm]['aug']['W'] = {} 
      point['windroses'][nm]['aug']['WNW'] = {} 
      point['windroses'][nm]['aug']['NW'] = {} 
      point['windroses'][nm]['aug']['NNW'] = {} 
      
      point['windroses'][nm]['sep'] = {}
      point['windroses'][nm]['sep']['allDirection'] = {}
      point['windroses'][nm]['sep']['N'] = {} 
      point['windroses'][nm]['sep']['NNE'] = {} 
      point['windroses'][nm]['sep']['NE'] = {} 
      point['windroses'][nm]['sep']['ENE'] = {} 
      point['windroses'][nm]['sep']['E'] = {} 
      point['windroses'][nm]['sep']['ESE'] = {} 
      point['windroses'][nm]['sep']['SE'] = {} 
      point['windroses'][nm]['sep']['SSE'] = {} 
      point['windroses'][nm]['sep']['S'] = {} 
      point['windroses'][nm]['sep']['SSW'] = {} 
      point['windroses'][nm]['sep']['SW'] = {} 
      point['windroses'][nm]['sep']['WSW'] = {} 
      point['windroses'][nm]['sep']['W'] = {} 
      point['windroses'][nm]['sep']['WNW'] = {} 
      point['windroses'][nm]['sep']['NW'] = {} 
      point['windroses'][nm]['sep']['NNW'] = {} 
      
      point['windroses'][nm]['oct'] = {}
      point['windroses'][nm]['oct']['allDirection'] = {}
      point['windroses'][nm]['oct']['N'] = {} 
      point['windroses'][nm]['oct']['NNE'] = {} 
      point['windroses'][nm]['oct']['NE'] = {} 
      point['windroses'][nm]['oct']['ENE'] = {} 
      point['windroses'][nm]['oct']['E'] = {} 
      point['windroses'][nm]['oct']['ESE'] = {} 
      point['windroses'][nm]['oct']['SE'] = {} 
      point['windroses'][nm]['oct']['SSE'] = {} 
      point['windroses'][nm]['oct']['S'] = {} 
      point['windroses'][nm]['oct']['SSW'] = {} 
      point['windroses'][nm]['oct']['SW'] = {} 
      point['windroses'][nm]['oct']['WSW'] = {} 
      point['windroses'][nm]['oct']['W'] = {} 
      point['windroses'][nm]['oct']['WNW'] = {} 
      point['windroses'][nm]['oct']['NW'] = {} 
      point['windroses'][nm]['oct']['NNW'] = {} 
      
      point['windroses'][nm]['nov'] = {}
      point['windroses'][nm]['nov']['allDirection'] = {}
      point['windroses'][nm]['nov']['N'] = {} 
      point['windroses'][nm]['nov']['NNE'] = {} 
      point['windroses'][nm]['nov']['NE'] = {} 
      point['windroses'][nm]['nov']['ENE'] = {} 
      point['windroses'][nm]['nov']['E'] = {} 
      point['windroses'][nm]['nov']['ESE'] = {} 
      point['windroses'][nm]['nov']['SE'] = {} 
      point['windroses'][nm]['nov']['SSE'] = {} 
      point['windroses'][nm]['nov']['S'] = {} 
      point['windroses'][nm]['nov']['SSW'] = {} 
      point['windroses'][nm]['nov']['SW'] = {} 
      point['windroses'][nm]['nov']['WSW'] = {} 
      point['windroses'][nm]['nov']['W'] = {} 
      point['windroses'][nm]['nov']['WNW'] = {} 
      point['windroses'][nm]['nov']['NW'] = {} 
      point['windroses'][nm]['nov']['NNW'] = {} 

      point['windroses'][nm]['dec'] = {}
      point['windroses'][nm]['dec']['allDirection'] = {}
      point['windroses'][nm]['dec']['N'] = {} 
      point['windroses'][nm]['dec']['NNE'] = {} 
      point['windroses'][nm]['dec']['NE'] = {} 
      point['windroses'][nm]['dec']['ENE'] = {} 
      point['windroses'][nm]['dec']['E'] = {} 
      point['windroses'][nm]['dec']['ESE'] = {} 
      point['windroses'][nm]['dec']['SE'] = {} 
      point['windroses'][nm]['dec']['SSE'] = {} 
      point['windroses'][nm]['dec']['S'] = {} 
      point['windroses'][nm]['dec']['SSW'] = {} 
      point['windroses'][nm]['dec']['SW'] = {} 
      point['windroses'][nm]['dec']['WSW'] = {} 
      point['windroses'][nm]['dec']['W'] = {} 
      point['windroses'][nm]['dec']['WNW'] = {} 
      point['windroses'][nm]['dec']['NW'] = {} 
      point['windroses'][nm]['dec']['NNW'] = {} 
      ws = open(csf,'r')
      lines = ws.readlines() 
      for li in lines:
        x = li.split()
        period = str(x[0])
        direction = str(x[1])
        stat = str(x[2])         
        point['windroses'][nm][period][direction][stat] = None if x[3] == '-999.900' else float(x[3])

  vl.close()
  json.dump(point, open(out,'w'), sort_keys=False, indent = 2)
  # cp to S3
  # out is the json file name including dir, e.g. ~/json/i220_j36_stats.json
  # jf is the json file name on its own, e.g. i200_j36_stats.json
  # aws cp json file  
  cmd = '/home/chiodi/bin/aws/aws s3 cp '+out+' '+'s3://airfire-data-exports/smoke-planner/cansac-reanalysis-d03/'+jf
  os.system(cmd)  

  # remove the temporary ascii created by ferret
  for v in var:    # cycles through variables listed in ascii file fl = var_list.txt
    nm = v.strip()
    # name of climo-statitics file generated from (py)ferret scripts; e.g. w10_daytime_ave.i220.j36.txt
    csf = ddir+nm+'.i'+ii+'.j'+jj+'.txt'
    cmd = 'rm '+' '+csf
    os.system(cmd)    
  for v in vec: # now do w10 and tw
    nm1 = v.strip()
    for p in vec_periods:
      # csf if name of climo-statitics file generated from (py)ferret scripts; e.g. w10_daytime_ave.i220.j36.txt
      nm2  = p.strip()
      nm = nm1+'_direction_'+nm2
      csf = ddir+nm+'.i'+ii+'.j'+jj+'.txt'
      cmd = 'rm '+' '+csf
      os.system(cmd)   


if __name__ == '__main__':
  main()

# usage: pyton make_statsjson.py
