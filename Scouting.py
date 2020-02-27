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
allData = [x['summary_detail']['value'].split("\n") + [x['title']] for x in feedparser.parse(dataSource)['entries']]

for i in allData:  # Formats AllData, getting rid of unnecessary
    for x in range(10):  # Markup syntax
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
    for i in allData:
        if team in i[1:4]:
            teamScores.append(i[0])
        elif team in i[5:8]:
            teamScores.append(i[4])
    return statistics.mean([int(i) for i in teamScores])


def oppPointsScored(team):
    """tells you the average points scored of each opposing alliance that a specified team played against"""
    team = str(team)
    teamScores = []
    for i in allData:
        if team in i[1:4]:
            teamScores.append(i[4])
        elif team in i[5:8]:
            teamScores.append(i[0])
    return statistics.mean([int(i) for i in teamScores])


def teammateAvgScore(team):
    """gives you the average of each of this team's teammates averages."""
    team = str(team)
    teammates = []
    for i in allData:
        if team in i[1:4]:
            x = i[1:4]
            x.remove(team)
            teammates.extend(x)
        if team in i[5:8]:
            x = i[5:8]
            x.remove(team)
            teammates.extend(x)
    return statistics.mean([pointsScored(i) for i in teammates])


def none(team):
    return int(team)


betas = [0, .814521, -.1287542354, 0, .566211975, 0, 0, 0, 0, 0, 0]
functions = [none, pointsScored, oppPointsScored, none, teammateAvgScore, none, none, none, none, none, none]

# Calculates the full score for a team
# using dot product. (Multiplies each
# Beta value with each function output
# and adds them up).
def calculate(team):
    values = [i(team) for i in functions]
    return np.dot(betas, values)


def winPercentage(team):  # Gets the win percentage for a
    gamesPlayed = 0  # particular team. Used as x
    gamesWon = 0  # axis variable in all regressions
    team = str(team)
    for i in allData:
        if team in i[1:4]:
            gamesPlayed += 1
            if i[-2] == "Red":
                gamesWon += 1
        elif team in i[5:8]:
            gamesPlayed += 1
            if i[-2] == "Blue":
                gamesWon += 1
    return gamesWon / gamesPlayed


teams = []  # Gets a list of all the teams,
for i in allData:  # useful for showing calculation
    for x in i[1:4] + i[5:8]:  # results
        if x not in teams:
            teams.append(x)

teams.sort(key=lambda i: calculate(i))  # Shows each team's score
print([int(i) for i in teams])
print([round(calculate(i), 1) for i in teams])

for j in functions:  # Calculates correlation strength (r)
    x = np.array([winPercentage(i) for i in teams])  # with every term. r ends up being the
    y = np.array([j(i) for i in teams])  # beta coefficient for each term.

    slope, intercept, r, p, std_err = stats.linregress(x, y)  # creates OLS regression
    print(r)


def lineFit(b):
    return intercept + slope * b


line1 = lineFit(x)

# plots data on graph with line of best fit
# plt.scatter(x, y)
# plt.plot(x, line1, c='g')
# plt.show()
