# smoke_planner_cansa_Reanalysis_d03

Collection of Python and PyFerret scripts that process CANSAC Reanalysis domain 03 (d03) netcdf output into AirFire Smoke Planner JSON format.

## Preliminary notes

PyFerret and Python > 3.6 must be installed.  PyFerret installation notes can be found here: https://github.com/NOAA-PMEL/PyFerret/blob/master/README.md  
The Anaconda/Miniconda installation approach is recommended for Linux. Installing by this method will automatically create a suitable Python environment.

The following excerpts are from the PyFerret Readme: With miniconda installed, execute the following command on the terminal to install `pyferret` as well as
`ferret_datasets` into conda:
```shell
conda create -n FERRET -c conda-forge pyferret ferret_datasets --yes
```
(`FERRET` is the environment name where `pyferret` is installed.
You can change that to any name you like, such as `PyFerret`.)

### Running PyFerret installed via conda
To start using PyFerret, execute the following command:
```shell
conda activate FERRET
```
(replacing `FERRET` with whatever environment name you used.)

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

-The Python scripts in this repo are to be executed in Python from a command line.  They will run the PyFerret scripts within the Python environment.  For example, typing the following in a command line `python wrf_extract.py daylist hourlist main_CANSAC.jnl` will run the script `main_CANSAC.jnl` over each day and hour listed in the daylist and hourlist files.  This will be the first of several steps in processing the CANSAC data to smoke planner (see below for a description of each step)

-These scripts are hard coded to read data in from a one directory and save files to either that same, or another directory.  The lines of code specifiying these directories will need to be changed to suit the local environment.  The text `[START HERE]` has been placed near the start of each main python script to facilitate this process.

## Step 1. Extract WRF output data to hourly netcdf files containing desired variables (including some that are calculated in this step) on a time axis, with wind directions rotated to Earth-relative coordinates (North-South, East-West)
Prerequesites

- The source WRF output netcdf files 
- Python script `wrf_extract.py`.  example linux command line usage `python wrf_extract.py daylist hourlist main_CANSAC.jnl`
  `wrf_extract.py` loops though the lists of days and hours in the *daylist* and *hourlist* files (see below) and runs
  the PyFerret script it is given (in this case, main_CANSAC.jnl) for each listed hour (in this case, 00, 01, 02, ...23) of each listed day
  
- Pyferret scripts:
  - `main_CANSAC.jnl`                loads an uncompressed WRF data file, calls recipe.jnl & vi.jnl, then saves out smoke planner variables (e.g. mixing height, ventilation index, 2m temperature ...)
  - `recipe_CANSAC.jnl` defines variables necessary for fire-weather (e.g. relative humidity, virtual potential temperature) based on saved-out WRF variables
  - `vi.jnl` [`vi_346x265.jnl`] calculates mixing height, transport wind and ventilation index based on variables provided by WRF or defined by `recipe.jnl`

Variables supported as of 28 August 2023 are: mixing height (mh), transport wind speed (tw), tranport wind vector components rotated to earth coordinates (utwe,vtwe) ventilation index (vi), planetary boundary height (pbl), 10 m wind speed (w10), 10 m wind vector (u10e, v10e), 2m temperature (temp2), 2m rh (rh2), equilibrium moisture content (EMC), 500 mb geopotential height (z500) 

Other files:
  - *list_of_hours*  Text file with the names of the forecast hours you want to process on separate lines, such as
```
00
01
02
``` 
The file *hourlist* is provided in this repository and should not need to be changed, unless a subset of hours is desired, or the file naming convention changes (e.g. 00 -> f00)

  - *list_of_days*  Text file with dates you want to process on each line, for example
```

2010-01-01 
2010-01-02
2010-01-03
```
an example file *wrf_1980_days.list* is provided in this repository
and the python script *gendays.py* will generate a year's worth of dates when run from a terminal as follows:
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

wrf_aggregate.py depends on ferret script `agg.vn.yr.mn.dir.jnl`.  Output month-long netcdf files containing hourly data will reside in `[save_directory]/YEAR`, where `[save_directory]` is that specified in wrf_aggregate.py and `YEAR` is, say, `1980` or `1981`, etc.  The `[save_directory]` must exist prior to running this script, however, the ~/YEAR directory will be created if it does not already exist.


## Step 4. Reshape the WRF data into individual netcdf files with all times at a single lat-lon (X-Y) point.

See files and README.md in `reshape` directory

## Step 5. Calculate daily statistics and store results in daily netcdf files

See files and README.nc in `todaily` directory

## Step 6. Create JSON files and upload them to aws bucket

See files and README.nc in `json` directory
