import feedparser
# import pprint
import statistics
import numpy as np
from sklearn.metrics import r2_score
import matplotlib.pyplot as plt
from scipy import stats

# pp = pprint.PrettyPrinter(indent=3)

dataSource = "feed.xml"
# Extracts the valuable data from the RSS Feed
allMatches = [x['summary_detail']['value'].split("\n") + [x['title']] for x in feedparser.parse(dataSource)['entries']]

for i in allMatches:  # Formats AllData, getting rid of unnecessary markup syntax
    for x in range(10):
        if str(x) in "01235678":
            i[x] = ''.join(c for c in i[x] if c.isdigit())
            if x % 5 == 0:
                i[x] = i[x][1:-1]
    i.pop(4)
    i.insert(8, ["Red", "Blue"][int(i[0]) < int(i[4])])


def pointsScored(team):
    """tells you the average points scored of each alliance that a specified team was part of"""
    team = str(team)
    teamScores = []
    for match in allMatches:
        if team in match[1:4]:
            teamScores.append(match[0])
        elif team in match[5:8]:
            teamScores.append(match[4])
    return statistics.mean([int(score) for score in teamScores])


def pointsAllowed(team):
    """tells you the average points scored of each opposing alliance that a specified team played against"""
    team = str(team)
    teamScores = []
    for match in allMatches:
        if team in match[1:4]:
            teamScores.append(match[4])
        elif team in match[5:8]:
            teamScores.append(match[0])
    return statistics.mean([int(score) for score in teamScores])


def opp(team):
    team = str(team)
    opps = []
    for match in allMatches:
        if team in match[1:4]:
            opps.extend(match[5:8])
        elif team in match[5:8]:
            opps.extend(match[1:4])
    return statistics.mean(pointsScored(team) for team in opps)


def teammate(team):
    """gives you the average of each of this team's teammates averages."""
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


def teammateAllowed(team):
    """gives you the average of each of this team's teammates averages."""
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


def oppTeammate(team):
    team = str(team)
    opps = []
    for match in allMatches:
        if team in match[1:4]:
            opps.extend(match[5:8])
        elif team in match[5:8]:
            opps.extend(match[1:4])
    return statistics.mean(teammate(team) for team in opps)


def oppOpp(team):
    team = str(team)
    opps = []
    for match in allMatches:
        if team in match[1:4]:
            opps.extend(match[5:8])
        elif team in match[5:8]:
            opps.extend(match[1:4])
    return statistics.mean(opp(team) for team in opps)


def oppAllowed(team):
    team = str(team)
    opps = []
    for match in allMatches:
        if team in match[1:4]:
            opps.extend(match[5:8])
        elif team in match[5:8]:
            opps.extend(match[1:4])
    return statistics.mean(pointsAllowed(team) for team in opps)


def none(team):
    return int(team)


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


# yourself -->                  (your offense capability)
# yourself --> teammates -->    (ability of teammates)
# yourself --> opponents -->    (difficulty of opponents)
# yourself --> allowed   -->    (your defense capability)
# yourself --> teammates --> teammates -->
# yourself --> teammates --> opponents -->
# yourself --> teammates --> allowed   -->
# yourself --> opponents --> teammates -->
# yourself --> opponents --> opponents -->
# yourself --> opponents --> allowed   -->


# Calculates the full score for a team
# using dot product. (Multiplies each
# Beta value with each function output
# and adds them up).
def calculate(team):
    values = [function(team) for function in functions]
    return np.dot(betas, values)


def winPercentage(team):  # Gets the win percentage for a particular team
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


teams = []  # Gets a list of all the teams,
for i in allMatches:  # useful for showing calculation
    for x in i[1:4] + i[5:8]:  # results
        if x not in teams:
            teams.append(x)

# teams.sort(key=lambda i: calculate(i))  # Shows each team's score
# print([int(i) for i in teams])
# print([round(calculate(i), 1) for i in teams])


def lineFit(b):
    return intercept + slope * b


betas = [0]
for j in functions:  # Calculates correlation strength (r)
    if j != none:
        x = np.array([winPercentage(i) for i in teams])  # with every term. r ends up being the
        y = np.array([j(i) for i in teams])  # beta coefficient for each term.

        slope, intercept, r, p, std_err = stats.linregress(x, y)  # creates OLS regression
        # plt.scatter(x, y)
        # line1 = lineFit(x)
        # plt.plot(x, line1, c='g')
        # plt.show()
        print("Correlation Strength of", str(j)[10:-23], ": ", r)
        betas.append(r)


teamsToRatings = {}
for i in teams:
    teamsToRatings[i] = calculate(i)

x = np.array([winPercentage(team) for team in teams])
y = np.array([teamsToRatings[i] for i in teams])

slope, intercept, r, p, std_err = stats.linregress(x, y)  # creates OLS regression
print("Composite Correlation Strength: ", r)
betas.append(r)

teams.sort(key=lambda team: teamsToRatings[team])
print([int(i) for i in teams])
print([round(teamsToRatings[i], 1) for i in teams])
