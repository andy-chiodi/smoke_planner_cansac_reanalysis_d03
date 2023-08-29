# smoke_planner_cansac_reanalysis_d03

Collection of Python and PyFerret scripts that process CANSAC Reanalysis domain 03 netcdf output into AirFire Smoke Planner JSON format.

## Preliminary notes

PyFerret and Python > 3.6 must be installed.  PyFerret installation notes can be found here: https://github.com/NOAA-PMEL/PyFerret/blob/master/README.md  
The Anaconda/Miniconda installation approach is recommended for Linux. Installing by this method will automatically create a suitable Python environment.

You will find that the PyFerret Readme instructs that, once miniconda is installed, executing the following command will install `pyferret` into conda:
```shell
conda create -n FERRET -c conda-forge pyferret ferret_datasets --yes
```
Here `FERRET` is the environment name where `pyferret` is installed.
You can change that to any name you like, such as `PyFerret`.

### Running PyFerret installed via conda
To start using PyFerret, execute the following command:
```shell
conda activate FERRET
```
replacing `FERRET` with whatever environment name you used.

Once you are done working with PyFerret you can leave this environment,
if you wish, with the command:
```shell
conda deactivate
```

Note: this works best in the Bourne shell.  So, in the case that a C-shell is your default, Pyferret would be started with
```shell
bash
conda activate FERRET
```

### Running the smoke planner back-end scripts

-The Python scripts in this repo are to be executed from a command line.  They will run PyFerret within the Python environment.  In the case of Step 1 for example (see below), typing the following in a command line 
```
python wrf_extract.py daylist hourlist main_CANSAC.jnl
```
will run the script `main_CANSAC.jnl` over each day and hour listed in the `daylist` and `hourlist` files.  Typing
```
cat wrf_[step_name].py
```
where `[step_name]` is the name of the respective step and file (e.g. wrf_extract.py) will show the command line usage example.

-The Python scripts are typically hard coded to command PyFerret to read data in from a one directory and save files to another.  The lines of code specifiying these directories in the respective [step].py files will need to be changed, initially, to suit the local environment.  The text `[START HERE]` has been placed near the top of each main python script to aid with this task.

## Step 1. Extract or calculate desired variables from source CANSAC Reanalysis (WRF) output

Usage Example (while in directory ~/extract):
```
python wrf_extract.py daylist hourlist main_CANSAC.jnl
```
The files `daylist` and `hourlist` contain the lists of days and hours that `main_CANSAC.jnl` will be run over, and can be named whatever you like, say `days.txt`, as long as they are passed to `wrf_extract.py` in this order.

Prerequesites

- Access to the CANSAC output netcdf files 
- ncks
- edit directory names in `wrf_extract.py` to fit local environment
- Pyferret scripts:
   `main_CANSAC.jnl`   loads an uncompressed WRF data file, calls recipe.jnl & vi.jnl, then saves out smoke planner variables (e.g. mixing height, ventilation index, 2m temperature ...)
   `recipe_CANSAC.jnl` defines variables necessary for fire-weather (e.g. relative humidity, virtual potential temperature) based on source WRF output
   `vi_CANSAC.jnl` calculates mixing height, transport wind and ventilation index based on variables provided by WRF or defined by `recipe.jnl`

Variables supported as of 28 August 2023 are: mixing height (mh), transport wind speed (tw), tranport wind vector components rotated to earth coordinates (utwe,vtwe) ventilation index (vi), planetary boundary height (pbl), 10 m wind speed (w10), 10 m wind vector (u10e, v10e), 2m temperature (temp2), 2m rh (rh2), equilibrium moisture content (EMC), 500 mb geopotential height (z500) 

Other files:
   *list_of_hours*  Text file with the names of the forecast hours you want to process on separate lines, such as
```
00
01
02
``` 
The file *hourlist* is provided in this repository and should not need to be changed, unless a subset of hours is desired, or the file naming convention changes (e.g. 00 -> f00)

   *list_of_days*  Text file with dates you want to process on each line, for example
