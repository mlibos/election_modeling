import os
import csv
from pathlib import Path 
from zipfile import ZipFile 

data_files = []
#list out data files in data folder to find one to open
entries = Path('C:/Users/SEDan/Documents/election_modeling/data/')
for entry in entries.iterdir():
	file = 'C:/Users/SEDan/Documents/election_modeling/data/' + entry.name
	data_files.append(file)

poll = ''
for file in data_files:
	if '2020 US' in file:
		poll = file
file = open(poll, 'r')
states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", 
          "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", 
          "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", 
          "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", 
          "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]


csvfile = csv.reader(file)
# for now I will try to compute a polling average with error for a single state to test my skills.
def csv_reader(csv):
	#takes a poll in csv format and attempts to read it and collect data
	#csv is in this format: state,pollster,sponsor,start.date,end.date,entry.date.time..et.,number.of.observations,population,mode,biden,trump,biden_margin,other,undecided,url,include,notes
	state = 'MA'
	polls = []
	for poll in csv:
		if poll[0] == state:
			polls.append(poll)
	biden_mean = 0
	trump_mean = 0
	totalsample = 0
	for poll in polls:
		totalsample += int(poll[6])
		biden_mean += int(poll[6])*int(poll[9])
		trump_mean += int(poll[6])*int(poll[10])
		biden_std = 0
	biden_mean = round(biden_mean/totalsample,1)
	trump_mean = round(trump_mean/totalsample,1)
	print(biden_mean,trump_mean,totalsample)



csv_reader(csvfile)
