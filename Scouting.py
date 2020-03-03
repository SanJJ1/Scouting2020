import feedparser
import statistics
import numpy as np
import pprint
from scipy import stats
import math


# The source for the RSS feed for the match. May be downloaded locally, or a web link for live data and updates. ANY
# RSS Feed posted on Blue Alliance may be entered here to be analyzed. If you get the error: "ValueError: Inputs must
# not be empty.", you are most likely not accessing the Match RSS Feed properly. I have included three match RSS
# Feeds in case.
dataSource = "https://www.thebluealliance.com/event/2020ohmv/feed"


# The following line extracts the valuable data (match data) from the RSS Feed. The match data returns as an array of
# arrays in the format [ [*Red Alliance Score*, *Red Team 1*, *Red Team 2*, *Red Team 3*, *Blue Alliance Score*,
# *Blue Team 1*, *Blue Team 2*, *Blue Team 3*, *Match title* ], [*Red Alliance Score*, *Red Team 1*, *Red Team 2*,
# *Red Team 3*, *Blue Alliance Score*, *Blue Team 1*, *Blue Team 2*, *Blue Team 3*, *Match title* ], [Match 3],
# [Match 4]... ]
allMatches = [x['summary_detail']['value'].split("\n") + [x['title']] for x in feedparser.parse(dataSource)['entries']]


# Lines 25-32 Format AllData, getting rid of unnecessary markup syntax needed in the RSS Feed XML format.
for i in allMatches: 
    for x in "01235678":
        i[int(x)] = ''.join(c for c in i[int(x)] if c.isdigit())
        if int(x) % 5 == 0:
            i[int(x)] = i[int(x)][1:-1]
    i.pop(4)
    i.insert(8, ["Red", "Blue"][int(i[0]) < int(i[4])])


# Lines 40-45 make sure only match data for finished matches is used.
# When a scheduled match hasn't been played yet, the score for each alliance is set as
# "-1". This changes to a "1" when lines 25-32 format the data. So if "1", is detected
# as a score, it assumed to be an unplayed match. This is needed for when this 
# this script is being run mid-competition before all matches(including playoff matches)
# have been finished.
temp = []
for i in allMatches:
    if i[0] != "1":
        temp.append(i)

allMatches = temp


# pointsScored() gets a list of matches that an input team played, and calculates the average points scored in each
# match.
def pointsScored(team):
    team = str(team)
    teamScores = []
    for match in allMatches:
        if team in match[1:4]:
            teamScores.append(match[0])
        elif team in match[5:8]:
            teamScores.append(match[4])
    return statistics.mean([int(score) for score in teamScores])


# pointsAllowed() gets a list of matches that an input team played, and calculates the average points the team
# allowed in each match.
def pointsAllowed(team):
    team = str(team)
    teamScores = []
    for match in allMatches:
        if team in match[1:4]:
            teamScores.append(match[4])
        elif team in match[5:8]:
            teamScores.append(match[0])
    return statistics.mean([int(score) for score in teamScores])


# opp() gets a list of every opponent that a particular team played during all its matches, and calculates the
# average of each opponents average score
def opp(team):
    team = str(team)
    opps = []
    for match in allMatches:
        if team in match[1:4]:
            opps.extend(match[5:8])
        elif team in match[5:8]:
            opps.extend(match[1:4])
    return statistics.mean(pointsScored(team) for team in opps)


# teammate() gets a list of every teammate that a particular team played with during all its matches, and calculates the
# average of each teammates average score
def teammate(team):
    team = str(team)
    teammates = []
    for match in allMatches:
        if team in match[1:4]:
            x = match[1:4]
            x.remove(team)
            teammates.extend(x)
        if team in match[5:8]:
            x = match[5:8]
            x.remove(team)
            teammates.extend(x)
    return statistics.mean([pointsScored(team) for team in teammates])


# teammateTeammate() gets a list of all the teammates an input team played with, and gets a list of every team in
# turn that that team played with, and returns the average of every teammates average of their teammates average
# score.
def teammateTeammate(team):
    team = str(team)
    teammates = []
    for match in allMatches:
        if team in match[1:4]:
            x = match[1:4]
            x.remove(team)
            teammates.extend(x)
        if team in match[5:8]:
            x = match[5:8]
            x.remove(team)
            teammates.extend(x)
    return statistics.mean([teammate(team) for team in teammates])


# teammateOpp() gets a list of all the teammates an input team played with, and gets a list of every opponent in
# turn that that team played against, and returns the average of every teammates average of their opponents average
# score.
def teammateOpp(team):
    team = str(team)
    teammates = []
    for match in allMatches:
        if team in match[1:4]:
            x = match[1:4]
            x.remove(team)
            teammates.extend(x)
        if team in match[5:8]:
            x = match[5:8]
            x.remove(team)
            teammates.extend(x)
    return statistics.mean([opp(team) for team in teammates])


