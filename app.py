import streamlit as st
import math
import pandas as pd
import numpy as np

page_title = "Mixed Skills Tourney Dec 3rd, 2023"
st.set_page_config(page_title=page_title)
st.title(page_title)
sb = st.sidebar
total_cols = st.columns(2)
div_totals = st.expander("Division Totals")

div_max = {
	"REC": 33,
	"INT": 47,
	"COMP": 97,
	"POW": 58,
	"PLUS": 17,
}
# Might be able to actually grab the true division average to improve accuracy
div_score = {
	"REC": 0.5,
	"INT": 1.5,
	"COMP": 2.5,
	"POW": 3.5,
	"PLUS": 4.5,
}

# Create form for easy update.
sf = sb.form("Settings")

players_in = {}
for k, v in div_max.items():
	players_in[k] = sf.slider(f"Number of {k} Players", 0, v, v)

sf.divider()

n_iter = sf.slider(
	"Number of Testing Iterations (Higher number will likely yield better results, but will take more time)",
	0,
	100000,
	1000
)
set_seed = sf.number_input("Set Seed for Controlled Randomness", min_value=0, max_value=10000, step=1, value=None)
if set_seed is None:
	set_seed = np.random.choice(list(range(10000)))

np.random.seed(set_seed)

sf.form_submit_button("Rerun Teams")

total_players = sum(players_in.values())
total_teams = math.floor(total_players / 6)

total_cols[0].metric("Total Number of Players", total_players)
total_cols[1].metric("Total Number of Teams", total_teams)

for i, (k, v) in enumerate(players_in.items()):
	div_totals.metric(f"{k} Players", v)

player_list = ["REC" for i in range(players_in["REC"])] + \
	["INT" for i in range(players_in["INT"])] + \
	["COMP" for i in range(players_in["COMP"])] + \
	["POW" for i in range(players_in["POW"])] + \
	["PLUS" for i in range(players_in["PLUS"])]

# Create teams
def create_teams_one():
	team_df = pd.DataFrame(
		[], 
		columns=[f"Player {p}" for p in range(1, 8)] + ["Team Rating"],
		index=[f"Team {p}" for p in range(1, total_teams + 1)]
	)

	randomizer = []	
	for j in range(7):
		randomizer += list(np.random.choice(list(range(1, total_teams + 1)), total_teams, replace=False))
	randomizer = randomizer[0:len(player_list)]

	for t in range(1, total_teams + 1):
		t_list = [player_list[i] for i, x in enumerate(randomizer) if int(x) == t]
		team_rating = sum([div_score[p] for p in t_list]) / len(t_list)

		if len(t_list) == 6:
			t_list += ["-"]
		t_list += [team_rating]

		team_df.loc[f"Team {t}"] = t_list

	return team_df

def create_teams_many(n):
	best_score = 100
	out_df = None

	progress_text = f"Randomizing Teams {n} Times"
	my_bar = st.progress(0, text=progress_text)

	for i in range(n):
		my_bar.progress(((i + 1) / n), text=progress_text)

		team_df = create_teams_one()
		team_eq = team_df["Team Rating"].std()
		if team_eq < best_score:
			best_score = team_eq
			out_df = team_df.copy()

	my_bar.empty()
	return out_df

team_df = create_teams_many(n_iter)
team_eq = team_df["Team Rating"].std()
sum_cols = st.columns(2)
sum_cols[0].metric("Team Equality (Lower is better and a bit under 0.1 is the best I was getting when running a LOT of iterations)", round(team_eq, 4))
sum_cols[1].metric("Random Seed Used (Keep track of this number if you like the results and then you can recreate this random draw in the future)", set_seed)
team_expander = st.expander("Suggested Team Composition")
team_expander.table(team_df)