#Team Kirkland Meeseeks
#SoftDev pd1
#P01 -- ArRESTed Development
#2019-12-04

import sqlite3
from utl.db_builder import exec, execmany
from collections import OrderedDict
import random

#====================================================
#formatting functions

#turns tuple into a list
def formatFetch(results):
    collection=[]
    for item in results:
         if str(item) not in collection:
            collection.append(str(item)[2:-3])
    return collection

#====================================================
#sign up and login functions

#authenticates user
def userValid(username,password):
    q = "SELECT username FROM user_tbl;"
    data = exec(q)
    for uName in data:
        if uName[0] == username:
            q = "SELECT password from user_tbl WHERE username=?"
            inputs = (username,)
            data = execmany(q, inputs)
            for passW in data:
                if (passW[0] == password):
                    return True
    return False

#add user-provided credentials to database
def addUser(username, password, flag):
    q = "SELECT * FROM user_tbl WHERE username=?"
    inputs = (username,)
    data = execmany(q, inputs).fetchone()
    if (data is None):
        q = "INSERT INTO user_tbl VALUES(?, ?, ?, ?, '', 200, ?, ?, 0)"
        command = "SELECT flag from flags_tbl where country=?"
        inputs = (flag, )
        pic = execmany(command, inputs).fetchone()[0]
        command = "SELECT stat FROM user_tbl WHERE username='admin'"
        stats = exec(command).fetchone()[0]
        inputs = (username, password, pic, pic, flag, stats)
        execmany(q, inputs)
        return True
    return False #if username already exists

#reset password
def changePass(username, password):
    q = "UPDATE user_tbl SET password=? WHERE username=?"
    inputs = (password, username)
    execmany(q, inputs)

#displays all options for country on sign-up page
def allCountries():
    q = "SELECT country FROM flags_tbl;"
    data = exec(q).fetchall()
    return formatFetch(data)

#====================================================
#user information

def getStats(username):
    q = "SELECT stat from user_tbl WHERE username=?"
    inputs = (username,)
    data = execmany(q, inputs).fetchone()[0]
    stats = {}
    if (data is not None):
        data = data.split(",")
        for category in data:
            category = category.split("|")
            stats[category[0]] = (category[1], category[2])
    return stats

def getCountry(username):
    q = "SELECT flag from user_tbl WHERE username=?"
    inputs = (username,)
    data = execmany(q, inputs).fetchone()[0]
    return data

def getPic(username):
    q = "SELECT pic from user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0]
    return data

def getScore(username):
    q = "SELECT score from user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0]
    return data

def getMoney(username):
    q = "SELECT money from user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0]
    return data

def getColl(username):
     q = "SELECT coll from user_tbl WHERE username=?"
     inputs = (username, )
     data = execmany(q, inputs).fetchone()[0].split(",")
     return data

#get IDs of all the pictures in user's collections
def getCollID(username):
    coll = getColl(username)
    list = []
    for i in range(len(coll)):
        pic = coll[i]
        q = "SELECT country from flags_tbl WHERE flag=?"
        inputs = (pic, )
        data = execmany(q, inputs).fetchone()
        if (data is None):
            q = "SELECT category from pic_tbl WHERE pic=?"
            data = execmany(q, inputs).fetchone()[0]
        else:
            data = data[0]
        list.append(data)
    return list

def getGames(username, owner):
    q = "SELECT game_id from user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0].split(",")
    output = []
    if len(data) > 0:
        data.pop(0)
    for i in range(len(data)):
        entry = []
        game_id = data[i]

        #first item in tuple
        if "S" in game_id:
            entry.append("Single Player")
        elif "P" in game_id:
            entry.append("PVP")
        else:
            entry.append("Team")

        #second item in tuple
        entry.append(game_id)

        #third, fourth, fifth item in tuple
        if gameCompleted(game_id):
            entry.append("View")
            entry.append("")
            entry.append("btn-secondary")
        else:
            if ownGame(owner, game_id):
                entry.append("Play")
                entry.append("")
                entry.append("btn-primary")
            else:
                if gameFull(game_id):
                    entry.append("Full")
                    entry.append("disabled")
                    entry.append("btn-danger")
                else:
                    entry.append("Join")
                    entry.append("")
                    entry.append("btn-success")
        output.append(tuple(entry))
    return output

