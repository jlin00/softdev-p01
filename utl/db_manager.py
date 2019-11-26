#Team Kirkland Meeseeks
#SoftDev pd1
#P01 -- ArRESTed Development
#2019-1?-??

import sqlite3
from utl.db_builder import exec, execmany
from collections import OrderedDict

#====================================================
#formatting functions

#turns tuple into a list
def formatFetch(results):
    collection=[]
    for item in results[0]:
        if str(item) not in collection and len(str(item))>0:
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
        command = "SELECT stat FROM user_tbl WHERE username='jackielin'"
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

#====================================================
#creating leaderboard functions
def orderDict(list):
    list = sorted(list, key=lambda x:x[1])
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

#====================================================
#creating store functions
def purchase(username, value):
    q = "SELECT money FROM user_tbl WHERE username=?"
    inputs = (username,)
    money = execmany(q, inputs).fetchone()[0]
    if (money >= value):
        if (value == 50):
            packR(username)
        #additional code
        q = "UPDATE user_tbl SET money=? WHERE username=?"
        money -= value
        inputs = (money, username)
        execmany(q, inputs)
        return True
    return False

def packR(username):
    q = "SELECT pic FROM pic_tbl ORDER BY random() LIMIT 3;"
    data = exec(q).fetchall()
    for pic in data:
        pic = pic[0]
        coll = getColl(username)
        coll.append(pic)
        coll = ",".join(coll)
        print(coll)
        q = "UPDATE user_tbl SET coll=? WHERE username=?"
        inputs = (coll, username)
        execmany(q, inputs)

def packS():
    #code to return random space pack
    return None

def packM():
    #code to return random pokemon pack
    return None