```

2010-01-01 
2010-01-02
2010-01-03
```
an example file *wrf_1980_days.list* is provided in this repository
and the python script *gendays.py* will generate a igiven year's worth of dates when run from a terminal as follows:
```
python gendays.py 1981
```
  - alpha.nc is the netcdf files needed to rotate the WRF wind vectors to North-South, East-West directions.
  - wrf_zaxis.nc is needed to use ncks to slightly modifiy the source CANSAC WRF files so that modern PyFerret can read them (PyFerret gets tripped up by WRF's definition of a vertical axis with horizontal dimension) 

## Step 2. Aggregate the individual hourly files to month-long chunks (netcdf files).

Usage example (in directory ~/aggregate):
```
python wrf_aggregate.py varlist yearlist monthlist
```
where *varlist*, *yearlist* and *monthlist* are ascii files with the names of variables, years and months to aggregate over listed in a single column.  For example, *varlist*, might contain:
```
mh
mh2
pbl
rh2
temp2
tw
u10e
utwe
v10e
vi
vtwe
w10
z500
emc
```
*yearlist*:
```
1980
```
*monthlist*
```
01
02
03
04
05
06
07
08
09
10
11
12
```

wrf_aggregate.py depends on ferret script `agg.vn.yr.mn.dir.jnl`.  Upon successful execution, the month-long aggregated netcdf files containing hourly data will reside in `[save_directory]/YEAR`, where `[save_directory]` is the name specified in wrf_aggregate.py and `YEAR` is, say, `1980` or `1981`, etc.  The `[save_directory]` must exist prior to running this script, however, the ~/YEAR directory will be created by wrf_aggregate.py if it does not already exist.


## Step 3. Get GridMet 1000-hr and 100-hr dead fuel moisture and daily precipitation data (4km horiz. resolution), and regrid it to the CANSAC d03 grid (2km res.).

Usage example (in ~/gridmet directory):
```
python wrf_getregridmet.py varlist yearlist
```
where `varlist` is the name of a file listing the gridmet variable names:
```
pr
fm100
fm1000
```
and `yearlist` is the name of a file listing the years you would like to download and process data for, e.g.:
```
1980
1981
1982
1983
1984
```

Depends on PyFerret scripts getregridmet_fm1000.jnl  getregridmet_fm100.jnl  getregridmet_pr.jnl and a file with the latitudes and longitudes of the CANSAC d03 grid, namely, cansac.486lon.534lat.nc

## Step 4. Reshape the data into netcdf files with all time steps at a single lat-lon (X-Y) point.

Usage example (in ~./reshape directory):
```
python wrf_reshape.py 1980
```

In this case, the year to process is passed to wrf_reshape.py through sys.argv[1] 

Depends on `reshape_gridmet_var_yr_ijrange_sub.jnl`,  `reshape_vars_yr_ijrange.jnl` and  `reshape_var_yr_ijrange_sub.jnl`
Run this after the first three steps have been completed for the given year.  


## Step 5. Calculate daily metrics that will be provided to the client and store them netcdf files

Usage example (in ~./todaily):
```
python wrfdaily_tz.py
```

Depends on Ferret scripts `gridmet_append_vars_ij.jnl`,  `merge.jnl`,  `todaily_transport_wind_tz.jnl`,  `todaily_tz.jnl`,  `todaily_wind_tz.jnl`,  `wrfdaily_tz.jnl` and netcdf file 'cansac.486lon.534lat.nc'.  What most likely can/should be edited is in the Python script `wrfdaily_tz.py` and includes the input and output directory paths, the start and end year of the entire archive that will be sent to the smoke planner (e.g. 1980 - 2022) and the I,J range that the script will iterate over.  The I,J range is hard-coded on lines 18 and 19 and set by default to cover the entire d03 domain (486 I points, 534 J points).  You can edit this range if a subset of the domain is desired for some reason. 

## Step 6. Create JSON files and upload them to aws bucket

Usage example (in ~./json):
```
python nc2json.py
```

Depends on file `var_list.txt`, modules in Python script `ij2latlon.py`, netcdf file `CANSAC_i486_j534_landmask.nc` and `nc2json.py`.  Note that around line 55 of `nc2json.py`  the start date of the JSON file is defined.  This must match the start date of the daily netcdf files (e.g. wrf.daily.i1.j1.nc, wrf.daily.i1.j2.nc ... wrf.daily.i486.j534.nc) in order for the smoke planner client to properly interpret dates.
The aws client will also need to be installed locally to run this and the next step.

## Step 7.  Create JSON stastics files (percentile and wind rose information) and upload them the the aws bucket

Usage example (in ~./stats):

```
python make_statsjson.py
```

This is one of the longer steps in terms of time needed to complete.  The wind rose data is particularly time consuming.
Depends on `ij2latlon.py` from this directory, `CANSAC_i486_j534_landmask.nc` and `hgt.cansac.i486.j534.nc` (height of grid cell is saved in stats.json), Ferret scripts `calcstats.jnl`,  `calcstats_vector.jnl`,  `make_percentiles.jnl`,  `make_percentiles_month.jnl`,  `make_windrose.jnl`, and `make_windrose_month.jnl`, `var_list.dat` and  `wind_vector_list.dat` and make_statsjson.py.

