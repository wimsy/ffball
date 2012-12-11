import yql
import webbrowser
import os
from yql.storage import FileTokenStore
import pandas as pd
import copy
from pandas import DataFrame
import pickle
import csv

def get_authvals_csv(authf):
	vals = {}	
	with open(authf, 'rU') as f:
		f_iter = csv.DictReader(f)
		vals = f_iter.next()
	return vals

def refresh_data():
  """ Call with no parameters. Returns a list of JSON rows with score data. """
  auth_vals = get_authvals_csv('auth.csv')
  y = yql.ThreeLegged(auth_vals['consumer_key'], auth_vals['consumer_secret'])
  path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'cache'))
  token_store = FileTokenStore(path, secret=auth_vals['file_token_secret'])
  stored_token = token_store.get('foo')

  if not stored_token:
    request_token, auth_url = y.get_token_and_auth_url()
    webbrowser.open(auth_url)
    verifier = raw_input('Please enter your PIN:')
    access_token = y.get_access_token(request_token, verifier)
    token_store.set('foo', access_token)
  else:
    # Check access_token is within 1hour-old and if not refresh it
    # and stash it
    access_token = y.check_token(stored_token)
    if access_token != stored_token:
        token_store.set('foo', access_token)

  teams_query = "select * from fantasysports.teams where league_key=%s" % str(auth_vals['league_key'])
  teams_yql = y.execute(teams_query, token=access_token)
  team_names = []
  for team in teams_yql.rows:
    team_names.append(team['name'])

  scoreboards_query = "select * from fantasysports.leagues.scoreboard where league_key='273.l.103279' and week in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16)"
  scoreboards_yql = y.execute(scoreboards_query, token=access_token)
  current_week = int(scoreboards_yql.rows[-1]['current_week'])
  scoreboards = scoreboards_yql.rows[0:current_week-1]
  
  standings_query = "select * from fantasysports.leagues.standings where league_key='273.l.103279'"
  standings_yql = y.execute(standings_query, token=access_token)
  standings = standings_yql.rows

  pickle.dump(scoreboards, open('scoreboards.pkl', 'w'))
  pickle.dump(standings, open('standings.pkl', 'w'))
  return scoreboards, standings

def load_data():
  """ Call with no parameters and receive a list of JSON rows from 'scoreboards.pkl' """
  scoreboards = pickle.load(open('scoreboards.pkl', 'r'))
  standings = pickle.load(open('standings.pkl', 'r'))
  return scoreboards, standings

def process_data(scoreboards, standings):
  """ process_data(scoreboards) where scoreboards is a list of JSON rows 
  Returns a pandas DataFrame with weekly score data """
  scores = []
  weeks = []
  for week in scoreboards:
    weeks.append('Week ' + week['scoreboard']['week'])
    pointsd = {}
    for matchup in week['scoreboard']['matchups']['matchup']:
        for team in matchup['teams']['team']:
            pointsd[team['name']] = team['team_points']['total']
    scores.append(copy.copy(pointsd))

  scoresdf = DataFrame(scores, index=weeks)
  for team in scoresdf.columns:
      scoresdf[team] = [float(score) for score in scoresdf[team]]
  
  ranks = []
  teamdata = standings[0]
  for rank in teamdata['standings']['teams']['team']:
    ranks.append({'Rank': rank['team_standings']['rank'], 'Team Name': rank['name'], \
      'Wins': rank['team_standings']['outcome_totals']['wins'], \
      'Losses': rank['team_standings']['outcome_totals']['losses'], \
      'Ties': rank['team_standings']['outcome_totals']['ties'], \
      'Points For': rank['team_standings']['points_for']})
  standingsdf = DataFrame(ranks)    
      
  return scoresdf, standingsdf
