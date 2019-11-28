#Team Kirkland Meeseeks
#SoftDev pd1
#P01 -- ArRESTed Development
#2019-1?-??

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

def makeDict(results):
    dictionary={}
    for pair in results:
        if(pair[0]!=None):
            if(pair[1]==None):
                value=0
            else:
                value=pair[1]
            if value not in dictionary.keys():
                list=[pair[0]]
                dictionary[value]=list
            else:
                dictionary[value].append(pair[0])
    for key in dictionary:
        dictionary[key]=sorted(dictionary[key])
    return dictionary

#====================================================
#sign up and login functions

#validates if the user exists in the database
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
        command = "SELECT stat FROM user_tbl WHERE username='jackie'"
        stats = exec(command).fetchone()[0]
        inputs = (username, password, pic, pic, flag, stats)
        execmany(q, inputs)
        return True
    return False #if username already exists

def allCountries():
    q = "SELECT country FROM flags_tbl;"
    data = exec(q).fetchall()
    return formatFetch(data)

#====================================================
#user profile
def changePass(username, password):
    q = "UPDATE user_tbl SET password=? WHERE username=?"
    inputs = (password, username)
    execmany(q, inputs)

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

def updatePic(username, pic):
    q = "UPDATE user_tbl SET pic=? WHERE username=?"
    inputs = (pic, username)
    data = execmany(q, inputs)

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

def getGames(username):
    q = "SELECT game_id from user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0].split(",")
    return data

#====================================================
#creating leaderboard functions
def orderDict(list):
    list = sorted(list, key=lambda x:x[1])
    list = list[::-1]
    dict = OrderedDict()
    for item in list:
        dict[item[0]] = item[1]
    return dict

def userLeaderboard():
    q = "SELECT username, score FROM user_tbl"
    data = exec(q).fetchall()
    return orderDict(data)

def nationLeaderboard():
    q = "SELECT country, SUM(score) FROM user_tbl, flags_tbl WHERE flags_tbl.country = user_tbl.flag GROUP BY flags_tbl.country"
    data = exec(q).fetchall()
    data = orderDict(data)
    return data

def myCountryboard(username):
    q = "SELECT flag FROM user_tbl WHERE username=?"
    inputs = (username,)
    country = execmany(q, inputs).fetchone()[0]
    q = "SELECT username,score FROM user_tbl WHERE flag=?"
    inputs = (country,)
    countryRank = orderDict(execmany(q, inputs).fetchall())
    return countryRank

def findUser(query):
    query = query.lower().strip()
    list = []
    q = "SELECT username FROM user_tbl"
    data = exec(q).fetchall()
    for name in data:
        if (query in name[0]):
            list.append(name[0])
    return list

##### UPDATE TO MAKE GAME ID UNIQUE #####
def findGame(query):
    query = query.lower().strip()
    list = []
    q = "SELECT game_id FROM game_tbl"
    data = exec(q).fetchall()
    for game in data:
        if (query in game[0] and "S" not in game[0]):
            list.append(game[0])
    return list

#====================================================
#creating store functions
def purchase(username, value):
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
        #additional code
        q = "UPDATE user_tbl SET money=? WHERE username=?"
        money -= value
        inputs = (money, username)
        execmany(q, inputs)
        return True
    return False

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

def pfp(username,link):
    q = "UPDATE user_tbl SET pic=? WHERE username=?"
    inputs=(link, username)
    execmany(q,inputs)

def getpfp(pic_id):
    q = "SELECT pic FROM pic_tbl WHERE category=?"
    inputs = (pic_id, )
    data = execmany(q, inputs).fetchone()
    if (data is None):
        q = "SELECT flag FROM flags_tbl WHERE country=?"
        inputs = (pic_id, )
        data = execmany(q, inputs).fetchone()
    return data[0]
#====================================================
#playing trivia game functions

#get all single player games
def getSingle(username):
    q = "SELECT game_id FROM user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0]
    data = data.split(",")
    list = []
    for i in range(len(data)):
        if "S" in data[i]:
            list.append(data[i])
    return list

def getPVP(username):
    q = "SELECT game_id FROM user_tbl WHERE username=?"
    inputs = (username, )
    data = execmany(q, inputs).fetchone()[0]
    data = data.split(",")
    list = []
    for i in range(len(data)):
        if "P" in data[i]:
            list.append(data[i])
    return list

def getTeam(username):
        q = "SELECT game_id FROM user_tbl WHERE username=?"
        inputs = (username, )
        data = execmany(q, inputs).fetchone()[0]
        data = data.split(",")
        list = []
        for i in range(len(data)):
            if "T" in data[i]:
                list.append(data[i])
        return list

def addSingle(username):
    #generate random game id
    game_id = "S" + str(random.randrange(10000))
    command = "SELECT game_id FROM game_tbl WHERE game_id=?"
    inputs = (game_id, )
    data = execmany(command, inputs).fetchall()
    while game_id in data:
        game_id = "S" + str(random.randrange(10000))

    #add game to game table
    command = "INSERT INTO game_tbl VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)"
    inputs = (str(game_id), username, '0,0,'+username, '', username, 1, 0, '', '')
    execmany(command, inputs)

    #add game to user table
    command = 'SELECT game_id FROM user_tbl WHERE username=?'
    inputs = (username, )
    games = execmany(command, inputs).fetchone()[0]
    command = 'UPDATE user_tbl SET game_id=? WHERE username=?'
    games += "," + game_id
    inputs = (games, username)
    execmany(command, inputs)

def gameStarted(game_id):
    q = "SELECT started FROM game_tbl WHERE game_id=?"
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()[0]
    return (data == 1)

def gameCompleted(game_id):
    q = "SELECT completed FROM game_tbl WHERE game_id=?"
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()[0]
    return (data == 1)

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

def updateQuestion(username, game_id):
    #determine team number
    team = getTeamNum(username, game_id)
    q = "SELECT team%s FROM game_tbl WHERE game_id=?" % team
    r = "UPDATE game_tbl SET currentq%s=?" % team
    s = "UPDATE game_tbl SET team%s=?" % team

    #update question number that team is up to
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()[0].split(",")
    number = int(data[1]) + 1 #increment by 1
    if (number > 10):
        completeGame(game_id)
        return
    data[1] = str(number)
    data = ",".join(data)
    inputs = (data, )
    execmany(s, inputs)

    #update current question for that team
    command = "SELECT * FROM question_tbl ORDER BY random() LIMIT 1"
    question = exec(command).fetchone()[1]
    inputs = (question, )
    execmany(r, inputs)

def completeGame(game_id):
    q = "UPDATE game_tbl SET completed=? WHERE game_id=?"
    inputs = (1, game_id)
    execmany(q, inputs)

def currentNumber(username, game_id):
    team = getTeamNum(username, game_id)
    q = "SELECT team%s FROM game_tbl WHERE game_id=?" % team
    inputs = (game_id, )
    data = execmany(q, inputs).fetchone()[0].split(",")
    number = int(data[1])
    return number
