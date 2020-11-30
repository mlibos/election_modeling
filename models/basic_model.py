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



def find_polls(csvfile,state):
	#finds polls pertaining to given state
	polls = []
	for poll in csvfile:
		if poll[0] == state:
			if len(polls) < 7:
				polls.append(poll)
	return (polls)
def std_dev(proportion,n):
	#finds std_dev of a single poll using variance = np(1-p)
	std_dev = (n*proportion*(1-proportion))**0.5
	return std_dev
def interval_calc(polls):
	#takes a list of polls and computes a 95% confidence interval of vote shares
	biden_mean = []
	trump_mean = []
	totalsample = [0,[]]
	#taking poll results from our poll list and creating lists containing vote totals and sample sizes
	for poll in polls:
		n = int(poll[6])
		biden = int(poll[9])/100
		trump = int(poll[10])/100
		totalsample[0] += n
		totalsample[1].append(n)
		biden_mean.append(biden)
		trump_mean.append(trump)
	#calculating weighted means using a pooled sample
	biden_weighted_mean = 0
	trump_weighted_mean = 0
	for index,mean in enumerate(biden_mean):
		biden_weighted_mean += biden_mean[index]*totalsample[1][index]
	for index,mean in enumerate(trump_mean):
		trump_weighted_mean += trump_mean[index]*totalsample[1][index]
	biden_weighted_mean = round(biden_weighted_mean/totalsample[0],3)
	trump_weighted_mean = round(trump_weighted_mean/totalsample[0],3)
	#calculating variance and std_dev
	n_term = 0
	for n in totalsample[1]:
		n_term += (1/n)
	biden_SE = (biden_weighted_mean*(1-biden_weighted_mean)*n_term)**0.5
	trump_SE = (trump_weighted_mean*(1-trump_weighted_mean)*n_term)**0.5
	#taking std_dev and calculating a 95% confidence interval
	biden_interval = [biden_weighted_mean-biden_SE*1.645,biden_weighted_mean+biden_SE*1.645]
	trump_interval = [trump_weighted_mean-trump_SE*1.645,trump_weighted_mean+trump_SE*1.645]
	for i in range(2):
		biden_interval[i] = round(biden_interval[i],3)
		trump_interval[i] = round(trump_interval[i],3)
	biden_interval.insert(1,biden_weighted_mean)
	trump_interval.insert(1,trump_weighted_mean)
	intervals = [biden_interval,trump_interval,totalsample[0],len(totalsample[1])]
	return intervals

def csv_reader(filename):
	#takes a poll in csv format and attempts to read it and collect data
	#csv is in this format: state,pollster,sponsor,start.date,end.date,entry.date.time..et.,number.of.observations,population,mode,biden,trump,biden_margin,other,undecided,url,include,notes
	states = ["--","AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
	state_intervals = {}
	for state in states:
		#convert to reader csv
		file = open(filename, 'r')
		csvfile = csv.reader(file)
		#find polls for state
		polls = find_polls(csvfile,state)
		#compute intervals
		if polls:
			state_intervals[state] = interval_calc(polls)
		else:
			state_intervals[state] = None
	state_intervals['NATIONAL'] = state_intervals['--']
	del state_intervals['--']
	return state_intervals

for file in data_files:
	if '2020 US' in file:
		filename = file

state_intervals = csv_reader(filename)
for state in state_intervals:
	print(state,state_intervals[state])

def calc_prob(biden_mean,trump_mean,n):
	#difference is always expressed as biden-trump (pos = biden lead, neg = trump lead)
	difference = biden_mean-trump_mean
	return(z_score)

def state_probabilities(state_intervals):
	#uses difference of trump biden proportions to calculate z-score of when the underdog wins the race, giving race probabilities.
	states = ["NATIONAL","AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
	state_probabilities = {}
	for state in states:
		if state_intervals[state] == None:
			pass
		else:
			biden_mean = state_intervals[state][0][1]
			trump_mean = state_intervals[state][1][1]
			n = state_intervals[state][2]
			p_value = calc_prob(biden_mean,trump_mean,n)
			state_probabilities[state] = p_value
	return state_probabilities
# probs = state_probabilities(state_intervals)
# for prob in probs:
# 	print(prob,probs[prob])



	