#====================================================
#leaderboard

#create an orderedDict given a list of values
def orderDict(list):
    list = sorted(list, key=lambda x:x[1])
    list = list[::-1]
    dict = OrderedDict()
    for item in list:
        dict[item[0]] = item[1]
    return dict

#top users
def userLeaderboard():
    q = "SELECT username, score FROM user_tbl"
    data = exec(q).fetchall()
    return orderDict(data)

#top nations
def nationLeaderboard():
    q = "SELECT country, SUM(score) FROM user_tbl, flags_tbl WHERE flags_tbl.country = user_tbl.flag GROUP BY flags_tbl.country"
    data = exec(q).fetchall()
    data = orderDict(data)
    return data

#top users in country
def myCountryboard(username):
    q = "SELECT flag FROM user_tbl WHERE username=?"
    inputs = (username,)
    country = execmany(q, inputs).fetchone()[0]
    q = "SELECT username,score FROM user_tbl WHERE flag=?"
    inputs = (country,)
    countryRank = orderDict(execmany(q, inputs).fetchall())
    return countryRank

#====================================================
#store

#buy a picture pack, each pack has unique price (value)
def purchase(username, value):
    if (value != 50 and value != 75 and value != 100):
        return False
    q = "SELECT money FROM user_tbl WHERE username=?"
    inputs = (username,)
    money = execmany(q, inputs).fetchone()[0]
    if (money >= value):
        if (value == 50):
            packR(username)
        if (value == 75):
            packP(username)
        if (value == 100):
            packM(username)
        #deduct from user's money
        q = "UPDATE user_tbl SET money=? WHERE username=?"
        money -= value
        inputs = (money, username)
        execmany(q, inputs)
        return True
    return False

#Rick and Morty pack
def packR(username):
    q = "SELECT pic FROM pic_tbl WHERE category LIKE 'R%' ORDER BY random() LIMIT 3"
    data = exec(q).fetchall()
    for pic in data:
        pic = pic[0]
        coll = getColl(username)
        coll.append(pic)
        coll = ",".join(coll)
        q = "UPDATE user_tbl SET coll=? WHERE username=?"
        inputs = (coll, username)
        execmany(q, inputs)

#Pokemon pack
def packP(username):
    q = "SELECT pic FROM pic_tbl WHERE category LIKE 'P%' ORDER BY random() LIMIT 3"
    data = exec(q).fetchall()
    for pic in data:
        pic = pic[0]
        coll = getColl(username)
        coll.append(pic)
        coll = ",".join(coll)
        q = "UPDATE user_tbl SET coll=? WHERE username=?"
        inputs = (coll, username)
        execmany(q, inputs)

#mystery pack
def packM(username):
    q = "SELECT pic FROM pic_tbl WHERE category LIKE 'M%' ORDER BY random() LIMIT 3 "
    data = exec(q).fetchall()
    for pic in data:
        pic = pic[0]
        coll = getColl(username)
        coll.append(pic)
        coll = ",".join(coll)
        q = "UPDATE user_tbl SET coll=? WHERE username=?"
        inputs = (coll, username)
        execmany(q, inputs)

#given pic_id, fetch image source from pic_tbl
def getpfp(pic_id):
    q = "SELECT pic FROM pic_tbl WHERE category=?"
    inputs = (pic_id, )
    data = execmany(q, inputs).fetchone()
    if (data is None):
        q = "SELECT flag FROM flags_tbl WHERE country=?"
        inputs = (pic_id, )
        data = execmany(q, inputs).fetchone()
    return data[0]

#checks to see if user owns picture
def ownsPic(username, pic_id):
    list = getCollID(username)
    for item in list:
        if item == pic_id:
            return True
    return False

def updatePic(username, pic_id):
    isOwner = ownsPic(username, pic_id)
    if isOwner:
        pic = getpfp(pic_id)
        q = "UPDATE user_tbl SET pic=? WHERE username=?"
        inputs = (pic, username)
        data = execmany(q, inputs)

