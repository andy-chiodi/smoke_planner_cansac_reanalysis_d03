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

## Step 4. Reshape the WRF data into individual netcdf files with all times at a single lat-lon (X-Y) point.



## Step 5. Calculate daily statistics and store results in daily netcdf files

See files and README.nc in `todaily` directory

## Step 6. Create JSON files and upload them to aws bucket

See files and README.nc in `json` directory
