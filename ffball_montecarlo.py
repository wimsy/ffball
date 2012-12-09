import random
import pandas as pd
import numpy as np
from pandas import DataFrame

def sim_points(team_stats):
  scores = {}
  for team in team_stats:
    scores[team] = random.gauss(team_stats[team]['mean'], team_stats[team]['std'])
  return scores
  
def decide_games(matchups, scores):
  results = []
  for matchup in matchups:
    if scores[matchup[0]] > scores[matchup[1]]:
      results.append({'Lose': matchup[1], 'Win': matchup[0]})
    elif scores[matchup[0]] < scores[matchup[1]]:
      results.append({'Lose': matchup[0], 'Win': matchup[1]})
    else:
      results = np.NaN
      return results
  return results
  
def sim_games(matchups, team_stats, num):
  results = []
  for sim in range(0,num):
#    print sim
    results.append(decide_games(matchups, sim_points(team_stats)))
  return DataFrame(results)
  
def get_scores(team_stats, num):
  scores = []
  for week in range(0,num):
    scores.append(sim_points(team_stats))
  return scores
  
def calc_finals(semi_results):
  final = [[semi_results[0]['Win'], semi_results[1]['Win']], \
    [semi_results[1]['Lose'], semi_results[0]['Lose']]]
  return final

def calc_outcome(final_results):
  outcome = {'1st': final_results[0]['Win'], '2nd': final_results[0]['Lose'], \
    '3rd': final_results[1]['Win'], '4th': final_results[1]['Lose']}
  return outcome
  
def final_freqs(outcomes):
  outcomesdf = DataFrame(outcomes)
  freqs = []
  for place in outcomesdf.columns:
    freqs.append(outcomesdf[place].value_counts()/float(len(outcomes)))
  freqdf = DataFrame(freqs, index=outcomesdf.columns)
  return freqdf, outcomesdf

def run_trial(semifinal, team_stats):
  scores = get_scores(team_stats, 2)
  final = calc_finals(decide_games(semifinal, scores[0]))
  outcome = calc_outcome(decide_games(final, scores[1]))
  return outcome
  
def run_sim(semifinal, scoresdf, num):
  outcomes = []
  team_stats = get_team_stats(scoresdf)
  for trial in range(0,num):
    outcomes.append(run_trial(semifinal, team_stats))
  freqdf, outcomesdf = final_freqs(outcomes)
  return freqdf, outcomesdf
#  return outcomes

def get_team_stats(scoresdf):
  team_stats = {}
  for team in scoresdf:
    team_stats[team] = {'mean': scoresdf[team].mean(), 'std': scoresdf[team].std()}
  return team_stats
  
def calc_semis(bracket):
  semifinal = [[bracket[0], bracket[3]], [bracket[1], bracket[2]]]
  return semifinal