# teammateAllowed() gets a list of every teammate that a particular team played with during all its matches,
# and calculates the average of each teammates opponents average score
def teammateAllowed(team):
    team = str(team)
    teammates = []
    for match in allMatches:
        if team in match[1:4]:
            x = match[1:4]
            x.remove(team)
            teammates.extend(x)
        if team in match[5:8]:
            x = match[5:8]
            x.remove(team)
            teammates.extend(x)
    return statistics.mean([pointsAllowed(team) for team in teammates])


# oppTeammate() gets a list of all the opponents an input team played with, and gets a list of every teammate in
# turn that that team played with, and returns the average of every opponents average of their teammates average
# score.
def oppTeammate(team):
    team = str(team)
    opps = []
    for match in allMatches:
        if team in match[1:4]:
            opps.extend(match[5:8])
        elif team in match[5:8]:
            opps.extend(match[1:4])
    return statistics.mean(teammate(team) for team in opps)


# oppOpp() gets a list of all the opponents an input team played with, and gets a list of every opponent in
# turn that that team played against, and returns the average of every opponentse average of their opponents average
# score.
def oppOpp(team):
    team = str(team)
    opps = []
    for match in allMatches:
        if team in match[1:4]:
            opps.extend(match[5:8])
        elif team in match[5:8]:
            opps.extend(match[1:4])
    return statistics.mean(opp(team) for team in opps)


# oppAllowed() gets a list of every opponent that a particular team played against during all its matches,
# and calculates the average of the average points allowed by each opponent
def oppAllowed(team):
    team = str(team)
    opps = []
    for match in allMatches:
        if team in match[1:4]:
            opps.extend(match[5:8])
        elif team in match[5:8]:
            opps.extend(match[1:4])
    return statistics.mean(pointsAllowed(team) for team in opps)


# dummy method used as a placeholder in the functions array, where the corresponding beta value in the dot product is
# supposed to be a constant with no function attached.
def none(team):
    team *= 1
    return 1


functions = [none,
             pointsScored,
             pointsAllowed,
             opp,
             teammate,
             teammateTeammate,
             teammateOpp,
             teammateAllowed,
             oppTeammate,
             oppOpp,
             oppAllowed]


# yourself -->                  (your ability)
# yourself --> teammates -->    (ability of your teammates)
# yourself --> opponents -->    (difficulty of your opponents)
# yourself --> allowed   -->    (your defense ability)
# yourself --> teammates --> teammates --> (your teammates teammates ability)
# yourself --> teammates --> opponents --> (your teammates opponents difficulty)
# yourself --> teammates --> allowed   --> (your teammates defense ability)
# yourself --> opponents --> teammates --> (your opponents teammates ability)
# yourself --> opponents --> opponents --> (your opponents opponents difficulty)
# yourself --> opponents --> allowed   --> (your opponents defense ability)


# winPercentage() simply looks at how many matches a team played and how many they won to calculate their win
# percentage.
def winPercentage(team):
    gamesPlayed = 0
    gamesWon = 0
    team = str(team)
    winner = -2
    for match in allMatches:
        if team in match[1:4]:
            gamesPlayed += 1
            if match[winner] == "Red":
                gamesWon += 1
        elif team in match[5:8]:
            gamesPlayed += 1
            if match[winner] == "Blue":
                gamesWon += 1
    return gamesWon / gamesPlayed


# Simply gets a list of all the teams in the competition. This is later used to rank all the teams.
teams = []
for i in allMatches:
    for x in i[1:4] + i[5:8]:
        if x not in teams:
            teams.append(x)


# Calculates the correlation r value between an input function of a team and win percentage for that team
def corr(function):
    x = np.array([winPercentage(i) for i in teams])  # with every term. r ends up being the
    y = np.array([function(i) for i in teams])  # beta coefficient for each term.
    m, intercept, r, p, std_err = stats.linregress(x, y)  # creates OLS regression
    return r


# Sets the weight of each term to its win rate correlation^7. The reason the correlation is exponentiated is so that
# those terms with low correlation play a negligible role in the equation.
weights = [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
for j in functions:
    if j != none:
        r = corr(j)
        print("Correlation Strength of", str(j)[10:-23], ": ", r)
        weights[functions.index(j)] *= math.pow(r, 7)


# The full equation has 11 terms. 10 of them are the last 10 functions in the functions array, and the last is a
# constant term, hence the none() dummy function in the list of functions. Each of these functions has a weight B,
# so the equation ends up looking something like this:
# (B0) + (pointsScored() * B1) + (pointsAllowed() * B2) + (opp() * B3) + (teammate() * B4) ...
# With a list of the functions
def calculate(team):
    values = [function(team) for function in functions]
    return np.dot(weights, values)


print("Composite Correlation Strength: ", corr(calculate))


# Creates a dictionary with each key being a team and each value being it's corresponding calculated rating
teamsToRatings = {}
for i in teams:
    teamsToRatings[i] = calculate(i)

pp = pprint.PrettyPrinter()

# Lists every team and its corresponding rating
teams.sort(key=lambda team: teamsToRatings[team])
pp.pprint([i + " " + str(round(teamsToRatings[i], 1)) for i in teams])

y = [teamsToRatings[i] for i in teams]
print("Average Score: ", statistics.mean(y))
print("Median Score: ", statistics.median(y))
print("std Score: ", statistics.stdev(y))