#====================================================
#playing trivia game functions
def ownGame(username, game_id):
    q = "SELECT game_id FROM user_tbl WHERE username=?"
    inputs = (username,)
    data = execmany(q, inputs).fetchone()[0]
    return (game_id in data)

#get all single player games
def getSingle(username):
    q = "SELECT game_id FROM user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0]
    data = data.split(",")
    list = []
    for i in range(len(data)):
        if "S" in data[i]:
            if (not gameCompleted(data[i])):
                list.append(data[i])
    return list

#get all PVP games
def getPVP(username):
    q = "SELECT game_id FROM user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0]
    data = data.split(",")
    list = []
    for i in range(len(data)):
        if "P" in data[i]:
            if (not gameCompleted(data[i])):
                list.append(data[i])
    return list

#get all team games
def getTeam(username):
        q = "SELECT game_id FROM user_tbl WHERE username=?"
        inputs = (username, )
        data = execmany(q, inputs).fetchone()[0]
        data = data.split(",")
        list = []
        for i in range(len(data)):
            if "T" in data[i]:
                if (not gameCompleted(data[i])):
                    list.append(data[i])
        return list

#create a single player game
def addSingle(username):
    #generate random game id
    game_id = "S" + str(random.randrange(10000000000))
    command = "SELECT game_id FROM game_tbl"
    data = exec(command).fetchall()
    list = []
    for entry in data:
        list.append(entry[0])
    if len(list) >= 10000000000:
        return False
    while game_id in list:
        game_id = "S" + str(random.randrange(10000000000))

    #add game to game table
    command = "INSERT INTO game_tbl VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    inputs = (str(game_id), username, '0,0,'+username, '', username, '', 1, 0, 1, '', '')
    execmany(command, inputs)

    #add game to user table
    command = 'SELECT game_id FROM user_tbl WHERE username=?'
    inputs = (username, )
    games = execmany(command, inputs).fetchone()[0]
    command = 'UPDATE user_tbl SET game_id=? WHERE username=?'
    games += "," + game_id
    inputs = (games, username)
    execmany(command, inputs)
    return True

#create a pvp game
def addMulti(username, type):
    #generate random game id
    game_id = type + str(random.randrange(10000000000))
    command = "SELECT game_id FROM game_tbl"
    data = exec(command).fetchall()
    list = []
    for entry in data:
        list.append(entry[0])
    if len(list) >= 10000000000:
        return False
    while game_id in list:
        game_id = type + str(random.randrange(10000000000))

    #add game to game table
    command = "INSERT INTO game_tbl VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
    inputs = (str(game_id), username, '0,0,'+username, '', username, '', 0, 0, 0, '', '')
    execmany(command, inputs)

    #add game to user table
    command = 'SELECT game_id FROM user_tbl WHERE username=?'
    inputs = (username, )
    games = execmany(command, inputs).fetchone()[0]
    command = 'UPDATE user_tbl SET game_id=? WHERE username=?'
    games += "," + game_id
    inputs = (games, username)
    execmany(command, inputs)
    return True

def joinGame(username, game_id):
    owner = ownGame(username, game_id)
    if not owner and not gameFull(game_id):
        #joining a PVP game
        if "P" in game_id:
            #update game table
            q = "SELECT participants FROM game_tbl WHERE game_id=?"
            inputs = (game_id, )
            participants = execmany(q, inputs).fetchone()[0]
            q = "UPDATE game_tbl SET participants=?, team2=?, playing2=?, started=? WHERE game_id=?"
            participants += "," + username
            team2 = '0,0,' + username
            playing2 = username
            started = 1
            inputs = (participants, team2, playing2, started, game_id)
            execmany(q, inputs)

            #update user table
            q = "SELECT game_id FROM user_tbl WHERE username=?"
            inputs = (username, )
            games = execmany(q, inputs).fetchone()[0]
            q = "UPDATE user_tbl SET game_id=? WHERE username=?"
            games += "," + game_id
            inputs = (games, username)
            execmany(q, inputs)
        #joining a team game

def joinPVP(username, type):
    q = "SELECT game_id FROM game_tbl WHERE game_id LIKE 'P%' AND team2='' AND playing1!=?"
    inputs = (username, )
    game_id = execmany(q, inputs).fetchone()
    if (game_id is None):
        return addMulti(username, type)
    else:
        game_id = game_id[0]
        joinGame(username, game_id)
    return True

