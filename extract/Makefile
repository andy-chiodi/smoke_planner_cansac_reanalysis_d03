# Using this as a placeholder for remembering the commands I need to type

activate:
	conda activate FERRET

clean:
	- rm daylist_*_run*
	- rm logfile.daylist*
        
extract_1982: clean
	/fire8/jonc/Projects/smoke_planner_cansac_reanalysis_d03/extract/create_daylist.sh 1982
	python wrf_extract.py 1982 main_CANSAC.jnl &> output_1982.log &

