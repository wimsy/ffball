def analyze_scores(scoresdf):
  contenders = scoresdf[["Ain't no NCAA", "Usual Suspects", "Sproles Royce", \
    "C-Men", "Boltinators", "Stafford Infection", "Ice Princess"]]
  contenders.plot(kind='kde')
  return contenders
  