#check if game started
def gameStarted(game_id):
    q = "SELECT started FROM game_tbl WHERE game_id=?"
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()[0]
    return (data == 1)

#check if game completed
def gameCompleted(game_id):
    q = "SELECT completed1, completed2 FROM game_tbl WHERE game_id=?"
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()
    return (data[0] == 1 and data[1] == 1)

#only team1 is completed
def team1Completed(game_id):
    q = "SELECT completed1, completed2 FROM game_tbl WHERE game_id=?"
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()
    return (data[0] == 1 and data[1] == 0)

#only team2 is completed
def team2Completed(game_id):
    q = "SELECT completed2, completed1 FROM game_tbl WHERE game_id=?"
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()
    return (data[0] == 1 and data[1] == 0)

#check if game is full
def gameFull(game_id):
    if "S" in game_id:
        return False
    if "P" in game_id:
        q = "SELECT team2 FROM game_tbl WHERE game_id=?"
        inputs = (game_id, )
        data = execmany(q, inputs).fetchone()[0]
        if data == "":
            return False
    else:
        q = "SELECT team1, team2 FROM game_tbl WHERE game_id=?"
        inputs = (game_id, )
        data = execmany(q, inputs).fetchone()[0]
    return True

#check which team user is on for a particular game
def getTeamNum(username, game_id):
    q = "SELECT team1 FROM game_tbl WHERE game_id=?"
    r = "SELECT team2 FROM game_tbl WHERE game_id=?"
    inputs = (game_id, )
    team1 = execmany(q, inputs).fetchone()[0].split(",")
    team2 = execmany(r, inputs).fetchone()[0].split(",")
    for i in range(len(team1) - 2):
        i = i + 2
        if team1[i] == username:
            return "1";
    return "2";

#get which number question the team is currently up to
def currentNumber(username, game_id):
    team = getTeamNum(username, game_id)
    q = "SELECT team%s FROM game_tbl WHERE game_id=?" % team
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()[0].split(",")
    number = int(data[1])
    return number

#get which question a team is up to
def getCurrentQuestion(username, game_id):
    team = getTeamNum(username, game_id)
    q = "SELECT currentq%s FROM game_tbl WHERE game_id=?" % team
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()[0]
    if (data != ""):
        q = "SELECT * FROM question_tbl WHERE question=?"
        inputs = (data, )
        output = execmany(q, inputs).fetchone()
        return output
    return None

#generate next question for team
def updateQuestion(username, game_id):
    #determine team number
    team = getTeamNum(username, game_id)
    q = "SELECT team%s FROM game_tbl WHERE game_id=?" % team
    r = "UPDATE game_tbl SET currentq%s=? WHERE game_id=?" % team
    s = "UPDATE game_tbl SET team%s=? WHERE game_id=?" % team

    #update question number that team is up to
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()[0].split(",")
    number = int(data[1]) + 1
    if number > 10:
        completeGame(username, game_id)
        return
    data[1] = str(number)
    data = ",".join(data)
    inputs = (data, game_id)
    execmany(s, inputs)

    #update current question for that team
    command = "SELECT * FROM question_tbl ORDER BY random() LIMIT 1"
    question = exec(command).fetchone()[1]
    inputs = (question, game_id)
    execmany(r, inputs)

def completeGame(username, game_id):
    team = getTeamNum(username, game_id)
    q = "UPDATE game_tbl SET completed%s=? WHERE game_id=?" % team
    inputs = (1, game_id)
    execmany(q, inputs)

#====================================================
#search

#find by username
def findUser(query):
    query = query.lower().strip()
    list = []
    q = "SELECT username FROM user_tbl"
    data = exec(q).fetchall()
    for name in data:
        if (query in name[0]):
            list.append(name[0])
    return list

#find by game_id
def findGame(query):
    query = query.lower().strip()
    list = []
    q = "SELECT game_id FROM game_tbl"
    data = exec(q).fetchall()
    for game in data:
        if (query in game[0] and "S" not in game[0]):
            list.append(game[0])
    return list
