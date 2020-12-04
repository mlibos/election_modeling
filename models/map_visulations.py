import plotly.express as px
from basic_model import *

data_files = []
#list out data files in data folder to find one to open
entries = Path('C:/Users/SEDan/Documents/election_modeling/data/')
for entry in entries.iterdir():
	file = 'C:/Users/SEDan/Documents/election_modeling/data/' + entry.name
	data_files.append(file)
for file in data_files:
	if '2020 US' in file:
		filename = file
state_intervals = csv_reader(filename)
probs = state_probabilities(state_intervals)
results = electoral_calculations_simulation(probs,40000)

states = ["AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DC", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA", "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK", "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"]
data = []
for state in states:
	data.append(probs[state]*100)
fig = px.choropleth(locations=states, locationmode="USA-states", color=data, color_continuous_scale='Bluered_r',scope="usa")
fig.show()