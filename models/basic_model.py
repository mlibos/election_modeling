import os
import csv
from pathlib import Path 
from zipfile import ZipFile 
import scipy.stats
import math
import random
import time

start = time.time()

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
	#here I do some math MUMBO JUMBO bc I haven't implemented a more nuanced version of accounting for undecided voter share. I assume no more than 2% of votes go to 3rd parties so I split undecided vote 40/60 to each candidate until their combined vote share is 98% b/c of trump polling error
	biden_weighted_mean = (biden_weighted_mean/totalsample[0])
	trump_weighted_mean = (trump_weighted_mean/totalsample[0])
	if biden_weighted_mean + trump_weighted_mean < 0.98:
		undecided = 0.98 - trump_weighted_mean - biden_weighted_mean
		biden_weighted_mean += undecided*(0.3)
		trump_weighted_mean += undecided*(0.7)
	biden_weighted_mean = round(biden_weighted_mean,3)
	trump_weighted_mean = round(trump_weighted_mean,3)

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
	biden_SE = round(biden_SE,5)
	trump_SE = round(trump_SE,5)
	biden_interval.insert(1,biden_weighted_mean)
	trump_interval.insert(1,trump_weighted_mean)
	biden_interval.append(biden_SE)
	trump_interval.append(trump_SE)
	intervals = [biden_interval,trump_interval,totalsample[0]]
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
# for state in state_intervals:
# 	print(state,state_intervals[state])

def calc_prob(biden_mean,biden_SE,trump_mean,trump_SE,n):
	#first we calculate c which is the intersection point of the two curves
	# which results in the parabolic equation ax^2 + bx + c == 0 where
	# a = 1/(2*sigma1^2) - 1/(2*sigma2^2);
	# b = mu2/(sigma2^2) - mu1/(sigma1^2);
	# c = mu1^2/(2*sigma1^2) - mu2^2/(2*sigma2^2) - log(sigma2/sigma1)
	# D = b^2 - 4 * a * c;
	# x1 = (-b + sqrt(D))/(2*a);
	# x2 = (-b - sqrt(D))/(2*a);
	if biden_SE == trump_SE:
		return('same SE')
	a = 1/(2*biden_SE**2) - 1/(2*trump_SE**2)
	b = trump_mean/(trump_SE**2)-biden_mean/(biden_SE**2)
	c = biden_mean**2/(2*biden_SE**2) - trump_mean**2/(2*trump_SE**2) - math.log(trump_SE/biden_SE)
	D = b**2-4*a*c
	x1 = (-b+D**0.5)/(2*a)
	x2 = (-b-D**0.5)/(2*a)
	#one root is positive and the intersection we want, the other is negative and useless
	if x1> x2:
		intersection = x1
	else:
		intersection = x2
	#pvalue will be expressed in terms of biden win
	p_value = round(scipy.stats.norm.sf(intersection,biden_mean,biden_SE),4)
	return p_value


def state_probabilities(state_intervals):
	#uses difference of trump biden proportions to calculate z-score of when the underdog wins the race, giving race probabilities.
	states = ["NATIONAL","AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
	state_probs= {}
	for state in states:
		if state_intervals[state] == None:
			pass
		else:
			biden_mean = state_intervals[state][0][1]
			biden_SE = state_intervals[state][0][3]
			trump_mean = state_intervals[state][1][1]
			trump_SE = state_intervals[state][1][3]
			n = state_intervals[state][2]
			p_value = calc_prob(biden_mean,biden_SE,trump_mean,trump_SE,n)
			state_probs[state] = p_value
	return state_probs
probs = state_probabilities(state_intervals)
# for prob in probs:
# 	print(prob,probs[prob])


def electoral_calculations_simple(state_probabilities):
	#uses state probabilities to calculate electoral college results
	#first I will implement a simple model that just gives expected values for each state instead of running simulations over a large N times
	states = {"AL":9,"AK":3, "AZ":11, "AR":6, "CA":55, "CO":9, "CT":7, "DC":3, "DE":3, "FL":29, "GA":16, "HI":4, "ID":4, "IL":20, "IN":11, "IA":6, "KS":6, "KY":8, "LA":8, "ME":4, "MD":10, "MA":11, "MI":16, "MN":10, "MS":6, "MO":10, "MT":3, "NE":5, "NV":6, "NH":4, "NJ":14, "NM":5, "NY":29, "NC":15, "ND":3, "OH":18, "OK":7, "OR":7, "PA":20, "RI":4, "SC":9, "SD":3, "TN":11, "TX":38, "UT":6, "VT":3, "VA":13, "WA":12,"WV":5, "WI":10,"WY":3}
	biden_votes = 0
	trump_votes = 0
	for state in state_probabilities:
		if state == 'NATIONAL':
			pass
		else:
			biden_votes += state_probabilities[state]*states[state]
			trump_votes += (1-state_probabilities[state])*states[state]
	biden_votes = round(biden_votes,1)
	trump_votes = round(trump_votes,1)
	return(biden_votes,trump_votes)
def electoral_calculations_simulation(state_probabilities,n):
	#runs n simulations of election outcome using calculated probabilities.
	states = {"AL":9,"AK":3, "AZ":11, "AR":6, "CA":55, "CO":9, "CT":7, "DC":3, "DE":3, "FL":29, "GA":16, "HI":4, "ID":4, "IL":20, "IN":11, "IA":6, "KS":6, "KY":8, "LA":8, "ME":4, "MD":10, "MA":11, "MI":16, "MN":10, "MS":6, "MO":10, "MT":3, "NE":5, "NV":6, "NH":4, "NJ":14, "NM":5, "NY":29, "NC":15, "ND":3, "OH":18, "OK":7, "OR":7, "PA":20, "RI":4, "SC":9, "SD":3, "TN":11, "TX":38, "UT":6, "VT":3, "VA":13, "WA":12,"WV":5, "WI":10,"WY":3}
	biden_wins = 0
	trump_wins = 0
	ties = 0
	for simulation in range(n):
		biden_votes = 0
		trump_votes = 0
		for state in state_probabilities:
			#polling error for trump
			error = random.uniform(0.0,0.07)
			value = random.random() + error
			if state == "NATIONAL":
				pass
			elif value < state_probabilities[state]:
				biden_votes += states[state]
			else:
				trump_votes += states[state]
		if biden_votes > trump_votes:
			biden_wins +=1
		elif biden_votes < trump_votes:
			trump_wins +=1
		else:
			ties +=1
	biden_prob = round(biden_wins/n,4)
	trump_prob = round(trump_wins/n,4)
	tie_prob = round(ties/n,4)
	return('Biden probability: ',biden_prob, 'Trump probability: ',trump_prob, "Tie probability: ", tie_prob, 'n = ',n)




print(electoral_calculations_simulation(probs,40000))
end = time.time()
print('time to run: ',end-start)