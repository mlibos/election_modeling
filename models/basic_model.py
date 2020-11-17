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
	biden_mean = []
	trump_mean = []
	totalsample = [0,[]]

	#equation for combined_std = sqrt((txx-tx2/tn) / (tn-1)) where tn = total n tx = sum of mean*n txx = sum of tx^2
	for poll in polls:
		n = int(poll[6])
		biden = int(poll[9])/100
		trump = int(poll[10])/100
		totalsample[0] += n
		totalsample[1].append(n)
		biden_mean.append(biden)
		trump_mean.append(trump)
	biden_tx = 0
	biden_txx = 0
	for index,mean in enumerate(biden_mean):
		biden_tx += mean*totalsample[1][index]
		biden_txx += (mean*totalsample[1][index])**2
	trump_tx = 0
	trump_txx = 0
	for index,mean in enumerate(trump_mean):
		trump_tx += mean*totalsample[1][index]
		trump_txx += (mean*totalsample[1][index])**2
	biden_std = ((biden_txx-biden_tx**2/totalsample[0])/(totalsample[0]-1))**0.5
	trump_std = ((trump_txx-trump_tx**2/totalsample[0])/(totalsample[0]-1))**0.5	

	print(biden_mean,trump_mean,totalsample)
	print(biden_std,trump_std)



csv_reader(csvfile)
