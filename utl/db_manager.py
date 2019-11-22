#Team Kirkland Meeseeks
#SoftDev pd1
#P01 -- ArRESTed Development
#2019-1?-??

import sqlite3
from utl.db_builder import exec, execmany

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
        q = "INSERT INTO user_tbl VALUES(?, ?, '', '', '', 200, ?, '', 300)"
        inputs = (username, password, flag)
        execmany(q, inputs)
        #q = "INSERT INTO user_tbl VALUES('%s', '%s', '', '', '', 200, \"%s\", '', 0);" % (username, password, flag)
        #exec(q)
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


#====================================================
#creating leaderboard functions

def userLeaderboard():
    q = "SELECT username, score FROM user_tbl"
    data = exec(q).fetchall()
    return makeDict(data)

def nationLeaderboard():
    q = "SELECT country, SUM(score) FROM user_tbl, flags_tbl WHERE flags_tbl.country = user_tbl.flag GROUP BY flags_tbl.country"
    data = exec(q).fetchall()
    data = makeDict(data)
    #print(data)
    return data

def myCountryboard(username):
    q = "SELECT flag FROM user_tbl WHERE username=?"
    inputs = (username,)
    country = execmany(q, inputs).fetchone()[0]
    q = "SELECT username,score FROM user_tbl WHERE flag=?"
    inputs = (country,)
    countryRank = makeDict(execmany(q, inputs).fetchall())
    return countryRank
#====================================================
#creating store functions
def moneyExchange(username):
    q = "SELECT money FROM user_tbl WHERE username=?"
    inputs = (username,)
    money=execmany(q,inputs)
    
