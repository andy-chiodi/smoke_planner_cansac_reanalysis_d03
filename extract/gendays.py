import sys
from datetime import date, timedelta

def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days + 1)):
        yield start_date + timedelta(n)

year = int(sys.argv[1])
start_date = date(year, 1, 1)
end_date = date(year, 12, 31)
fn = 'cansac_daylist_'+str(year)+'.txt'
f = open(fn,'w')
for single_date in daterange(start_date, end_date):
    #print(single_date.strftime("%Y-%m-%d"))
    d = single_date.strftime("%Y-%m-%d")
    f.write(d+"\n")
f.close()
